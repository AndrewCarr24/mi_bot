# MI Wiki — schema and conventions

This directory is an LLM-maintained wiki of synthesized knowledge about
the US private mortgage insurance industry, the six MIs covered in the
KB (MGIC, Radian, Essent, NMI Holdings, Arch Capital, Enact), and the
regulatory framework they operate under (PMIERs, GSE relationship,
FHFA oversight). It is a small implementation of the LLM-Wiki pattern
described by Karpathy (April 2026).

## Three layers

1. **Raw sources** — the 227 documents indexed in the dsRAG KB:
   - 18 10-K filings, 54 10-Q filings, 73 8-K filings, 72 earnings call
     transcripts (the per-MI corpus, 2023-2025)
   - 10 industry / regulatory references (PMIERs base, August 2024
     update, FHFA reports, USMI white papers, Freddie Mac PMI primer)
   - These are immutable. The wiki *cites* them by `doc_id` but never
     modifies them.

2. **The wiki** (this directory) — LLM-authored markdown:
   - `index.md` — master catalog of all wiki pages with one-line
     descriptions
   - `metrics/*.md` — explainers for the core MI metrics (PMIERs, NIW,
     IIF, persistency, loss ratio, reinsurance/CRT)
   - `companies/*.md` — one page per MI in the corpus
   - `topics/*.md` — regulatory and industry topic pages
     (Aug 2024 PMIERs update, GSE relationship, US mortgage market,
     regulatory landscape, catastrophe impact)
   - `log.md` — append-only chronological log of additions and
     significant edits

3. **The schema** — this file (`AGENTS.md`). Read it before authoring
   or maintaining the wiki.

## Page schema

Every wiki page follows this structure:

```markdown
# <page title>

> One-paragraph summary (3-5 sentences). The reader should be able to
> stop here and understand the topic at a working level.

## What it is

<concept-defining content; for company pages, business overview>

## Why it matters

<analyst-relevant context; tradeoffs, sensitivities, why analysts watch
this metric / topic / company>

## Current state (as of {YYYY-MM-DD})

<the most recent picture from the corpus — for metrics, latest values
across the 6 MIs; for companies, latest financials; for topics, latest
regulatory state>

## How it has evolved

<historical arc using corpus data — quarterly trend if applicable, or
key inflection points>

## Sources

- [doc_id_1] — what it contributed
- [doc_id_2] — what it contributed
- ...

## Related

- [[metric/persistency]]
- [[topic/pmiers_aug_2024_update]]
- ...
```

## Citation convention

- In the body of a page, cite specific facts with the source `doc_id`
  in parentheses, e.g. `(MTG_10-K_2024-12-31)` or `(INDUSTRY_PMIERS_2.0_BASE)`.
- The `Sources` section at the bottom of the page lists every
  `doc_id` referenced, with one-line context for each.
- `doc_id`s match the dsRAG KB ingestion convention exactly. The
  filings_catalog rendered in the agent's system prompt is the
  authoritative list of valid `doc_id`s.

## Cross-reference convention

- Use markdown wikilinks: `[[metrics/pmiers]]`, `[[companies/mtg_mgic]]`.
- Do not deep-link into sections — page-level only. Pages are short
  enough that a section anchor isn't needed.

## What goes in vs stays out

In:
- Synthesized industry-level knowledge (definitions, regulatory
  context, market structure)
- Cross-MI comparisons that are stable enough to be worth pre-computing
- Per-company overviews (business, capital, recent results)
- Topic / regulatory pages where the answer is structural rather than
  point-in-time numeric

Out:
- Specific quantitative lookups that are better answered by retrieving
  from a single filing (use `dsrag_kb` for those)
- Speculation, forecasts, or anything not grounded in a cited source
- Marketing-style content from a company about itself — write the
  company page from analyst perspective, citing filings, not press releases

## Lint procedures

Periodically run a health-check pass:
- Find pages that cite `doc_id`s that no longer exist in the catalog
- Find pages whose "Current state (as of …)" date is more than 6 months stale
- Find orphan pages with no inbound `[[wikilinks]]`
- Find concepts mentioned in multiple pages that lack their own page
- Find contradictions between pages (e.g., two metric definitions that
  disagree)

## Updating when new sources arrive

When a new filing is added to the corpus:
1. Read the new filing
2. Identify which existing wiki pages it affects (typically 5-15)
3. Update the relevant pages' "Current state" sections
4. Append a one-line entry to `log.md` describing what changed
