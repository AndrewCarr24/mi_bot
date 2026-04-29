# PMIERs (Private Mortgage Insurer Eligibility Requirements)

> PMIERs are the financial and operational requirements that private mortgage insurers must meet to be approved by Fannie Mae and Freddie Mac to insure mortgages. The framework centers on a quarterly comparison of an insurer's available assets against its minimum required assets, which is calculated as a risk-weighted percentage of its risk-in-force. A sufficiency ratio above 100% indicates compliance. The August 2024 update (Guidance 2024-01) introduced new haircuts, exclusions, and concentration limits on the available-assets side, addressing the risk that insurers' own investment portfolios could lose value during a stress event. PMIERs are the single most important regulatory constraint on MI capital management and directly influence dividend capacity, new business appetite, and reinsurance strategy.

## What it is

PMIERs establish the conditions under which a private mortgage insurer can be an "approved insurer" eligible to write coverage on loans acquired by Fannie Mae and Freddie Mac. The core financial test is a risk-based evaluation performed each quarter: an insurer must maintain **available assets** that equal or exceed its **minimum required assets** (INDUSTRY_PMIERS_2.0_BASE).

**Available assets** are the most liquid assets on the insurer's statutory balance sheet — cash, bonds, publicly traded equities, certain receivables, and assets held by exclusive affiliated reinsurers. The calculation subtracts unearned premium reserves, outstanding debt obligations, and pledged collateral. Under the PMIERs 2.0 base, equities were discounted 25% (INDUSTRY_PMIERS_2.0_BASE); the August 2024 update doubled that haircut to 50% effective March 31, 2025, with bond-level haircuts and concentration limits introduced for the first time (INDUSTRY_PMIERS_GUIDANCE_2024-01).

**Minimum required assets** are derived from the insurer's risk-in-force (RIF) — the sum of each insured loan's current principal balance multiplied by the applicable coverage percentage. The RIF is then weighted by risk attributes (loan-to-value ratio, credit score, loan purpose, occupancy type, etc.) using factors specified in Exhibit A of the PMIERs document (INDUSTRY_PMIERS_2.0_BASE).

The **sufficiency ratio** is available assets divided by minimum required assets. A ratio below 100% constitutes an available assets shortfall, triggering mandatory notification to the GSEs and potential remediation actions including new business restrictions, capital infusion requirements, or suspension of approval status (INDUSTRY_PMIERS_2.0_BASE).

Beyond the financial test, PMIERs also mandate quality control programs, underwriting standards, quarterly operational performance scorecards, and extensive reporting requirements (INDUSTRY_PMIERS_OVERVIEW_FHFA).

## Why it matters

PMIERs are the binding capital constraint for every MI. Unlike statutory risk-based capital (RBC) requirements imposed by state insurance regulators, PMIERs are set by the GSEs under FHFA oversight and are specifically calibrated to mortgage insurance risk. Analysts watch PMIERs sufficiency ratios as the primary indicator of an MI's financial strength and regulatory headroom.

A high sufficiency ratio (typically 150%+ for well-capitalized MIs) signals capacity to write new business, pay dividends to the parent holding company, and absorb losses without breaching the 100% floor. A declining ratio — whether from adverse loss development, investment portfolio losses, or aggressive new business growth — can constrain dividend payments and force the insurer to seek capital or reduce exposure.

The August 2024 update (Guidance 2024-01) is particularly significant because it introduces, for the first time, explicit haircuts on the available-assets side. Previously, PMIERs only addressed the liability side (required assets based on insured risk). The new rules apply haircuts to bond portfolios based on credit rating, impose concentration limits, and exclude certain asset types — effectively raising the bar for what counts as "available" and reducing reported sufficiency ratios for insurers with lower-quality or concentrated investment portfolios (INDUSTRY_PMIERS_GUIDANCE_2024-01).

## Current state (as of 2025-03-31)

Guidance 2024-01 became effective March 31, 2025, with a phased transition schedule for the new available-asset requirements. Key provisions include:

- **Bond haircuts**: A sliding scale based on credit rating — 0.20% for AAA, 0.60% for AA, 1.30% for A, 2.10% for BBB, 10% for BB (with a 5-year max remaining term), 25% for B (with a 2-year max remaining term), and 100% for CCC and below. Securities backed by the full faith and credit of the U.S. Government receive a 0% haircut. Sub-investment-grade bonds remain eligible but are subject to the aggregate cap below (INDUSTRY_PMIERS_GUIDANCE_2024-01).
- **Concentration limits**: Total Freddie Mac and Fannie Mae debt and MBS combined may not exceed 25% of available assets; ABS may not exceed 20%; non-agency CMBS rated at least BBB- may not exceed 5%. The aggregate of common and preferred shares plus BB-rated and B-rated bonds may not exceed 5% of available assets. Approved insurers must also set and disclose their own concentration limits for any single non-U.S.-Government issuer (INDUSTRY_PMIERS_GUIDANCE_2024-01).
- **COLI limit**: Corporate-owned life insurance assets are capped at 10% of the insurer's risk-based required asset amount (INDUSTRY_PMIERS_GUIDANCE_2024-01).
- **Surplus notes**: Eligible surplus notes are limited to 9% of minimum required assets; amounts above that threshold are excluded from available assets (INDUSTRY_PMIERS_GUIDANCE_2024-01).

All six MIs reported sufficiency ratios well above 100% in their most recent quarterly filings, though the full impact of the new haircuts will be reflected in Q1 2025 statutory filings due in May 2025.

## How it has evolved

PMIERs were first introduced in draft form by FHFA in July 2014, following the financial crisis and the GSE conservatorship. The draft framework was designed to replace the prior patchwork of GSE-specific eligibility requirements with a unified, risk-based standard (INDUSTRY_PMIERS_OVERVIEW_FHFA).

The final PMIERs 2.0 framework took effect March 31, 2019, after a transition period that gave insurers up to two years to achieve full compliance. The 2019 version established the available-assets vs. required-assets framework that remains in place today, along with the operational scorecard, quality control requirements, and reporting obligations (INDUSTRY_PMIERS_2.0_BASE).

The August 2024 update (Guidance 2024-01) represents the most significant revision since 2019. It addresses a gap identified by FHFA: the original PMIERs did not require insurers to hold additional assets against the risk that their own investment portfolios might lose value. The new rules effectively impose a capital charge on asset-side risk, bringing MI regulation closer to the Basel III framework used for banks (INDUSTRY_PMIERS_GUIDANCE_2024-01).

## Sources

- [INDUSTRY_PMIERS_2.0_BASE] — The foundational PMIERs document (effective March 31, 2019), defining available assets, minimum required assets, the risk-based calculation, and all operational requirements.
- [INDUSTRY_PMIERS_GUIDANCE_2024-01] — The August 2024 update introducing enhanced available-asset requirements, including bond haircuts, concentration limits, and COLI restrictions, effective March 31, 2025.
- [INDUSTRY_PMIERS_OVERVIEW_FHFA] — FHFA's 2014 overview of the draft PMIERs, providing historical context on the framework's origins, quality control requirements, and remediation options.

## Related

- [[topics/pmiers_aug_2024_update]]
- [[topics/gse_relationship]]