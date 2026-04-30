# IIF (Insurance in Force)

> Insurance in Force ("IIF") is the unpaid principal balance of mortgage loans an MI insures — the running stock of business that drives current and future earned premium. IIF grows with NIW, declines with cancellations (refinances, sales, prepayments, HOPA-mandated terminations) and claims, and amortizes naturally as borrowers pay down principal. At year-end 2025, the six U.S. private mortgage insurers held approximately $1.3 trillion of combined primary IIF, with MGIC crossing $300 billion for the first time (MGIC IIF $303.1B; Radian $282.5B; Enact $273.1B; Essent $248.4B; NMI $221.4B; Arch USMI not separately disclosed) (MTG_10-K_2025-12-31; RDN_10-K_2025-12-31; ACT_10-K_2025-12-31; ESNT_10-K_2025-12-31; NMIH_10-K_2025-12-31). For the industry overall, USMI reports approximately $1.4 trillion in mortgages guaranteed by the GSEs with private MI protection as of September 30, 2023 (INDUSTRY_USMI_RESILIENCY_2023-11). IIF is the most important balance-sheet metric for MIs because most premiums earned in any given year come from policies written in prior years.

## What it is

**Definition.** Per MGIC's glossary, "Insurance in force is the unpaid principal balance, either reported to us by mortgage servicers or estimated by us, for the loans we insure" (MTG_10-K_2025-12-31). Other MIs use definitionally consistent language:

- **Enact**: "IIF refers to the unpaid principal balance of mortgage loans that we insure directly" (ACT_10-K_2025-12-31).
- **Enact (alternate)**: "IIF at the time of origination is used to determine premiums as the premium rate is expressed as a percentage of IIF. IIF is one of the primary drivers of our future earned premium" (ACT_10-K_2025-12-31).

IIF is reported as **direct primary** (before reinsurance) by default in MI 10-Ks (MTG_10-K_2025-12-31). The portion of IIF subject to quota share or excess-of-loss reinsurance is disclosed separately in segment / Exhibit D footnotes (see [[topics/crt_reinsurance]]).

**Mechanics — what changes IIF.** Per Enact's MD&A: "Cancellations of our insurance policies as a result of prepayments and other reductions of IIF, such as rescissions of coverage and claims paid, generally have a negative effect on premiums earned" (ACT_10-K_2025-12-31). Specifically:

- **NIW** adds to IIF at the original principal balance of each insured loan (NMIH_10-K_2025-12-31; see [[metrics/niw]]).
- **Persistency cancellations** remove IIF when a borrower refinances out of MI coverage, sells the home, or otherwise prepays the loan; HOPA-mandated termination at 78% LTV also removes IIF (INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09; see [[metrics/persistency]]).
- **Borrower-requested cancellation** at 80% LTV with a "good payment history" further reduces IIF on a discretionary basis (INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09).
- **Claims paid** reduce IIF when a defaulted loan results in a claim payment to the lender / GSE.
- **Natural amortization** — as borrowers pay down principal over time, the unpaid principal balance of each insured loan declines, gradually reducing IIF even on policies that remain in force.

**RIF vs. IIF**. Risk in Force ("RIF") is the smaller, coverage-weighted measure: "for an individual loan insured by us, [RIF] is equal to the unpaid loan principal balance, as reported to us, multiplied by the insurance coverage percentage" (MTG_10-K_2025-12-31 glossary). Across the industry, RIF is approximately 25-27% of IIF, reflecting typical MI coverage percentages (see [[topics/gse_relationship]] for the standard coverage table).

**Pool vs. primary**. The figures cited above are *primary* IIF — coverage on individual loans. Pool insurance (coverage on a finite set of loans with aggregate stop-loss limits) is a small residual; Enact reports its remaining pool exposures are 0.1% of total RIF (ACT_10-K_2025-12-31).

## Why it matters

**First, IIF is the principal driver of future earned premium.** Premium rates are expressed as a percentage of IIF; current-period earned premium reflects the running stock (and, for monthly-premium policies, the period over which IIF was in force). Per Enact: "Based on the composition of our insurance portfolio, with monthly premium policies comprising a larger proportion of our total portfolio than single premium policies, an increase or decrease in IIF generally has a corresponding impact on premiums earned" (ACT_10-K_2025-12-31). For Enact specifically, a 10% decline in primary persistency on existing IIF would reduce earned premiums by approximately $95 million in the first full year, partially offset by higher policy cancellations in single-premium products (ACT_10-K_2025-12-31).

