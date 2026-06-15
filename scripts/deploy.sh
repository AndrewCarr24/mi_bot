#!/usr/bin/env bash
# Build, push, and deploy agent_fin to AWS.
#
# Steps:
#   1. Preflight: env, AWS auth, git state.
#   2. Bootstrap ECR if it doesn't exist.
#   3. Build + tag + push container to ECR.
#   4. Apply CDK changes (App Runner stack).
#   5. Trigger explicit redeploy (so App Runner pulls the new image even
#      when no infra changed).
#   6. Wait + report URL.
#
# Usage:  ./scripts/deploy.sh

set -euo pipefail

# ---- 0. Locate ourselves; ensure cwd is agent_fin/.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

REGION="${AWS_REGION:-us-east-1}"
SERVICE_NAME="agent-fin"
STACK_ECR="AgentFinEcrStack"
STACK_RUNNER="AgentFinRunnerStack"

log() { echo "[deploy] $*"; }

# ---- 1. Preflight.
log "preflight: checking env vars"
for var in AGENT_PASSWORD COOKIE_SECRET DEEPSEEK_API_KEY; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is unset. Run: set -a && . .env && set +a" >&2
    exit 1
  fi
done

# LangSmith tracing is how prod usage is observed (full Q&A + latency +
# tool calls land in the `agent-fin` project). The vars are baked into the
# container at deploy time from the local env, so if they're unset here
# they silently won't reach prod. Warn loudly before we push.
if [[ "${LANGSMITH_TRACING:-}" != "true" || -z "${LANGSMITH_API_KEY:-}" ]]; then
  echo "[deploy] ----------------------------------------------------------" >&2
  echo "[deploy] WARNING: LangSmith tracing is NOT fully configured:" >&2
  echo "[deploy]   LANGSMITH_TRACING=${LANGSMITH_TRACING:-<unset>}" >&2
  echo "[deploy]   LANGSMITH_API_KEY=$([[ -n "${LANGSMITH_API_KEY:-}" ]] && echo '<set>' || echo '<unset>')" >&2
  echo "[deploy]   LANGSMITH_PROJECT=${LANGSMITH_PROJECT:-<unset>}" >&2
  echo "[deploy] Prod runs will NOT be traced — you lose usage analytics." >&2
  echo "[deploy] Fix: run  set -a && . .env && set +a  before deploying." >&2
  echo "[deploy] ----------------------------------------------------------" >&2
  if [[ -t 0 ]]; then
    read -r -p "[deploy] Continue without LangSmith tracing? [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]] || { echo "[deploy] aborted." >&2; exit 1; }
  else
    echo "[deploy] (non-interactive; continuing in 5s — Ctrl-C to abort)" >&2
    sleep 5
  fi
else
  log "preflight: LangSmith tracing OK (project=${LANGSMITH_PROJECT:-agent-fin})"
fi

log "preflight: checking AWS auth"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"

log "preflight: checking git state"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "[deploy] WARNING: uncommitted changes in working tree."
fi

IMAGE_TAG="$(git rev-parse --short HEAD)"
log "deploying tag=$IMAGE_TAG (account=$ACCOUNT_ID, region=$REGION)"

# ---- 2. Bootstrap ECR if needed.
log "bootstrap: checking ECR repo $SERVICE_NAME"
if ! aws ecr describe-repositories --repository-names "$SERVICE_NAME" --region "$REGION" >/dev/null 2>&1; then
  log "bootstrap: deploying $STACK_ECR"
  ( cd infra/cdk && cdk deploy "$STACK_ECR" --require-approval never )
fi

ECR_URI="$(aws ecr describe-repositories --repository-names "$SERVICE_NAME" \
            --region "$REGION" --query 'repositories[0].repositoryUri' --output text)"
log "ECR URI: $ECR_URI"

# ---- 3. Build + tag + push.
log "build: docker build (linux/amd64)"
docker build --platform=linux/amd64 \
  -t "$SERVICE_NAME:$IMAGE_TAG" \
  -t "$SERVICE_NAME:latest" \
  .

log "push: ECR login"
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$ECR_URI"

log "push: tagging + pushing $IMAGE_TAG and latest"
docker tag "$SERVICE_NAME:$IMAGE_TAG" "$ECR_URI:$IMAGE_TAG"
docker tag "$SERVICE_NAME:latest"     "$ECR_URI:latest"
docker push "$ECR_URI:$IMAGE_TAG"
docker push "$ECR_URI:latest"

# ---- 4. Redeploy the existing service to the new image, env-safe.
#
# NOTE: the live `agent-fin` service is NOT CloudFormation-managed (there is
# no AgentFin* stack), so `cdk deploy AgentFinRunnerStack` would try to
# create a *duplicate* service and fail. Instead, _update_service.py resumes
# the service if paused, swaps only the image tag, preserves the baked-in
# env vars, and merges in LANGSMITH_* from the local env. If you ever need to
# change infra (DynamoDB table, IAM, sizing), that's a separate CDK migration
# — see infra/cdk/runner_stack.py and the note in CLAUDE.md.
log "redeploy: update-service to $IMAGE_TAG (env-preserving)"
./.venv/bin/python scripts/_update_service.py \
  --service "$SERVICE_NAME" --tag "$IMAGE_TAG" --region "$REGION"
