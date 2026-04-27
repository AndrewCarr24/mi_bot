# agent_fin

Deploy-ready SEC filings research agent. LangGraph ReAct loop, single-tool
retrieval (`dsrag_kb`) over a [dsRAG](https://github.com/D-Star-AI/dsRAG)
knowledge base, with the orchestrator LLM swappable between DeepSeek
(default, OpenAI-compatible API) and Bedrock (Sonnet via Converse).

This is a clean fork of the experimentation repo — the 3-tool stack, the
FlashRank reranker, the tool-output compressor, and the `--mode` toggle
have all been removed.

## Layout

```
agent_fin/
├── data/
│   ├── parsed/                # source markdowns (TICKER_FORM_PERIOD.md) — tracked
│   ├── dsrag_store/           # persisted KB (chunks, vectors, metadata) — gitignored, rebuild
│   └── raw/                   # SEC HTML downloaded from EDGAR — gitignored, refetch
├── pipelines/
│   ├── build_kb.py            # parsed/*.md → dsrag_store/*
│   ├── bedrock_embedding.py   # Titan v2 embedder (registered with dsRAG)
│   ├── fetchers.py            # SEC EDGAR fetch helpers
│   └── parsers.py             # filing → markdown
├── src/
│   ├── config.py              # pydantic settings (provider, models, memory)
│   ├── domain/prompts.py
│   ├── infrastructure/
│   │   ├── catalog.py         # data/parsed/ → filings catalog for the prompt
│   │   ├── dsrag_kb.py        # KB singleton + auto-query helper
│   │   ├── memory.py          # AgentCore Memory hooks (optional)
│   │   └── model.py           # ChatBedrockConverse | ChatDeepSeek factory
│   └── application/orchestrator/
│       ├── streaming.py       # public async iterator interface
│       └── workflow/          # LangGraph: router → cache → agent → tools
├── eval/
│   ├── run_eval.py            # FinanceBench-style grader (CSV-driven)
│   ├── pricing.py
│   ├── usage.py
│   └── results/               # per-run CSVs of question / answer / correctness
└── run_app.py                 # one-shot CLI runner
```

The KB and the raw SEC HTML are **not in git** — at the current corpus
size the vector store is ~350 MB (over GitHub's 100 MB hard per-file
limit) and the raw HTML is ~1.3 GB. Both are regenerable from
`data/parsed/*.md` (which IS tracked, ~22 MB across 72 markdowns).

To rebuild the KB on a fresh checkout:

```bash
cd agent_fin
uv sync --extra pipelines    # add Docling + sec-edgar-downloader
set -a && . .env && set +a
python pipelines/build_kb.py # ~45-60 min for the current 72-doc corpus
```

To re-fetch and re-parse from scratch (only needed if `data/parsed/`
also gets cleaned):

```bash
python pipelines/fetchers.py # ~10 min, populates data/raw/
python pipelines/parsers.py  # ~20 min, populates data/parsed/
python pipelines/build_kb.py # ~45-60 min
```

## Setup

```bash
cd agent_fin
uv sync
cp .env.example .env       # fill in DEEPSEEK_API_KEY
set -a && . .env && set +a
```

`AWS_REGION` (and a credential chain) is required even with the DeepSeek
orchestrator: KB build calls Bedrock Titan v2 for embeddings, and the
router/judge always run on Haiku via Converse.

**Optional: LangSmith tracing.** Set `LANGSMITH_TRACING=true`,
`LANGSMITH_API_KEY=...` (from https://smith.langchain.com/settings),
and `LANGSMITH_PROJECT=agent-fin` in `.env`. LangChain auto-instruments
from those env vars — no code changes — and every node, tool call,
and LLM round-trip shows up in the LangSmith UI with input/output
prompts, tokens, latency, and cost. Free tier (5K traces/month) covers
demo traffic comfortably.

## Running

```bash
# One-shot CLI query
python run_app.py "What was AMD's FY2022 revenue?"

# Eval harness
python eval/run_eval.py                            # default questions_financebench.csv
python eval/run_eval.py eval/other.csv             # custom CSV

# Rebuild the KB from data/parsed/*.md (idempotent — `exists_ok=True`)
python pipelines/build_kb.py
```

## Local development

Four loops in increasing cost/time. Use the cheapest one that catches the
bug you're chasing.

```bash
# 1. Inner loop (seconds): live-reload FastAPI + curl
uvicorn api:app --reload --port 8000
curl -N -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What was AMD revenue in FY2022?","conversation_id":"dev-001"}'

# Multi-turn: reuse the same conversation_id across calls; the in-process
# MemorySaver checkpointer retains history per conversation_id.

# 2. Mid loop (~3-5 min): regression across the FinanceBench eval set
python eval/run_eval.py
# → eval/results/<input>_<ts>.csv with per-question correctness + cost

# 3. Outer loop (~1 min): build + run the production container locally
docker build --platform=linux/amd64 -t agent-fin:local .
docker run --rm -p 8080:8080 \
  --env-file .env -e AWS_REGION=us-east-1 \
  -v ~/.aws:/home/app/.aws:ro agent-fin:local
# → catches container packaging issues that uvicorn alone won't surface

# 4. Deploy loop (~5 min): push to ECR + redeploy App Runner
#    Substitute <ACCOUNT_ID> (aws sts get-caller-identity) and
#    <SERVICE_ARN> (aws apprunner list-services) before running.
ACCOUNT_ID=<ACCOUNT_ID>
SERVICE_ARN=<SERVICE_ARN>
docker build --platform=linux/amd64 \
  -t ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/agent-fin:latest .
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com
docker push ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/agent-fin:latest
aws apprunner start-deployment --service-arn ${SERVICE_ARN}
```

**Cost note**: local uvicorn is free; each `/ask` call costs DeepSeek
+ Bedrock Haiku tokens (roughly 1-5¢ per question). The full eval over
~23 questions costs ~$0.50-1.

## Switching the orchestrator

```bash
# DeepSeek (default)
ORCHESTRATOR_PROVIDER=deepseek python run_app.py "..."

# Bedrock (Sonnet) — caches the system prefix via cachePoint blocks
ORCHESTRATOR_PROVIDER=bedrock python run_app.py "..."
```

The router and judge are pinned to Bedrock Haiku regardless of the
orchestrator provider.