**Second, IIF growth is constrained in elevated-rate environments.** When mortgage rates are high relative to outstanding note rates on the in-force book, refinance activity is suppressed (high persistency) but new origination is also suppressed (low NIW). The net effect is muted IIF growth. Through 2024-2025, IIF growth across the six MIs averaged roughly 2-3% per year — a pace consistent with elevated persistency offsetting modest NIW (ESNT_10-K_2025-12-31; ACT_10-K_2025-12-31; MTG_TRANSCRIPT_2025-12-31).

**Third, IIF mix-by-vintage matters for the loss profile.** The 2020-2021 vintages were originated at historically low note rates with significant subsequent home price appreciation, leaving them sticky (high persistency, low refinance turnover). The 2022-2024 vintages were originated at higher rates with less embedded equity and are now seasoning into the natural loss-emergence period (3-4 years post-origination per management commentary), making IIF mix-by-vintage a leading indicator of where loss content is concentrating (MTG_TRANSCRIPT_2025-12-31; NMIH_TRANSCRIPT_2025-12-31).

## Current state (as of 2025-12-31)

**Year-end 2025 primary IIF by MI** (direct primary, before reinsurance):

| MI | Primary IIF | YoY Change | Source |
|---|---|---|---|
| MGIC | $303.1B | +3% (industry-first $300B threshold crossed) | MTG_10-K_2025-12-31; MTG_TRANSCRIPT_2025-12-31 |
| Radian | $282.5B | up from $275.1B (+2.7%) | RDN_10-K_2025-12-31 |
| Enact | $273.1B | up from $268.8B (+2%) | ACT_10-K_2025-12-31 |
| Essent | $248.4B | up from $243.6B (+1.9%) | ESNT_10-K_2025-12-31 |
| NMI Holdings | $221.4B | up 5.4% YoY | NMIH_TRANSCRIPT_2025-12-31 |
| Arch (USMI) | "relatively flat year-over-year" | n/a | ACGL_TRANSCRIPT_2025-12-31 |

**Year-end 2025 primary RIF**:
- MGIC: $81.2 billion (MTG_10-K_2025-12-31).
- Radian: $74.7 billion (RDN_10-K_2025-12-31).
- Enact: $71.4 billion (ACT_10-K_2025-12-31).
- NMI Holdings: $59.3 billion (NMIH_10-K_2025-12-31).
- Essent: $56.5 billion (ESNT_10-K_2025-12-31).

**Industry context**: USMI reports nearly $1.4 trillion in mortgages guaranteed by the GSEs with private MI protection as of September 30, 2023 (INDUSTRY_USMI_RESILIENCY_2023-11, citing GSE 10-Q filings). Six-MI primary IIF totaled approximately $1.33 trillion at year-end 2025 (MGIC $303B + Radian $283B + Enact $273B + Essent $248B + NMI $221B = $1,328B, plus Arch USMI not separately broken out).

**Composition at year-end 2025**:
- **Single-premium policies as % of primary IIF**: Enact 9% (unchanged from YE 2024) (ACT_10-K_2025-12-31). At Essent, the 10-K does not separately disclose the single-premium share of primary IIF, but reports that monthly premium policies comprised 99% of NIW in both 2025 and 2024 (ESNT_10-K_2025-12-31). At NMI, monthly-paid premium products comprised approximately 93% of primary IIF at year-end 2025 (NMIH_10-K_2025-12-31).
- **Note-rate mix**: Approximately 50% of Radian's IIF carries a mortgage rate of 5.5% or lower; roughly 60% of Essent's IIF carries a note rate of 6% or lower; approximately 70% of Enact's IIF had mortgage rates below 6% as of year-end 2024 (RDN_TRANSCRIPT_2025-12-31; ESNT_TRANSCRIPT_2025-12-31; ACT_TRANSCRIPT_2024-12-31).
- **Credit quality**: Weighted-average original FICO scores of in-force books at YE 2025 are clustered around 746-747 (Enact 746, Essent 747); Arch's most recently disclosed weighted-average book FICO of 745 is from Q4 2024 commentary and is not updated in the YE 2025 sources (ACT_10-K_2025-12-31; ESNT_TRANSCRIPT_2025-12-31; ACGL_TRANSCRIPT_2024-12-31).
- **Vintage mix**: Most MIs report a balanced book by origination year. Enact's pre-2009 legacy books represent 2% of both primary IIF and primary RIF at YE 2025 (ACT_10-K_2025-12-31).
- **Geographic concentration**: Enact's largest state concentration is California at 12% of primary RIF; largest MSA is Phoenix, AZ at 3% of primary RIF (ACT_10-K_2025-12-31).

## How it has evolved

**Multi-year IIF trajectory** at the industry level reflects three regimes:

