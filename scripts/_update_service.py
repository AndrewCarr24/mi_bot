#!/usr/bin/env python3
"""Resume (if paused) + redeploy an existing App Runner service to a new
image tag, PRESERVING its live runtime env vars and merging in any
LANGSMITH_* vars present in the local environment.

Why this exists instead of `cdk deploy`: the live `agent-fin` service was
created manually — no CloudFormation stack owns it (verified: there is no
`AgentFin*` stack). `cdk deploy AgentFinRunnerStack` would therefore try to
*create a second* service named `agent-fin` and fail. And a naive
`aws apprunner update-service` with a partial ImageConfiguration would WIPE
the baked-in env vars (password, API keys, model IDs). This helper does the
minimal, env-safe thing: read the live SourceConfiguration, swap only the
image tag, add LangSmith tracing vars, and push it back.

It intentionally does NOT set DATA_LAYER_BACKEND=dynamodb: there is no
DynamoDB table or instance-role policy yet, so enabling it would make every
message error. Durable thread persistence is a separate follow-up; LangSmith
already captures full Q&A for usage analytics.

Usage:
    python scripts/_update_service.py --service agent-fin --tag <gitsha> [--region us-east-1]
"""
from __future__ import annotations

import argparse
import copy
import os
import sys
import time

import boto3

# Optional tracing vars: merged in from the local env if present so the
# redeployed service starts emitting LangSmith traces (the live service
# currently has none — the last manual deploy dropped them).
LANGSMITH_VARS = ("LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_TRACING")


def _strip_none(obj):
    """Drop None-valued keys (describe-service returns ConnectionArn=None,
    empty RuntimeEnvironmentSecrets, etc.; update-service rejects some)."""
    if isinstance(obj, dict):
        return {k: _strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_none(v) for v in obj]
    return obj


def _wait(client, arn: str, target: str = "RUNNING", timeout: int = 600) -> None:
    deadline = time.time() + timeout
    last = None
    while True:
        status = client.describe_service(ServiceArn=arn)["Service"]["Status"]
        if status != last:
            print(f"[update_service] status={status}")
            last = status
        if status == target:
            return
        if status in ("CREATE_FAILED", "DELETE_FAILED"):
            sys.exit(f"[update_service] service entered failed state: {status}")
        if time.time() > deadline:
            sys.exit(f"[update_service] timeout waiting for {target} (last={status})")
        time.sleep(10)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--service", required=True)
    ap.add_argument("--tag", required=True, help="ECR image tag to deploy (e.g. git short sha)")
    ap.add_argument("--region", default=os.environ.get("AWS_REGION", "us-east-1"))
    args = ap.parse_args()

    client = boto3.client("apprunner", region_name=args.region)

    summary = next(
        (s for s in client.list_services()["ServiceSummaryList"]
         if s["ServiceName"] == args.service),
        None,
    )
    if summary is None:
        sys.exit(f"[update_service] service {args.service!r} not found in {args.region}")
    arn = summary["ServiceArn"]

    desc = client.describe_service(ServiceArn=arn)["Service"]
    src = _strip_none(copy.deepcopy(desc["SourceConfiguration"]))
    img = src["ImageRepository"]

    repo_uri = img["ImageIdentifier"].rsplit(":", 1)[0]
    new_ident = f"{repo_uri}:{args.tag}"

    img_cfg = img.setdefault("ImageConfiguration", {})
    env = img_cfg.get("RuntimeEnvironmentVariables", {})
    before = set(env)
    for key in LANGSMITH_VARS:
        val = os.environ.get(key)
        if val:
            env[key] = val
    added = sorted(set(env) - before)

    img["ImageIdentifier"] = new_ident
    img_cfg["RuntimeEnvironmentVariables"] = env

    # Resume first — update-service is rejected on a PAUSED service.
    if desc["Status"] == "PAUSED":
        print("[update_service] service is PAUSED — resuming before update")
        client.resume_service(ServiceArn=arn)
        _wait(client, arn, "RUNNING")

    print(f"[update_service] image -> {new_ident}")
    print(f"[update_service] env vars: {len(env)} total; added: {added or 'none'}")
    client.update_service(ServiceArn=arn, SourceConfiguration=src)
    _wait(client, arn, "RUNNING")

    final = client.describe_service(ServiceArn=arn)["Service"]
    print(f"[update_service] deployed https://{final['ServiceUrl']}  (tag={args.tag})")


if __name__ == "__main__":
    main()
