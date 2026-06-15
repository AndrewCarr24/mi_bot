"""ECR repository for the agent_fin container image."""

from __future__ import annotations

from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ecr as ecr,
    Duration,
)
from constructs import Construct


class AgentFinEcrStack(Stack):
    """ECR repo: scan-on-push, lifecycle policy retains last 10 images."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.repo = ecr.Repository(
            self,
            "AgentFinRepo",
            repository_name="agent-fin",
            image_scan_on_push=True,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description="Retain last 10 images.",
                    max_image_count=10,
                ),
            ],
        )

        CfnOutput(
            self,
            "EcrRepoUri",
            value=self.repo.repository_uri,
            description="URI for `docker push`.",
        )
