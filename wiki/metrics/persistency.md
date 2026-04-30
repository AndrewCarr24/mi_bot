# Persistency

> Persistency measures the percentage of insurance-in-force ("IIF") that remains in force after a twelve-month period — the complement of the run-off rate. It is a primary determinant of future earned premium (especially for monthly-premium policies, where higher persistency means more months of premium collection per policy) and is highly sensitive to mortgage interest rates, home price appreciation, and refinancing activity. Persistency rates across the six U.S. private mortgage insurers have been historically elevated since 2022 because high prevailing mortgage rates have suppressed refinance volumes — the so-called "lock-in effect." At year-end 2025, the industry persistency band ran from approximately 82% (Arch USMI Q4) to 85.7% (Essent), with most MIs in the 82-85% range. Persistency softened modestly from peak 2023 levels as rates eased through late 2024 and into 2025, but remains well above the historical lows seen during the 2020-2021 refinance boom (when MGIC reached 60.7% in March 2021) (MTG_10-K_2024-12-31).

## What it is

**Definition.** Per MGIC's glossary: "Annual Persistency: The percentage of our insurance remaining in force from one year prior" (MTG_10-K_2025-12-31). Other MIs use definitionally consistent language:

- **Enact**: "The percentage of our IIF that remains insured after taking into account annualized cancellations for the period presented is defined as our persistency rate" (ACT_10-K_2025-12-31).
- **Essent**: "Our annual persistency rate" — measured at year-end as the percentage of IIF that remained in force from one year prior (ESNT_10-K_2025-12-31).

