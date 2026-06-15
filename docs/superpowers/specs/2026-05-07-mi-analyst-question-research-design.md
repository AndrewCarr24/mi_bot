# MI Analyst Question Research — Design

**Date:** 2026-05-07
**Status:** Design (pre-implementation)
**Owner:** Andrew Carr
**Skill flow:** brainstorming → writing-plans → executing-plans (via dispatching-parallel-agents)

## Problem

The current MI eval suite (`eval/questions_mi_28q.csv`) is heavy on point-in-time value lookups ("What was MGIC's PMIERs Available Assets at 12/31/2024?"). It exercises the agent's ability to retrieve specific figures, but it under-represents the question shapes a real MI analyst at one of the cohort companies would actually pose: longitudinal trend analysis, cross-issuer benchmarking with qualitative dimensions, regulatory-impact synthesis, transcript-Q&A signal extraction, forward-looking guidance interpretation, and so on.

This project produces a research artifact — a folder of structured markdown — that catalogs the questions a working MI analyst asks against this kind of corpus (10-K, 10-Q, 8-K, transcripts, plus industry/regulatory references already in the KB). The artifact serves two downstream uses:

- **(A) Eval expansion:** the questions feed a new eval CSV whose expected answers are authored against the KB, growing the test surface beyond 28 mostly-lookup questions.
- **(B) Capability-gap survey:** flagging questions that the current agent's architecture is unlikely to answer well, regardless of whether the data is in the KB. These become input to future architecture work.

## Decisions

| # | Question | Choice |
|---|---|---|
| 1 | Research organization | Topic-first (8 topics that match analyst workflow), not source-first or hybrid. Each topic md aggregates evidence across sources. |
| 2 | Source breadth | Sell-side equity research, MI investor materials (presentations, press releases, IR pages), FHFA / Fannie / Freddie publications, USMI and trade press, earnings call Q&A archives, broker-dealer notes, mortgage-market analyst reports. Subagents pick representative sources per topic, not exhaustive sweep. |
| 3 | Output format | Folder `agent_fin/eval/inputs/analyst_questions/` with one md per topic + a README index. Each question has structured metadata (shape, source, KB doc-types, current-agent-difficulty, optional expected-answer notes). |
| 4 | Question depth target | ~12-20 questions per topic × 8 topics = ~100-150 total. Moderate depth — enough to meaningfully expand the eval and identify gaps, not exhaustive. |
| 5 | Expected answers | NOT researched in this pass. Subagents may include "expected-answer notes" if the source data turned them up incidentally, but eval-grade `expected_answer` strings are authored in a separate downstream pass against the KB. |
| 6 | Execution pattern | `superpowers:dispatching-parallel-agents` — 8 parallel research subagents (one per topic), each with isolated context and a focused md template. Wall-time target ~25-30 min. Cost target ~$5-10. |

## Topic list

| # | Topic | Scope |
|---|-------|-------|
| 01 | Quarterly results & profitability | NIW, IIF, premium yields (in-force, NIW-rate, net-of-reinsurance), loss ratios, expense ratios, ROE, EPS drivers, segment vs consolidated reporting |
| 02 | Capital management & PMIERs | PMIERs sufficiency / available assets / cushion, dividends, share repurchases, holding-co vs operating-co capital, debt covenants, capital allocation framework |
| 03 | Credit & delinquency | Default rate, delinquency cohort progression, claim severity, cures and rescissions, geographic concentration, hurricane/disaster impact, vintage performance |
| 04 | Regulatory & GSE landscape | PMIERs updates (Aug 2024 Guidance 2024-01, March 2025 2024-02), GSE policy / pilot programs, FHFA actions, state insurance regulation, holding-company law, charter constraints |
| 05 | Reinsurance & risk transfer | CRT (Bellemeade, Oaktown, Triangle Re), ILS structures, quota share, excess of loss, M-Cover, ceding economics, profit commission, ceded loss recoveries |
| 06 | Competitive dynamics & market share | NIW-share trends, customer concentration, pricing discipline, risk-based pricing engines (Rate GPS, RADAR Rates), new entrant risk, market consolidation |
| 07 | Macro & housing | Origination volume, mortgage rates, persistency, refi cycle dynamics, HPA, regional housing markets, GSE share, FHA/VA share, refinance vs purchase mix |
| 08 | Forward-looking guidance & strategy | Transcript Q&A signals, capital-return outlook, M&A posture, segment-strategy commentary, multi-year guidance, management priorities, ESG/governance |

