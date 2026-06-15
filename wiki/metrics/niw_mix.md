# NIW Mix (FICO / LTV / Purchase-vs-Refinance)

> Each MI discloses the composition of its new insurance written — by borrower FICO score, by loan-to-value ratio, and by purchase vs. refinance — but in different documents and with different bin structures. This page harmonizes those disclosures into common bins for fiscal years 2021-2025 across the six MIs. Headline pattern: credit quality has tightened cohort-wide (average ≥740 FICO share rose from ~62% of NIW in 2021 to ~70% in 2025), Arch consistently writes the cleanest book (76.7% ≥740 in 2025), Enact carries the highest <680 share every year (6.0-7.3%), and the purchase share collapsed-then-recovered with the rate cycle (refis fell from ~12-20% of NIW in 2021 to 1-5% in 2022-2024, rebounding to 8-13% in 2025) (MTG_10-K_2025-12-31; RDN_10-K_2025-12-31; ESNT_8-K_2026-02-13; NMIH_8-K_2026-02-10; ACT_10-K_2025-12-31; ACGL_10-K_2025-12-31).

## What it is

**Definition.** NIW mix tables break a period's new insurance written into shares by risk attribute, measured at loan origination: borrower FICO score (lowest borrower's decision score, per MGIC's convention — MTG_10-K_2025-12-31), original LTV ratio, and loan purpose (purchase vs. refinance).

**Where each MI discloses it.** This varies and is a common source of confusion:

| MI | NIW mix tables in 10-K? | In earnings 8-K supplements? |
|---|---|---|
| MGIC (MTG) | Yes (full tables) | Summary lines only (FICO<680 share, >95% LTV share) |
| Radian (RDN) | Yes | Yes |
| Essent (ESNT) | No — 10-K has portfolio (IIF/RIF) FICO tables only | Yes (only NIW-mix source) |
| NMI (NMIH) | Yes | Yes |
| Enact (ACT) | Yes (full tables) | No |
| Arch (ACGL) | Only from FY2024 onward | Yes (only source for FY2023 and earlier) |

**Bin harmonization.** Native bins differ (MGIC and Enact publish 8-9 FICO bins; Radian and Arch publish 4; Essent and NMI publish 6 with a lumped ≤679 bottom bucket). The lowest common denominator across all six is three FICO bins (≥740 / 680-739 / <680) and four LTV bins (>95% / 90.01-95% / 85.01-90% / ≤85%). One caveat: MGIC's bottom LTV bin is "80.01-85%" rather than "≤85%" — its NIW below 80% LTV is not disclosed but is ≤0.5% based on the parallel RIF table (MTG_10-K_2025-12-31), so the bins are treated as comparable.

## Why it matters

**First, NIW mix is the leading indicator of future loss content.** Loans with FICO <680, LTV >95%, or DTI >45% carry materially higher claim probabilities (MTG_10-K_2025-12-31). A shift in mix precedes a shift in loss ratio by the 3-6 year loss-emergence window.

**Second, mix differences explain pricing and PMIERs differences across the cohort.** PMIERs Minimum Required Assets are calculated from grids keyed to original LTV and credit score (INDUSTRY_PMIERS_2.0_BASE), so an MI writing more <680 / >95% LTV business holds proportionally more capital per dollar of risk.

**Third, the purchase/refi split tracks the rate cycle and affects persistency.** Refinance-heavy NIW (2020-2021) churns the book and depresses persistency; purchase-dominated NIW (2022-2024, >95% purchase at most MIs) extends policy life. The 2025 uptick in refi share (8-13%) is the first sign of the cycle turning (per the FY2025 10-Ks cited below).

## Current state (as of 2025-12-31)

**Share of FY NIW from borrowers with FICO ≥740 (%):**

| MI | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| MGIC (MTG) | 63.1 | 61.6 | 68.2 | 68.3 | 69.1 |
| Radian (RDN) | 58.6 | 59.8 | 65.4 | 69.6 | 66.1 |
| Essent (ESNT) | 57.2 | 58.1 | 58.2 | 61.4 | 67.6 |
| NMI (NMIH) | 65.8 | 64.0 | 73.5 | 71.5 | 72.1 |
| Enact (ACT) | 59.2 | 62.4 | 63.4 | 64.6 | 67.0 |
| Arch (ACGL) | 65.2 | 66.4 | 65.5 | 70.2 | 76.7 |

