"""Single-query runner for the agent.

Usage:
    cd agent_fin
    python run_app.py "What was ACT's revenue in Q3 2024?"

Streams the agent's final answer to stdout.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))


async def run(query: str) -> None:
    from src.infrastructure.dsrag_kb import DSRAG_STORE_DIR

    if not DSRAG_STORE_DIR.exists():
        raise SystemExit(
            f"KB not found at {DSRAG_STORE_DIR}. "
            "Build it first with: python pipelines/build_kb.py"
        )

    from src.application.orchestrator.streaming import get_streaming_response

    async for chunk in get_streaming_response(messages=query, customer_name="User"):
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Natural-language question for the agent.")
    args = parser.parse_args()
    asyncio.run(run(args.query))
