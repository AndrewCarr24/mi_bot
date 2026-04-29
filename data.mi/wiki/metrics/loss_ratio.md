# Loss Ratio (MI-specific)

> The loss ratio is the fundamental measure of underwriting profitability in mortgage insurance, calculated as losses incurred (net of reinsurance) divided by net premiums earned. Unlike standard P&C insurance, MI loss ratios are frequently negative in benign credit environments due to the mechanics of case reserve estimation and favorable reserve development. The metric is highly sensitive to macroeconomic conditions, home price appreciation, and the aging of the delinquency inventory, making it a key barometer of credit cycle positioning for the six MIs.

## What it is

In mortgage insurance, the loss ratio is defined as the provision for losses (losses incurred, net of reinsurance) expressed as a percentage of net premiums earned. For example, Radian reports its loss ratio as "provision for losses expressed as a percentage of net premiums earned" for its Mortgage Insurance segment (RDN_10-K_2024-12-31). MGIC similarly calculates the loss ratio as "the ratio, expressed as a percentage, of the sum of losses incurred, net to net premiums earned" (MTG_10-K_2024-12-31).

The mechanics of loss reserving in MI differ materially from standard P&C insurance. MIs establish case reserves only when a loan becomes delinquent (typically two or more payments past due) and has not cured or resulted in a claim (MTG_10-K_2024-12-31). Reserves are estimated using two key assumptions: the **claim rate** (what percentage of delinquent loans will result in a claim payment) and **claim severity** (the expected dollar amount of that claim). IBNR (incurred but not reported) reserves are also established for delinquencies estimated to have occurred but not yet reported to the insurer (MTG_10-K_2024-12-31).

Losses incurred each period consist of two components: losses on new delinquency notices received in the current period, and the **re-estimation** of reserves on delinquencies carried over from prior periods. This re-estimation — known as reserve development — can be either favorable (reserves released) or adverse (reserves strengthened).

## Why it matters

The loss ratio is the primary lens through which analysts assess an MI's underwriting performance and credit cycle positioning. Several features make it especially important:

- **Negative loss ratios are normal in benign environments.** When favorable reserve development on prior-year delinquencies exceeds losses on new notices, the loss ratio turns negative. This is not a sign of accounting error but reflects the fact that MIs initially reserve conservatively on new delinquencies and subsequently release reserves as loans cure or as claim rate assumptions improve. MGIC reported a loss ratio of (1.5)% for 2024 and (2.2)% for 2023 (MTG_10-K_2024-12-31). Radian reported (0.2)% for 2024 and (4.6)% for 2023 (RDN_10-K_2024-12-31).

- **High sensitivity to home prices.** Favorable development is heavily driven by home price appreciation, which allows delinquent borrowers to cure through property sales (MTG_10-K_2024-12-31). A sustained downturn in home prices would reverse this dynamic, causing adverse development.

- **Vintage-level loss ratios reveal underwriting quality.** Radian discloses cumulative incurred loss ratios by origination vintage, showing how different underwriting years perform over time. For example, the COVID-affected 2020 vintage shows elevated cumulative loss ratios (25.6% at Dec 2020) that subsequently declined as home prices rose (RDN_10-K_2024-12-31).

- **Small changes in assumptions have outsized impact.** MGIC notes that a one percentage point change in the average claim rate reserve factor would change loss reserves by approximately ±$18 million, and a $1,000 change in average severity would change reserves by ±$7 million (MTG_10-K_2024-12-31).

## Current state (as of 2024-12-31)

Based on the most recent annual filings, the dispersion across MIs is wide — from Arch and MGIC at deeply negative loss ratios to Essent at single-digit positive:

| MI | Loss Ratio (2024) | Loss Ratio (2023) | Loss Ratio (2022) | Source |
|---|---|---|---|---|
| Arch (mortgage segment) | (4.4)% | (8.9)% | n/a | ACGL_10-K_2024-12-31 |
| MGIC | (1.5)% | (2.2)% | n/a | MTG_10-K_2024-12-31 |
| Radian | (0.2)% | (4.6)% | (35.5)% | RDN_10-K_2024-12-31 |
| Enact | 4% | 3% | (10)% | ACT_10-K_2024-12-31 |
| Essent | 8.1% | 3.4% | (20.7)% | ESNT_10-K_2024-12-31 |

Note: NMIH's loss ratio is calculated on a different basis (its 10-K does not surface a comparable single percentage; insurance claims and claim expenses were $31.5M in 2024 vs. $602.2M in net premiums earned for 2025, suggesting a positive but low single-digit ratio).

Several patterns are visible. First, the dispersion comes from how aggressively each MI has reserved for the seasoning 2022-2023 vintages and how quickly favorable prior-period development has been recognized. Second, Radian's 2022 loss ratio of (35.5)% was exceptionally negative, reflecting very large favorable reserve development as COVID-era delinquencies cured at rates far exceeding initial expectations (RDN_10-K_2024-12-31). Third, the narrowing of loss ratios from 2023 to 2024 across all MIs reflects the normalization of the delinquency inventory as the COVID book ages and new notices on more recent vintages begin to contribute meaningfully to losses incurred — visible most clearly at Essent (3.4% → 8.1%) and Enact (3% → 4%).

For MGIC in 2024, new delinquency notices added $197.6 million to losses incurred, while re-estimation of prior-year reserves produced $212.5 million of favorable development, resulting in net negative losses incurred of $(14.9) million (MTG_10-K_2024-12-31). The favorable development was "primarily result[ing] from a decrease in the expected claim rate on previously received delinquencies" as home price appreciation allowed borrowers to cure through sale (MTG_10-K_2024-12-31).

## How it has evolved

The loss ratio trajectory across the six MIs over 2022-2024 reflects the unwinding of COVID-era reserving. In 2020-2021, MIs established large case reserves as delinquencies spiked. As home prices surged and forbearance programs facilitated cures, those reserves proved excessive and were released over subsequent years, producing deeply negative loss ratios in 2022. By 2024, the favorable development has moderated as the COVID-related delinquency inventory has largely been resolved, and new notices on more recent vintages (2022-2024) are contributing a growing share of losses incurred.

The cumulative incurred loss ratio by vintage data from Radian illustrates this pattern clearly: the 2020 vintage peaked at 25.6% in December 2020 and has since declined to 3.1% by December 2024, while the 2022 vintage has risen from 9.4% to 17.0% over the same period (RDN_10-K_2024-12-31). This reflects the maturation of more recent vintages as they season and experience defaults.

## Sources

- [MTG_10-K_2024-12-31] — Provided detailed explanation of loss reserve methodology, the composition of losses incurred (new notices vs. prior-year development), and MGIC's loss ratio of (1.5)% for 2024.
- [RDN_10-K_2024-12-31] — Provided Radian's loss ratio definition, segment-level loss ratios for 2022-2024, and cumulative incurred loss ratio by vintage table.
- [INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09] — Provided background on MI claim mechanics and the percentage option for claim payment calculation.

## Related

- [[metrics/iif]]
- [[topics/catastrophe_impact_on_mi]]