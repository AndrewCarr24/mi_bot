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

# ---- 4. Apply infra changes.
log "infra: cdk deploy $STACK_RUNNER"
( cd infra/cdk && cdk deploy "$STACK_RUNNER" --require-approval never )

# ---- 5. Force redeploy (in case nothing infra-side changed).
log "redeploy: aws apprunner start-deployment"
SERVICE_ARN="$(aws apprunner list-services --region "$REGION" \
                --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn | [0]" \
                --output text)"
if [[ -z "$SERVICE_ARN" || "$SERVICE_ARN" == "None" ]]; then
  echo "ERROR: App Runner service '$SERVICE_NAME' not found after cdk deploy." >&2
  exit 1
fi
aws apprunner start-deployment --service-arn "$SERVICE_ARN" --region "$REGION" >/dev/null

# ---- 6. Wait + report.
log "wait: polling service status (timeout 5 min)"
DEADLINE=$(( $(date +%s) + 300 ))
while true; do
  STATUS="$(aws apprunner describe-service --service-arn "$SERVICE_ARN" \
            --region "$REGION" --query 'Service.Status' --output text)"
  if [[ "$STATUS" == "RUNNING" ]]; then
    break
  fi
  if [[ "$STATUS" == "CREATE_FAILED" || "$STATUS" == "DELETE_FAILED" || "$STATUS" == "OPERATION_IN_PROGRESS" ]]; then
    log "status=$STATUS (continuing to wait)"
  fi
  if (( $(date +%s) > DEADLINE )); then
    echo "ERROR: timeout waiting for service to reach RUNNING (last status=$STATUS)." >&2
    exit 1
  fi
  sleep 10
done

URL="$(aws apprunner describe-service --service-arn "$SERVICE_ARN" \
       --region "$REGION" --query 'Service.ServiceUrl' --output text)"
log "deployed: https://$URL  (image=$IMAGE_TAG)"
