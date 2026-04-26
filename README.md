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
# One-shot query
python run_app.py "What was AMD's FY2022 revenue?"

# Eval harness
python eval/run_eval.py                            # default questions_financebench.csv
python eval/run_eval.py eval/other.csv             # custom CSV

# Rebuild the KB from data/parsed/*.md (idempotent — `exists_ok=True`)
python pipelines/build_kb.py
```

## Switching the orchestrator

```bash
# DeepSeek (default)
ORCHESTRATOR_PROVIDER=deepseek python run_app.py "..."

# Bedrock (Sonnet) — caches the system prefix via cachePoint blocks
ORCHESTRATOR_PROVIDER=bedrock python run_app.py "..."
```

The router and judge are pinned to Bedrock Haiku regardless of the
orchestrator provider.
