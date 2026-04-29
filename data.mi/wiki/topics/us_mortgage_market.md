# The US Mortgage Market and MI Penetration

> The US mortgage market is the primary demand driver for private mortgage insurance (MI), which is required on conventional loans with loan-to-value (LTV) ratios above 80% that are purchased by Fannie Mae and Freddie Mac. MI penetration in the high-LTV segment is near-universal for GSE-eligible loans, making the industry's fortunes closely tied to origination volumes in the low-down-payment channel. The market is cyclical, sensitive to interest rates, and structurally shaped by GSE charters, FHFA oversight, and the competitive position of MI versus FHA insurance.

## What it is

The US mortgage origination market consists of loans originated by banks, credit unions, and non-bank lenders, which are either held in portfolio, securitized through Ginnie Mae (for government-backed loans), or sold to Fannie Mae and Freddie Mac (the GSEs) for securitization. Private mortgage insurance attaches to conventional loans with LTV ratios exceeding 80% that are sold to the GSEs — Freddie Mac's charter requires credit enhancement for any loan above 80% LTV, and MI is the most commonly used form (INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09). Standard MI coverage requirements range from 6% for loans at 80.01-85% LTV up to 35% for loans above 95% LTV, with the coverage percentage applied to the claim amount in the event of default (INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09).

MI penetration in the high-LTV conventional channel is effectively universal — nearly 60% of purchased loans with private MI went to first-time homebuyers in 2019, and more than 40% had annual incomes below $75,000 (INDUSTRY_USMI_WHITE_PAPER_2020-10). The alternative for low-down-payment borrowers is FHA insurance, which carries different pricing, underwriting, and premium structures. The MI industry's addressable market is therefore the subset of low-down-payment borrowers who choose or qualify for conventional (GSE-eligible) financing rather than FHA.

## Why it matters

For MI analysts, the mortgage market is the top-line driver. New insurance written (NIW) — the industry's primary volume metric — is a function of total conventional origination volume multiplied by the share of loans with LTV > 80%. When mortgage rates rise, refinance activity collapses and purchase originations slow, compressing NIW across all six MIs. When rates fall, refinance waves can temporarily boost NIW, though the duration of MI coverage on refinanced loans is shorter.

The cyclical nature of the business has driven the industry's transformation from a "buy-and-hold" model to an "aggregate-manage-distribute" model, where MIs actively transfer credit risk through reinsurance and insurance-linked notes (ILNs) to reduce earnings volatility through housing cycles (INDUSTRY_USMI_WHITE_PAPER_2020-10). This transformation, combined with risk-based pricing and PMIERs capital standards, has made the industry more resilient — but the fundamental sensitivity to origination volumes remains.

## Current state (as of 2024-12-31)

The US mortgage market in 2024 remained in a high-rate environment that depressed origination volumes. Fannie Mae's single-family conventional acquisition volume was $326.0 billion in 2024, up marginally from $316.0 billion in 2023, while Freddie Mac's was $346.4 billion, a 15.5% increase from 2023 (INDUSTRY_FHFA_ANNUAL_REPORT_2024). Despite the modest recovery, volumes remained well below the 2020-2021 refinance boom levels. Elevated interest rates continued to suppress both home purchase and refinance activity, and house price appreciation slowed (INDUSTRY_FHFA_ANNUAL_REPORT_2024).

The GSEs' combined single-family acquisition volume of roughly $672 billion in 2024 represents the primary pool from which MI NIW is drawn. With MI penetration in the high-LTV segment near-universal for GSE loans, the industry's NIW is largely a function of this volume and the mix of LTV buckets within it.

## How it has evolved

The MI industry has undergone a fundamental transformation since the 2008 financial crisis. Pre-crisis, MIs operated with exposure-based statutory capital, published rate cards with broad LTV-based pricing, and a "buy-and-hold" approach that left them fully exposed to housing downturns (INDUSTRY_USMI_WHITE_PAPER_2020-10). Post-crisis reforms — including the implementation of PMIERs risk-based capital standards, the Qualified Mortgage (QM) rule, enhanced GSE representation and warranty frameworks, and the widespread adoption of credit risk transfer (CRT) — have created a more resilient industry (INDUSTRY_USMI_WHITE_PAPER_2020-10).

The industry has also shifted from a historical 10-15% non-delegated underwriting rate to significantly more direct diligence on loan quality, and has adopted rescission relief principles that give lenders certainty about MI coverage from day one (INDUSTRY_USMI_WHITE_PAPER_2020-10). As of October 2020, MIs had transferred nearly $41.4 billion in risk on approximately $1.8 trillion of insurance-in-force since 2015 through a combination of quota share reinsurance, excess-of-loss transactions, and ILN issuances (INDUSTRY_USMI_WHITE_PAPER_2020-10).

The most recent regulatory evolution came in August 2024, when the GSEs issued updates to PMIERs that more precisely differentiate asset requirements based on credit rating granularity and bond liquidity, and establish limits on assets backed by residential mortgages and commercial real estate (INDUSTRY_FHFA_ANNUAL_REPORT_2024). These updates have a 24-month phase-in period with full effectiveness by September 30, 2026.

## Sources

- INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09 — Provided the GSE charter requirement for MI on loans above 80% LTV, standard coverage requirements by LTV bucket, and the mechanics of MI claim payments.
- INDUSTRY_USMI_WHITE_PAPER_2020-10 — Described the industry's transformation from buy-and-hold to aggregate-manage-distribute, the adoption of CRT, post-crisis regulatory enhancements, and borrower demographics for MI users.
- INDUSTRY_FHFA_ANNUAL_REPORT_2024 — Provided 2024 GSE acquisition volumes, the high-rate environment context, and details on the August 2024 PMIERs update.

## Related

- [[metrics/niw]]
- [[metrics/iif]]
- [[topics/mi_regulatory_landscape]]