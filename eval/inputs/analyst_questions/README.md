# MI Analyst Question Library

A topic-organized catalog of questions a working MI analyst at one of the six US private mortgage insurers (ACGL, ACT, ESNT, MTG, NMIH, RDN) would pose against this KB (10-K, 10-Q, 8-K, transcripts, plus PMIERs/USMI/FHFA references).

Two downstream uses:

- **(A) Eval expansion** — feed selected questions into a new eval CSV with KB-grounded `expected_answer` strings.
- **(B) Capability-gap survey** — identify question shapes the current agent architecture is unlikely to answer well, regardless of whether the data is in the KB.

Spec: [`docs/superpowers/specs/2026-05-07-mi-analyst-question-research-design.md`](../../../docs/superpowers/specs/2026-05-07-mi-analyst-question-research-design.md)

## Index

| # | Topic | File |
|---|-------|------|
| 01 | Quarterly results & profitability | [`01-quarterly-results.md`](01-quarterly-results.md) |
| 02 | Capital management & PMIERs | [`02-capital-management.md`](02-capital-management.md) |
| 03 | Credit & delinquency | [`03-credit-delinquency.md`](03-credit-delinquency.md) |
| 04 | Regulatory & GSE landscape | [`04-regulatory-gse.md`](04-regulatory-gse.md) |
| 05 | Reinsurance & risk transfer | [`05-reinsurance.md`](05-reinsurance.md) |
| 06 | Competitive dynamics & market share | [`06-competitive-dynamics.md`](06-competitive-dynamics.md) |
| 07 | Macro & housing | [`07-macro-housing.md`](07-macro-housing.md) |
| 08 | Forward-looking guidance & strategy | [`08-forward-looking.md`](08-forward-looking.md) |

## Methodology

Eight parallel research subagents (one per topic) used `WebSearch` and `WebFetch` to draw question patterns from at least three distinct source categories per topic. Sources covered include:

- Sell-side equity research (Stockstory, Motley Fool, MarketBeat coverage of MTG/ESNT/ACGL/NMIH/RDN/ACT)
- MI investor materials (10-K cover letters, IR presentations, 8-K press releases)
- Earnings call transcripts — Q&A sections specifically
- USMI white papers (2020 policy paper, 2023 resiliency, PMIERs fact sheet)
- FHFA publications (annual reports, OIG reports, PMIERs guidance)
- Trade press: Inside Mortgage Finance, HousingWire, National Mortgage News, ABA Banking Journal
- Industry data: MBA, ICE Mortgage Technology, Cotality, Milliman, Urban Institute
- Catastrophe-bond / ILS specialty press: Artemis.bm

Each subagent rated current-agent-difficulty informed by the documented failure modes diagnosed earlier in this branch's eval work (see `eval/diagnostics/`).

## Summary stats

- **Total questions:** 160 (20 per topic × 8 topics)
- **Question shapes:** cross-issuer 68 · longitudinal 28 · qualitative 24 · point-in-time 23 · mixed 17
- **Difficulty distribution:** hard 92 · moderate 51 · easy 17

The cross-issuer skew is intentional — it is the dominant analyst use case (cohort comparison) and also the area most under-represented by the existing 28-question eval (which is heavy on single-issuer point-in-time lookups).

## Cross-topic capability-gap synthesis

The eight topic files independently surfaced the same handful of failure modes. They map cleanly to architectural issues we'd already diagnosed:

### Gap 1 — Heavy multi-issuer cohort retrieval overruns the per-turn context budget

**Reported in: every topic.** The single most common gap. Pulling parallel disclosures across all six MIs at the depth the question requires generates >60K tokens of retrieval, which forces Stage 3 of `trim_history` to evict the earliest (often highest-relevance) chunks before the synthesis call. The agent then either drops an issuer silently or falls back to a generic framework.

Representative questions: 01-Q2 (cohort yield trend), 02-Q1 (cohort PMIERs cushion), 03-Q2 (cohort delinquency by FICO), 04-Q5 (cohort PMIERs phase-in disclosures), 05-Q12 (CRT attach/detach across cohort), 06-Q1 (NIW market-share trend), 07-Q2 (NIW vs FHA penetration), 08-Q5 (cohort capital-return outlook).

This gap shows up roughly 40+ times across the 160 questions. Architectural fixes already considered: cohort-preload routing (tested, didn't help — induced complacency), score-aware Stage 3 trim (refuted by data — score doesn't cleanly separate signal from noise), per-issuer retrieval-budget enforcement (untested, plausible direction).

### Gap 2 — 8-K Item-code retrieval misses when the press-release exhibit lacks the literal Item header

**Reported in: 01, 02, 04, 05, 06, 08.** When the analyst asks about a specific Item — most often Item 5.02 (officer/director changes), 7.01 (Reg FD), 8.01 (Other Events), or 5.03 (bylaws) — the body text indexed in the KB is the press-release exhibit, which often does NOT contain the literal `Item 5.02` string. The 8-K cover-page Item designations live in metadata that wasn't ingested. Retrieval ranking then loses the relevant chunk to longer Risk-Factor or governance language that mentions "directors and officers" in regulatory contexts.

