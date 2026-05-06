# infra/cdk

CDK-Python infrastructure for `agent_fin`. Two stacks:

- **`AgentFinEcrStack`** — ECR repository (image scanning, lifecycle policy retaining last 10 images).
- **`AgentFinRunnerStack`** — App Runner service + IAM access role + IAM instance role + env-var configuration. Depends on `AgentFinEcrStack`.

The image lifecycle (build, push, redeploy trigger) lives in [`scripts/deploy.sh`](../../scripts/deploy.sh), not in CDK.

## Prerequisites

- Node.js 18+ and AWS CDK CLI: `npm install -g aws-cdk`
- AWS CLI configured (`aws sts get-caller-identity` succeeds)
- Python deps: `pip install -r requirements.txt` (run from `infra/cdk/`)
- One-time per account/region: `cdk bootstrap`

## Deploy

The two stacks are normally deployed via `scripts/deploy.sh` (which deploys ECR if missing, pushes the image, then deploys the runner stack). To deploy a stack manually:

```bash
set -a && . ../../.env && set +a
export AGENT_PASSWORD=...
export COOKIE_SECRET=$(openssl rand -hex 32)
cdk deploy AgentFinEcrStack
cdk deploy AgentFinRunnerStack
```

## Destroy

```bash
cdk destroy AgentFinRunnerStack
cdk destroy AgentFinEcrStack
```

ECR refuses to delete a non-empty repo. To force-empty first:

```bash
aws ecr batch-delete-image --repository-name agent-fin \
  --image-ids "$(aws ecr list-images --repository-name agent-fin --query 'imageIds[*]' --output json)"
```

## Outputs

- `AgentFinEcrStack.EcrRepoUri` — ECR push target.
- `AgentFinRunnerStack.ServiceUrl` — public app URL.
- `AgentFinRunnerStack.ServiceArn` — used by `deploy.sh` for `start-deployment`.