## Per-md structure

```markdown
# <Topic name>

## Why this matters to MI analysts
[1-2 paragraphs: what an analyst is trying to learn from this topic;
 what decisions it informs]

## Sources consulted
- [bullet list with URLs]

## Questions

### Q1: <question text>
- **Shape:** point-in-time | longitudinal | cross-issuer | qualitative | mixed
- **Source:** [where this pattern was observed in the wild — URL or citation]
- **KB doc-types likely to contain answer:** [10-K MD&A, 10-Q seg reporting,
   transcript Q&A, 8-K Item 5.02, etc.]
- **Current-agent-difficulty:** easy | moderate | hard
  Rationale: [one line — e.g., "requires cross-issuer synthesis the agent
  hits the cap on" or "single-doc value lookup the agent already handles"]
- **Expected-answer notes:** [optional — only if research surfaced data]

### Q2: ...
[12-20 questions per topic]

## Capability gaps observed
[Which question shapes/types are likely beyond the current agent.
 Cross-reference with the failure modes already diagnosed: cap+trim
 interaction, retrieval-ranking misses on Highlights bullets,
 missed cohort coverage, etc.]
```

## Output location

```
agent_fin/eval/inputs/analyst_questions/
├── README.md                       # index, methodology, cross-topic gap synthesis
├── 01-quarterly-results.md
├── 02-capital-management.md
├── 03-credit-delinquency.md
├── 04-regulatory-gse.md
├── 05-reinsurance.md
├── 06-competitive-dynamics.md
├── 07-macro-housing.md
└── 08-forward-looking.md
```

## Subagent dispatch

`superpowers:dispatching-parallel-agents` — 8 parallel general-purpose research subagents.

Each subagent receives a self-contained prompt with:

- **Topic name + scope description** (from the table above).
- **MI cohort tickers** (ACGL, ACT, ESNT, MTG, NMIH, RDN) and full company names.
- **KB structure** — what doc types exist (10-K, 10-Q, 8-K, TRANSCRIPT) and what industry/regulatory references are indexed (PMIERs base + 2024 guidance, USMI white papers, FHFA reports, Freddie PMI handbook).
- **Current-agent-known-failure-modes** — so the difficulty rating is informed (cap+trim spirals on heavy single-turn retrieval; retrieval ranking misses on Highlights bullets vs Risk Factor boilerplate; cohort breadth-first coverage drops; trim drops oldest tool results, etc.).
- **The md template** verbatim.
- **Target: 12-20 questions** with full metadata.
- **Source citation requirement** — every question must cite where the pattern came from.
- **Output path** — `agent_fin/eval/inputs/analyst_questions/<NN>-<topic-slug>.md`.
- **Constraints** — don't write any other files, don't modify any existing eval CSV, don't run the agent.

Tool budget per subagent: WebFetch / WebSearch heavy. ~15-25 min wall time. ~$0.50-1.50 each.

## Acceptance criteria

- 8 topic md files exist, each with the required structure.
- Each contains 12-20 questions with all five required metadata fields populated (Shape, Source, KB doc-types, Current-agent-difficulty, Expected-answer notes optional).
- Sources are real and citable (URLs to actual analyst reports, FHFA pages, MI press releases, transcript archives, etc.).
- README.md indexes the 8 topic files and includes a cross-topic synthesis of capability-gap themes.
- No other files written; no eval CSVs modified; no agent runs triggered.

## What this design intentionally does NOT do

- Does not author eval-grade `expected_answer` strings (separate downstream pass).
- Does not modify the agent code, prompts, or KB.
- Does not commit a new eval CSV — only the research artifact.
- Does not run any agent eval (subagents are research-only).
- Does not exhaustively survey every possible MI source — moderate depth.

## Risks

- **Hallucinated questions / citations.** Mitigation: each question must cite a real URL; we'll spot-check a sample post-dispatch.
- **Coverage skew if a subagent leans too heavily on one source.** Mitigation: prompt requires sources from at least 3 distinct categories per topic.
- **Topic overlap (e.g. PMIERs appears in #02 capital, #04 regulatory).** Acceptable — different framings of the same underlying topic are useful for the eval.
- **One subagent failing.** Acceptable — 7/8 topics still produces a usable artifact; the failed topic can be re-dispatched.
