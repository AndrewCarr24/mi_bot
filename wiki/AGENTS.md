# MI Wiki — schema and conventions

This directory is an LLM-maintained wiki of synthesized knowledge about
the U.S. private mortgage insurance industry, the six MIs covered in
the dsRAG knowledge base (Arch, Enact, Essent, MGIC, NMI Holdings,
Radian), and the regulatory framework they operate under (PMIERs, the
GSE relationship, FHFA oversight, state insurance regulation, Bermuda
oversight where applicable). It is a small implementation of the
LLM-Wiki pattern described by Karpathy (April 2026).

## Three layers

1. **Raw sources** — the documents indexed in the dsRAG KB:
   - The per-MI corpus (10-Ks, 10-Qs, 8-Ks, earnings call transcripts,
     2023 through Q4 2025) for Arch, Enact, Essent, MGIC, NMI, Radian.
   - Industry / regulatory references (the PMIERs base requirements,
     the August 2024 PMIERs update, FHFA reports, USMI white papers,
     the Freddie Mac private mortgage insurance handbook).
   - These are immutable. The wiki *cites* them by `doc_id` but never
     modifies them.

2. **The wiki** (this directory) — LLM-authored markdown:
   - `companies/*.md` — one page per MI in the corpus.
   - `topics/*.md` — regulatory and industry topic pages
     (GSE relationship, U.S. mortgage market, MI regulatory landscape,
     August 2024 PMIERs update, catastrophe impact on MI).
   - `metrics/*.md` — explainers for the core MI metrics (PMIERs,
     NIW, IIF, persistency, loss ratio, reinsurance / CRT). Currently
     unwritten in this generation of the wiki — to be added.
   - `AGENTS.md` — this file. Read it before authoring or editing
     wiki pages.

3. **The schema** — defined below.

## Page schema

Every wiki page follows this structure:

```markdown
# <page title>

> One-paragraph summary blockquote (3–6 sentences). The reader should
> be able to stop here and understand the topic at a working level.
> Cite the most important supporting doc_id at the end of the
> blockquote.

## What it is

Concept-defining content. For company pages, the corporate structure,
operating subsidiaries, segment reporting, and the basic product /
business overview. For topic pages, the structural definition of the
topic — what regulatory framework, what market segment, what mechanism.

## Why it matters

Three to five paragraphs explaining why the topic is operationally
relevant for an analyst. Be specific about cause-and-effect. Avoid
boilerplate. Tie back to current data wherever possible.

## Current state (as of YYYY-MM-DD)

The most recent reportable state. For company pages, this is year-end
financials, capital position, capital return cadence, recent strategic
events. For topic pages, this is the present-day status of the
relationship, regulation, or market dynamic.

## How it has evolved

The trajectory through time, organized chronologically (or thematically
if more natural). Frame the evolution in terms of decisions and events
rather than just numbers — what changed, what drove it, what the
implications were.

## Sources

A list of every source cited inline, formatted:

- [doc_id] — what this source contributed (specific facts /
  figures / framing).

## Related

Wikilinks to the most relevant adjacent pages, formatted:

- [[companies/<name>]]
- [[topics/<name>]]
- [[metrics/<name>]]
```

## Citation conventions

- **Inline citations** use plain parentheses: `(MTG_10-K_2025-12-31)`.
- For multiple sources in one citation, separate with semicolons:
  `(MTG_10-K_2025-12-31; MTG_TRANSCRIPT_2025-12-31)`.
- The `Sources` section at the bottom of each page uses square
  brackets in a list: `- [MTG_10-K_2025-12-31] — what it provided`.
- Cite **every** numeric claim and every causal claim. If a fact
  cannot be cited from a corpus document, do not assert it.

## Authoring discipline

- **Validate against source data, not against other wiki pages.**
  Other wiki pages are not authoritative. Before writing or
  recommending content, ground claims in the underlying 10-Ks,
  transcripts, or industry references.
- **Don't make comparative claims you can't source.** "X is the
  largest" / "X is the only one" / "X has the highest" require
  evidence from outside the company's own filing — usually
  *Inside Mortgage Finance* market-share data or a cross-MI table
  in an industry reference. Otherwise rephrase as a non-comparative
  fact.
- **Keep editorial framing tight.** No "industry-leading" /
  "best-in-class" / "most conservatively managed" without a
  sourced comparison. Translate disclosure boilerplate into
  analyst-relevant implications rather than restating it.
- **Don't conflate cause and effect.** If two factors both influence
  a metric, separate them rather than welding them together. (E.g.,
  reserve-release narrowing → loss ratio is one chain; PMIERs
  multiplier expiration → PMIERs cushion is another. Don't merge.)
- **Date-stamp current state.** When the page references "year-end
  2025" or "Q4 2025," make sure that's accurate at the moment of
  writing and that the page heading "## Current state (as of …)"
  uses the corresponding date.

## File naming

- Company pages: `companies/<ticker_lower>_<name_lower>.md`
  (e.g., `mtg_mgic.md`, `acgl_arch.md`).
- Topic pages: `topics/<descriptive_slug>.md`.
- Metric pages: `metrics/<metric_slug>.md`.
- All wikilinks `[[topics/<name>]]` etc. use the path-prefixed form
  to make cross-folder references unambiguous.
