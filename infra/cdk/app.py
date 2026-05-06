#!/usr/bin/env python3
"""CDK app entrypoint for agent_fin infrastructure."""

import os

import aws_cdk as cdk

from ecr_stack import AgentFinEcrStack
from runner_stack import AgentFinRunnerStack


app = cdk.App()

env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
)

ecr_stack = AgentFinEcrStack(app, "AgentFinEcrStack", env=env)
runner_stack = AgentFinRunnerStack(
    app, "AgentFinRunnerStack", repo=ecr_stack.repo, env=env
)
runner_stack.add_dependency(ecr_stack)

app.synth()