Representative questions: 01-Q12, 01-Q20, 02-Q5, 04-Q17, 06-Q19, 08-Q9, 08-Q11, 08-Q18.

This is a **corpus-level gap** — best fix is filing-type metadata enrichment at ingestion (mark each 8-K with the Items it disclosed), not prompt or retrieval-time fixes. Until that happens, expect persistent failure here. q28 in the existing eval is the canonical example.

### Gap 3 — Synthesis genericness on qualitative cohort questions

**Reported in: every topic.** When the question asks what each issuer "said" or "characterized" or "emphasized" about a topic, the agent produces a flattened generic paragraph ("the cohort emphasized discipline") rather than preserving issuer-specific verbatim language. CEOs use overlapping vocabulary — "rational," "disciplined," "prudent," "risk-adjusted" — which encourages the LLM to merge them.

Representative questions: 01-Q9, 02-Q7, 02-Q11, 03-Q10, 04-Q3, 04-Q15, 05-Q14, 06-Q15, 06-Q17, 07-Q3, 08-Q1, 08-Q13.

The cleanest mitigation isn't a prompt nudge (we tested an analogous "nudge D" on q27 — didn't lift accuracy and added latency) but rather a structured per-issuer extraction step: extract a single verbatim quote per issuer in stage 1, then synthesize from the structured set in stage 2. That's the "two-stage extract→synthesize" pattern explored earlier.

### Gap 4 — Transcript Q&A buried under 10-K boilerplate

**Reported in: 01, 03, 06.** When a question asks "how did management explain X" or "what did analysts press on", the answer almost always lives in a transcript Q&A bullet — often a few sentences exchanged between an analyst and an executive. The agent's BM25/vector ranker tends to score longer Risk-Factor or MD&A passages higher because they contain more topic vocabulary, even though they're less responsive to the analyst-style question.

Representative questions: 01-Q9, 01-Q14, 03-Q3, 03-Q11, 06-Q4, 06-Q13, 06-Q16.

Architectural mitigation: doc-type-aware ranking (boost TRANSCRIPT chunks when the question phrasing signals "what did management say") or a separate transcript-Q&A retrieval mode. Not yet attempted.

### Gap 5 — Cross-document synthesis between regulatory and issuer-specific sources

**Reported in: 03, 04, 07.** Questions that require pulling a regulatory fact (PMIERs minimum, FHFA goal, USMI factsheet figure) AND an issuer-specific number to compare. The agent tends to retrieve only one source-type per query and either misses the regulatory grounding or misses the issuer-level number.

Representative questions: 03-Q14, 03-Q19, 04-Q15, 07-Q4, 07-Q10, 07-Q13, 07-Q18, 07-Q20.

Architectural mitigation: explicit two-bucket retrieval (one INDUSTRY_* doc, one issuer-specific doc) when the question references a regulatory benchmark.

### Gap 6 — Negative-result questions trigger self-doubt re-query loops

**Reported in: 02, 05.** When the answer is "none" or "no disclosure," the agent's tendency is to over-search before concluding rather than confidently report absence. This burns tool budget and risks hitting the per-turn cap for no marginal gain.

Representative questions: 02-Q15 (no cohort breach of 25:1 RBC), 05-Q14 (no profit-commission writedown).

This is the same self-doubt pattern that sank q24 (yields) earlier — the agent had the answer, didn't trust it, re-queried, hit cap, finalize_node trim degraded the result.

### Gap 7 — Out-of-corpus references (proxy statements, sell-side consensus)

**Reported in: 01, 08.** Analysts ask about content the KB doesn't index — DEF 14A proxy disclosures (NEO compensation, board composition, succession planning) and sell-side consensus comparisons (consensus EPS vs actual). The agent currently has no graceful "this isn't in the KB; here's what *is* and where to look elsewhere" convention. It either fabricates or produces empty answers.

Representative questions: 01-Q20 (consensus EPS comparison), 08-Q10 (NEO comp disclosure), 08-Q17 (compensation alignment with strategy).

Mitigation: a router-level "out-of-scope" classification + a templated answer pattern for these.

## Suggested next steps

These are observations from the gap synthesis, not commitments — for downstream brainstorming.

- **Filing-type metadata enrichment** (Gap 2) — re-index 8-Ks with the Item codes parsed from the cover page. Single biggest accuracy lift available; one-time corpus-level work.
- **Per-issuer cohort budget** (Gap 1) — instead of letting fan-out exceed the context budget, enforce a per-issuer chunk allocation at retrieval time so each of the six is guaranteed representation.
- **Two-stage extract → synthesize for tabular cohort questions** (Gap 3) — extract-then-synthesize pattern; explored conceptually earlier in this branch.
- **Doc-type-aware ranking** (Gap 4) — boost TRANSCRIPT chunks for "what did management say" patterns.
- **Out-of-scope routing** (Gap 7) — explicit classification + templated answer when the question references content known to live outside the KB.

Eval expansion (use A) should sample across difficulty buckets — primarily from `easy` (17 questions; quick wins to confirm baseline behavior) and `moderate` (51; targets the mid-zone where small architectural changes can move accuracy), with selective inclusion from `hard` (92; for tracking long-term progress on the structural failure modes above).
