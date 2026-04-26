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
│   ├── parsed/                # source markdowns (TICKER_FORM_PERIOD.md)
│   └── dsrag_store/           # persisted KB (chunks, vectors, metadata)
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
│   ├── run_eval.py            # FinanceBench-style grader
│   ├── pricing.py
│   ├── usage.py
│   └── questions_financebench.csv
├── scripts/probe_q13_q14.py   # retrieval-vs-harness diagnostic
└── run_app.py                 # one-shot CLI runner
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
