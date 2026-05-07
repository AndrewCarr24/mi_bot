"""App Runner service + IAM roles for agent_fin."""

from __future__ import annotations

import os

from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    Stack,
    aws_apprunner as apprunner,
    aws_dynamodb as dynamodb,
    aws_ecr as ecr,
    aws_iam as iam,
)
from constructs import Construct


REQUIRED_ENV_VARS = ("AGENT_PASSWORD", "COOKIE_SECRET", "DEEPSEEK_API_KEY", "AWS_REGION", "CHAINLIT_AUTH_SECRET")
OPTIONAL_ENV_VARS = ("LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_TRACING")


def _env_or_fail(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Required env var {name!r} is unset. "
            "Run `set -a && . .env && set +a` before `cdk deploy`."
        )
    return value


class AgentFinRunnerStack(Stack):
    """App Runner service for agent_fin.

    - 1 vCPU / 4 GB memory (KB pickle is ~350 MB; need headroom)
    - min/max instances = 1 (single-instance assumption per design)
    - No auto-deploy from ECR (deploy.sh triggers `start-deployment` explicitly)
    - Env vars baked in from local environment at `cdk deploy` time
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        repo: ecr.IRepository,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Validate required env vars before going further.
        for name in REQUIRED_ENV_VARS:
            _env_or_fail(name)

        # ---- Access role: App Runner pulls the image from ECR.
        access_role = iam.Role(
            self,
            "AppRunnerAccessRole",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
        )
        repo.grant_pull(access_role)

        # ---- Instance role: container's runtime AWS permissions.
        instance_role = iam.Role(
            self,
            "AppRunnerInstanceRole",
            assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com"),
        )
        # Bedrock invoke for: Titan v2 embeddings, Haiku (router/judge),
        # Sonnet (orchestrator when ORCHESTRATOR_PROVIDER=bedrock).
        instance_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v2:0",
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0",
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-sonnet-4-6-v1:0",
                    # Cross-region inference profiles (e.g., us.anthropic...)
                    f"arn:aws:bedrock:{self.region}:{self.account}:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    f"arn:aws:bedrock:{self.region}:{self.account}:inference-profile/us.anthropic.claude-sonnet-4-6",
                ],
            )
        )

        # ---- DynamoDB table for Chainlit thread + message storage.
        threads_table = dynamodb.Table(
            self,
            "AgentFinThreadsTable",
            table_name="agent-fin-threads",
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="expires_at",
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )
        threads_table.add_global_secondary_index(
            index_name="UserThread",
            partition_key=dynamodb.Attribute(
                name="UserThreadPK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="UserThreadSK", type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        threads_table.grant_read_write_data(instance_role)

        # ---- Build env-var list for App Runner.
        runtime_env = []
        for name in REQUIRED_ENV_VARS:
            runtime_env.append(
                apprunner.CfnService.KeyValuePairProperty(
                    name=name, value=_env_or_fail(name)
                )
            )
        for name in OPTIONAL_ENV_VARS:
            value = os.environ.get(name)
            if value:
                runtime_env.append(
                    apprunner.CfnService.KeyValuePairProperty(name=name, value=value)
                )

        # Production-only sessions config — set explicitly here, not from
        # the local .env. Local dev uses the Settings field defaults.
        runtime_env.append(
            apprunner.CfnService.KeyValuePairProperty(
                name="DATA_LAYER_BACKEND", value="dynamodb"
            )
        )
        runtime_env.append(
            apprunner.CfnService.KeyValuePairProperty(
                name="DYNAMODB_THREADS_TABLE", value=threads_table.table_name
            )
        )

        # ---- App Runner service.
        # Using L1 CfnService for full control over image-deployment knobs.
        service = apprunner.CfnService(
            self,
            "AgentFinService",
            service_name="agent-fin",
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=access_role.role_arn,
                ),
                auto_deployments_enabled=False,  # explicit start-deployment from deploy.sh
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=f"{repo.repository_uri}:latest",
                    image_repository_type="ECR",
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        port="8080",
                        runtime_environment_variables=runtime_env,
                    ),
                ),
            ),
            instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
                cpu="1024",      # 1 vCPU
                memory="4096",   # 4 GB
                instance_role_arn=instance_role.role_arn,
            ),
            health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                protocol="HTTP",
                path="/health",
                interval=20,
                timeout=5,
                healthy_threshold=2,
                unhealthy_threshold=3,
            ),
            network_configuration=apprunner.CfnService.NetworkConfigurationProperty(
                egress_configuration=apprunner.CfnService.EgressConfigurationProperty(
                    egress_type="DEFAULT",
                ),
                ingress_configuration=apprunner.CfnService.IngressConfigurationProperty(
                    is_publicly_accessible=True,
                ),
            ),
        )

        CfnOutput(
            self,
            "ServiceUrl",
            value=f"https://{service.attr_service_url}",
            description="Public URL for agent_fin.",
        )
        CfnOutput(
            self,
            "ServiceArn",
            value=service.attr_service_arn,
            description="ARN used by deploy.sh for `apprunner start-deployment`.",
        )
        CfnOutput(
            self,
            "ThreadsTableName",
            value=threads_table.table_name,
            description="DynamoDB table holding Chainlit thread + message history.",
        )