**Share of FY NIW from borrowers with FICO <680 (%):**

| MI | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| MGIC (MTG) | 4.8 | 5.3 | 4.2 | 3.9 | 4.1 |
| Radian (RDN) | 7.2 | 7.8 | 5.7 | 5.3 | 4.8 |
| Essent (ESNT) | 5.3 | 3.7 | 3.2 | 5.0 | 4.5 |
| NMI (NMIH) | 2.9 | 3.0 | 1.1 | 2.3 | 3.3 |
| Enact (ACT) | 7.3 | 6.3 | 6.3 | 6.1 | 6.0 |
| Arch (ACGL) | 3.9 | 2.7 | 2.7 | 3.4 | 2.5 |

(The middle bin, 680-739, is 100 minus the two shares above.)

**Share of FY NIW with LTV above 95% (%):**

| MI | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| MGIC (MTG) | 10.8 | 12.3 | 12.2 | 13.7 | 14.7 |
| Radian (RDN) | 12.0 | 16.6 | 16.9 | 16.1 | 16.6 |
| Essent (ESNT) | 13.5 | 10.7 | 17.6 | 18.8 | 14.5 |
| NMI (NMIH) | 9.5 | 8.9 | 9.2 | 12.8 | 12.0 |
| Enact (ACT) | 12.4 | 14.3 | 17.5 | 19.9 | 18.6 |
| Arch (ACGL) | 5.8 | 5.3 | 5.9 | 7.4 | 7.0 |

**Full LTV mix, FY2025 (%):**

| MI | >95% | 90.01-95% | 85.01-90% | ≤85% |
|---|---|---|---|---|
| MGIC (MTG) | 14.7 | 46.2 | 28.6 | 10.5 |
| Radian (RDN) | 16.6 | 44.3 | 30.2 | 9.0 |
| Essent (ESNT) | 14.5 | 50.6 | 25.4 | 9.5 |
| NMI (NMIH) | 12.0 | 44.0 | 31.3 | 12.6 |
| Enact (ACT) | 18.6 | 36.6 | 30.0 | 14.9 |
| Arch (ACGL) | 7.0 | 44.3 | 33.9 | 14.8 |

**Purchase share of FY NIW (%; refinance share = 100 minus value):**

| MI | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| MGIC (MTG) | 79.7 | 97.4 | 98.2 | 96.0 | 90.9 |
| Radian (RDN) | 80.5 | 96.1 | 98.5 | 95.3 | 92.1 |
| Essent (ESNT) | 82.1 | 97.6 | 98.8 | 95.0 | 87.2 |
| NMI (NMIH) | 82.2 | 97.1 | 97.9 | 95.4 | 91.8 |
| Enact (ACT) | 79.3 | 95.5 | 97.4 | 93.5 | 89.7 |
| Arch (ACGL) | 87.4 | 97.5 | 98.4 | 96.9 | 91.1 |

**Derivation notes (important for verification):**
- ACGL 2021 and 2022 full-year figures are dollar-weighted sums of the quarterly columns in the Q4 earnings 8-K supplements (ACGL_8-K_2022-02-09 for FY2021; ACGL_8-K_2023-02-13 for FY2022) — Arch did not publish FY NIW mix in its 10-K before FY2024.
- RDN 2025 FICO and LTV shares are dollar-weighted from the quarterly shares and quarterly NIW totals in the Q4 2025 8-K (RDN_8-K_2026-02-18); Radian's 8-K publishes quarterly shares only. RDN 2025 purchase/refi is direct from the 10-K (RDN_10-K_2025-12-31).
- MGIC FICO shares here aggregate MGIC's native 8-bin table into the 3-bin structure (e.g., 2025: 51.7% [760+] + 17.4% [740-759] = 69.1% ≥740) (MTG_10-K_2025-12-31).
- Essent's bottom FICO bucket is disclosed as "≤679", treated as identical to "<680" (FICO scores are integers).

## How it has evolved