When a borrower refinances, sells the home, or pays down the loan to the point where mortgage insurance is no longer required (typically at 78% LTV under the Homeowners Protection Act, or under the GSEs' broader cancellation guidelines), the policy is cancelled and the IIF is reduced (INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09; see [[topics/mi_regulatory_landscape]]). Persistency is the complement of the run-off rate — the percentage of IIF that leaves the book over a given period.

**Variants** that some MIs report:
- **Twelve-month persistency** — the percentage of IIF in place at the prior year-end that remains in force at the current measurement date. This is the standard reporting basis at MGIC, Enact, Essent, NMI Holdings, and (USMI persistency disclosure) Arch.
- **Quarterly-annualized persistency** — Radian reports both 12-month persistency and a quarterly-annualized figure. The quarterly-annualized number reacts faster to recent activity (a refinance pickup in one quarter compresses the QAP figure before it shows up in the 12-month figure).

**Mechanics — what changes persistency.** Per Enact's MD&A: "Recent elevated interest rates have increased persistency in the portfolio, but this impact is partially offset by lower NIW. Loan prepayment speeds and the relative mix of business between single premium policies and monthly premium policies also impact our profitability. Assuming all other factors remain constant over the life of the policies, prepayment speeds have an inverse impact on IIF and the expected premium from our monthly policies. Slower prepayment speeds, demonstrated by a higher persistency rate, result in IIF remaining in place, providing increased premium from monthly policies over time" (ACT_10-K_2025-12-31). The principal drivers of cancellations are:

- **Refinance activity**: Borrowers refinancing into a new mortgage cancel the existing MI policy. Refinance is the most rate-sensitive driver (RDN_TRANSCRIPT_2025-12-31).
- **Home sale**: Borrowers selling the home pay off the underlying loan.
- **Loan amortization to LTV cancellation thresholds**: HOPA mandates termination at 78% LTV (based on original property value); borrowers may also request cancellation at 80% LTV with a "good payment history" (INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09).
- **Claims paid / NPL settlements**: Loans that result in claim payments or commutation are removed from the in-force book.

## Why it matters

**First, persistency compounds into future revenue.** Most premiums earned in any given year come from policies written in prior years. For monthly-premium policies — which constitute the vast majority of recent NIW (e.g., 97% of MGIC's 2025 NIW) — higher persistency means more months of premium collection per policy and thus higher lifetime revenue (MTG_10-K_2025-12-31). Per Enact: a 10% decline in primary persistency on existing IIF would reduce earned premiums by approximately $95 million in the first full year, partially offset by higher policy cancellations in single-premium products (ACT_10-K_2025-12-31).

**Second, the persistency-vs-NIW trade-off depends on the rate environment.** When rates fall, refinance activity rises (compressing persistency) but origination volumes also rise (lifting NIW) — the two partially offset. When rates rise, the lock-in effect lifts persistency but suppresses NIW. Through 2024-2025, MIs have been operating in the high-persistency, low-NIW regime; management commentary across the six MIs in Q4 2025 expects this to continue absent a sharp rate move (MTG_TRANSCRIPT_2025-12-31; ESNT_TRANSCRIPT_2025-12-31).

**Third, persistency has a credit-quality dimension.** When refinance activity is high, borrowers with strong credit and significant home equity tend to refinance out of MI coverage, while riskier borrowers remain — potentially degrading the credit profile of the remaining IIF (MTG_10-K_2024-12-31). This adverse-selection dynamic means that periods of low persistency can be accompanied by a worsening of the in-force book's risk characteristics, while periods of high persistency (like the current cycle) preserve the credit profile of recent vintages.

**Fourth, single-premium policies are different.** For single-premium policies, where the premium is collected upfront and earned over the estimated life of the policy, higher-than-expected persistency can *reduce* profitability because the policy remains in force longer than assumed at pricing. (Conversely, for monthly-premium policies, higher persistency *increases* profitability.) Per Enact: "the profitability of our single premium business increases when persistency rates are lower" (ACT_10-K_2025-12-31).

## Current state (as of 2025-12-31)

**Year-end 2025 persistency by MI**:

| MI | Persistency | Basis | Source |
|---|---|---|---|
| Essent | 85.7% | 12-month annual | ESNT_TRANSCRIPT_2025-12-31; ESNT_10-K_2025-12-31 |
| MGIC | 85% | Annual | MTG_TRANSCRIPT_2025-12-31 |
| Radian | 83.6% | 12-month | RDN_10-K_2025-12-31 |
| NMI Holdings | 83.4% | 12-month | NMIH_TRANSCRIPT_2025-12-31 |
| Enact | 82% | Primary | ACT_10-K_2025-12-31 |
| Arch (USMI) | 81.8% | Q4 2025 | ACGL_TRANSCRIPT_2025-12-31 |
| Radian (quarterly-annualized) | 81.6% at YE 2025 (vs. 82.7% at YE 2024) | Quarterly | RDN_10-K_2025-12-31 |

**Year-over-year change**:
- Essent: 85.7% (2025) vs. 85.7% (2024) vs. 86.9% (2023) — flat 2025 vs. 2024 (ESNT_10-K_2025-12-31).
- MGIC: 85% at YE 2025; "elevated and stable throughout 2025" per management (MTG_TRANSCRIPT_2025-12-31).
- Enact: 82% (2025) vs. 83% (2024) vs. 85% (2023) — declined 1 point in 2025 (ACT_10-K_2025-12-31).
- NMI: 83.4% (Q4 2025) vs. 83.9% (Q3 2025) — declined 50 bps sequentially (NMIH_TRANSCRIPT_2025-12-31).
- Radian (quarterly-annualized): 81.6% at YE 2025 (vs. 82.7% at YE 2024) per the 10-K table; described in the transcript as "remained strong at 82% in the fourth quarter, a small decrease from the prior quarter due to higher refinance activity" (RDN_10-K_2025-12-31; RDN_TRANSCRIPT_2025-12-31).
- Arch (USMI): 81.8% in Q4 2025 (ACGL_TRANSCRIPT_2025-12-31).

**Driver: rate-volatility-induced refinance pickup**. Per Enact: "Our primary persistency rate decreased to 82% during 2025 compared to 83% during 2024. Persistency remains slightly elevated due to high interest rates but decreased in 2025 due to rate volatility throughout the year" (ACT_10-K_2025-12-31). Per Radian: the Q4 2025 quarterly-annualized rate was "a small decrease from the prior quarter due to higher refinance activity" (RDN_TRANSCRIPT_2025-12-31).

**Note-rate composition supporting durability of the lock-in effect**:
- Approximately 50% of Radian's IIF carries a mortgage rate of 5.5% or lower (RDN_TRANSCRIPT_2025-12-31).
- Roughly 60% of Essent's in-force portfolio has a note rate of 6% or lower (ESNT_TRANSCRIPT_2025-12-31).
- Approximately 70% of Enact's IIF had mortgage rates below 6% as of year-end 2024 (ACT_TRANSCRIPT_2024-12-31).

These note-rate distributions imply that persistency on the 2020-2022 vintages will remain elevated as long as mortgage rates stay above the underlying note rates on those loans.

**Refinance share of NIW (an inverse-persistency indicator)**: At MGIC, refinance-related NIW rose from 4% of NIW in 2024 to 9.1% in 2025 — visible evidence of the cycle beginning to soften the lock-in (MTG_10-K_2025-12-31).

## How it has evolved

**2020-2021 (cyclical low)**: Mortgage rates fell to historic lows during the COVID-19 monetary policy response, fueling a refinance wave. MGIC's persistency reached its decade low of **60.7%** at March 31, 2021, with the industry experiencing rapid IIF turnover (MTG_10-K_2024-12-31).

**2022-2023 (lock-in build-up)**: As the Federal Reserve raised rates sharply, refinance activity collapsed and persistency surged. MGIC's persistency reached its cyclical high of **86.3% at September 30, 2023** (MTG_10-K_2024-12-31). Year-end 2023 persistency was elevated across the industry (Essent 86.9%, Enact 85%) (ESNT_10-K_2025-12-31; ACT_10-K_2025-12-31).

**2024 (peak / plateau)**: Persistency held in the 82-87% range across the six MIs. Year-end 2024 figures: Essent 85.7%, Enact 83%, NMI 84.6% (NMIH_10-K_2025-12-31), Arch USMI ~82-83% (ACGL_TRANSCRIPT_2024-12-31). Industry context: the elevated persistency environment was driven by high mortgage rates suppressing refinance volumes, with little change quarter-to-quarter.

**2025 (modest softening)**: Federal Reserve rate moves in late 2024 and rate volatility through 2025 spurred incremental refinance activity. Persistency declined modestly across most MIs (1-2 points YoY). The sharpest visible movement was in the quarterly-annualized rates, which react faster than 12-month persistency to refinance pickups: Radian's quarterly-annualized persistency was 81.6% at YE 2025 vs. 82.7% at YE 2024 (a 1.1-point YoY decline), even though Radian's 12-month persistency held flat at 83.6% (RDN_10-K_2025-12-31). Refinance share of NIW more than doubled at MGIC (from 4% in 2024 to 9.1% in 2025) (MTG_10-K_2025-12-31).

**Forward**: Persistency is the most rate-sensitive metric in the MI book. NMI's framing in Q4 2025: "we do expect persistency is well above historical trends and continues notwithstanding the 50 basis point decrease last quarter to be well above trends. So we do expect as we go through time that that will come down more in line with historical norm" (NMIH_TRANSCRIPT_2025-12-31). The pace of normalization will depend on mortgage rates and the stickiness of the 2020-2022 vintages with low note rates.

## Sources

- [MTG_10-K_2025-12-31] — MGIC Annual Persistency definition (glossary); 2025 NIW share monthly premium (~97%) for context.
- [MTG_TRANSCRIPT_2025-12-31] — MGIC YE 2025 persistency at 85% / "elevated and stable throughout 2025"; refinance share of NIW (4% → 9.1% from 2024 to 2025).
- [MTG_10-K_2024-12-31] — Historical range since 2018: 60.7% low at March 31, 2021; 86.3% high at September 30, 2023; HOPA framework discussion; adverse-selection dynamic in low-persistency periods.
- [RDN_10-K_2025-12-31] — Radian's 12-month persistency at YE 2025 (83.6%) and YE 2024 (83.6%); discussion of persistency-rate framework.
- [RDN_TRANSCRIPT_2025-12-31] — Q4 2025 quarterly persistency rate "remained strong at 82% in the fourth quarter, a small decrease from the prior quarter due to higher refinance activity"; ~50% of Radian IIF at note rate ≤ 5.5%.
- [ACT_10-K_2025-12-31] — Enact persistency definition (annualized cancellation framework); 2025 / 2024 / 2023 figures (82% / 83% / 85%); the rate-volatility framing for the 2025 decline; the "10% persistency decline = $95M earned premium" sensitivity; single-premium-vs-monthly-premium dynamics (line on lower persistency increasing single-premium profitability).
- [ACT_TRANSCRIPT_2024-12-31] — Approximately 70% of Enact IIF had mortgage rates below 6% as of YE 2024.
- [ESNT_10-K_2025-12-31] — Essent annual persistency rate (85.7% / 85.7% / 86.9% for 2025 / 2024 / 2023); persistency definition framing.
- [ESNT_TRANSCRIPT_2025-12-31] — ~60% of Essent IIF at note rate ≤ 6%; YE 2025 persistency 85.7%.
- [NMIH_10-K_2025-12-31] — NMI persistency framework; 2024 persistency 84.6%.
- [NMIH_TRANSCRIPT_2025-12-31] — NMI Q4 2025 persistency 83.4% (vs. 83.9% in Q3); rate-volatility framing for the decline; persistency-vs-historical-norm commentary.
- [ACGL_TRANSCRIPT_2025-12-31] — Arch USMI Q4 2025 persistency 81.8%.
- [ACGL_TRANSCRIPT_2024-12-31] — Arch USMI Q4 2024 persistency context.
- [INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09] — HOPA cancellation framework (78% automatic, 80% upon borrower request).

## Related

- [[metrics/iif]]
- [[metrics/niw]]
- [[metrics/loss_ratio]]
- [[topics/us_mortgage_market]]
- [[topics/mi_regulatory_landscape]]