**2020-2021 (refinance churn)**: Historic-low mortgage rates drove a massive refinance wave that caused rapid turnover of IIF — borrowers refinanced out of existing MI coverage and into new policies. Persistency at MGIC fell to 60.7% in March 2021, the cyclical low (MTG_10-K_2024-12-31). High refinance turnover meant IIF was being re-written constantly.

**2022-2023 (lock-in / contraction)**: As the Federal Reserve raised rates sharply, refinance activity collapsed and persistency surged. New originations also declined, but the lock-in dominated — IIF grew slowly because borrowers stayed in place (MTG_10-K_2025-12-31).

**2024-2025 (steady growth)**: Persistency remained elevated (industry roughly 82-86% range at YE 2025) and NIW recovered modestly. IIF grew approximately 2-3% YoY across the major MIs through 2025. MGIC crossed $300 billion of IIF in 2025 — described by management as "an industry first," referring to the first U.S. mortgage insurer to surpass that threshold (MTG_TRANSCRIPT_2025-12-31).

**Forward**: Management commentary across the six MIs in Q4 2025 framed 2026 IIF growth as likely to remain modest. Per MGIC: "Consensus mortgage origination forecasts project the size of the MI market in 2026 will be relatively similar to 2025 ... we expect insurance in force to remain relatively flat in 2026" (MTG_TRANSCRIPT_2025-12-31). The path of mortgage rates is the principal swing factor: lower rates would lift refinance activity (reducing persistency), partially offset by larger origination volumes; higher rates would extend the lock-in but suppress NIW (MTG_TRANSCRIPT_2025-12-31; NMIH_TRANSCRIPT_2025-12-31).

## Sources

- [MTG_10-K_2025-12-31] — MGIC IIF definition (glossary), $303.1B YE 2025 primary IIF, $81.2B primary RIF, RIF definition, direct/primary terminology, the August 2024 references, IIF growth expectations.
- [MTG_TRANSCRIPT_2025-12-31] — $300B IIF "industry first" framing for MGIC; 2026 outlook for IIF "relatively flat."
- [RDN_10-K_2025-12-31] — Radian primary IIF $282.5B at YE 2025 (up from $275.1B at YE 2024); primary RIF $74.7B.
- [RDN_TRANSCRIPT_2025-12-31] — ~50% of Radian IIF at note rate ≤ 5.5%.
- [ACT_10-K_2025-12-31] — Enact IIF / RIF definitions; YE 2025 primary IIF $273.1B (vs. $268.8B YE 2024); the "10% persistency decline = $95M earned premium impact" sensitivity; weighted-average FICO 746 / LTV 93%; 9% single-premium share of primary IIF; 12% California / 3% Phoenix RIF concentration; legacy pre-2009 books 2% of IIF and RIF.
- [ACT_TRANSCRIPT_2024-12-31] — ~70% of Enact IIF had mortgage rates below 6% as of YE 2024.
- [ESNT_10-K_2025-12-31] — Essent YE 2025 IIF $248.4B (up from $243.6B); monthly premium policies comprised 99% of NIW in both 2025 and 2024 (the single-premium share of primary IIF is not separately disclosed).
- [ESNT_TRANSCRIPT_2025-12-31] — ~60% of Essent IIF at note rate ≤ 6%; weighted-average FICO 747.
- [NMIH_10-K_2025-12-31] — NIW definition (NIW occurs when a lender activates coverage); 2025 NIW $48.9B and YE 2025 IIF $221.4B.
- [NMIH_TRANSCRIPT_2025-12-31] — YE 2025 IIF $221.4B (+5.4% YoY); 2026 outlook commentary.
- [ACGL_TRANSCRIPT_2025-12-31] — Arch USMI IIF "relatively flat year-over-year"; weighted-average FICO 745 (per ACGL_TRANSCRIPT_2024-12-31).
- [ACGL_TRANSCRIPT_2024-12-31] — Arch USMI weighted-average FICO 745 cited in Q4 2024 commentary.
- [MTG_10-K_2024-12-31] — Cross-check for 60.7% persistency low at March 31, 2021.
- [INDUSTRY_USMI_RESILIENCY_2023-11] — Approximately $1.4 trillion in GSE-guaranteed mortgages with private MI protection (per GSE 10-Q filings, Sept 30, 2023).
- [INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09] — Cancellation framework (HOPA 78% / 80% rules).

## Related

- [[metrics/niw]]
- [[metrics/persistency]]
- [[metrics/loss_ratio]]
- [[topics/pmiers]]
- [[topics/crt_reinsurance]]
- [[topics/us_mortgage_market]]