**2021 (refi-heavy, looser mix):** Refinances were 12-20% of NIW across the cohort as rates sat near historic lows. Credit mix was the loosest of the period — cohort-average ≥740 share of ~62%, with Essent and Radian below 59% (ESNT_8-K_2023-02-10; RDN_10-K_2023-12-31).

**2022 (purchase pivot):** As rates rose, refis collapsed to 2-5% of NIW everywhere. Mix stayed roughly flat-to-looser at MGIC/RDN/ESNT (MTG <680 peaked at 5.3%, RDN at 7.8%) (MTG_10-K_2023-12-31; RDN_10-K_2024-12-31).

**2023-2024 (tightening into the smaller market):** With origination volumes roughly halved, every MI's ≥740 share rose — most sharply NMI (64.0% → 73.5% in 2023) and Radian (59.8% → 69.6% by 2024). Meanwhile >95% LTV share drifted UP at most MIs (affordability pressure pushing borrowers to higher LTVs), a notable divergence: credit scores tightened while LTVs loosened (NMIH_10-K_2024-12-31; RDN_10-K_2024-12-31; ACT_10-K_2024-12-31).

**2025 (cleanest book of the period; refis return):** Cohort-average ≥740 share reached ~70%. Arch hit 76.7% — a 10+ point cleanup from 2021. Refi share rebounded to 8-13% as rates eased, the first material refi contribution since 2021 (all six FY2025 10-Ks / Q4 2025 8-Ks as cited in the tables).

## Sources

- [MTG_10-K_2021-12-31] — MGIC FY2021 NIW by FICO / LTV / type-of-mortgage tables.
- [MTG_10-K_2023-12-31] — MGIC FY2022 (prior-year columns) FICO / LTV / purchase-refi.
- [MTG_10-K_2024-12-31] — MGIC FY2023 figures.
- [MTG_10-K_2025-12-31] — MGIC FY2024-FY2025 figures; decision-FICO convention; RIF <80% LTV ~0.2-0.3% (bin-comparability caveat); high-risk-attribute discussion.
- [RDN_10-K_2023-12-31] — Radian FY2021 (3-year table).
- [RDN_10-K_2024-12-31] — Radian FY2022-FY2024 FICO / LTV.
- [RDN_10-K_2025-12-31] — Radian FY2024-FY2025 purchase/refi.
- [RDN_8-K_2026-02-18] — Radian Q4 2025 supplement; quarterly FICO/LTV shares and NIW dollars used for the FY2025 weighted shares.
- [ESNT_8-K_2023-02-10] — Essent FY2021-FY2022 NIW by credit score / LTV / purchase-refi (year-ended columns).
- [ESNT_8-K_2024-02-09] — Essent FY2022-FY2023 LTV.
- [ESNT_8-K_2025-02-14] — Essent FY2023-FY2024 credit score / LTV.
- [ESNT_8-K_2026-02-13] — Essent FY2024-FY2025 credit score / LTV / purchase-refi.
- [NMIH_10-K_2023-12-31] — NMI FY2021-FY2022 (3-year tables).
- [NMIH_10-K_2024-12-31] — NMI FY2022-FY2024.
- [NMIH_8-K_2026-02-10] — NMI FY2025 FICO / LTV / purchase-refi.
- [ACT_10-K_2023-12-31] — Enact FY2021-FY2022 (3-year tables, dollar amounts).
- [ACT_10-K_2024-12-31] — Enact FY2022-FY2024.
- [ACT_10-K_2025-12-31] — Enact FY2024-FY2025.
- [ACGL_8-K_2022-02-09] — Arch Q4 2021 supplement; quarterly NIW by credit quality / LTV summed for FY2021.
- [ACGL_8-K_2023-02-13] — Arch Q4 2022 supplement; quarterly columns summed for FY2022.
- [ACGL_10-K_2024-12-31] — Arch FY2023-FY2024 NIW by credit quality / LTV.
- [ACGL_10-K_2025-12-31] — Arch FY2024-FY2025.
- [INDUSTRY_PMIERS_2.0_BASE] — PMIERs required-asset grids keyed to LTV and credit score.

## Related

- [[metrics/niw]]
- [[metrics/iif]]
- [[metrics/loss_ratio]]
- [[metrics/persistency]]
- [[topics/pmiers]]
