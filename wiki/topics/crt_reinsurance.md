# CRT and Reinsurance

> Credit risk transfer ("CRT") and reinsurance are the central capital-management tools that have transformed the U.S. private mortgage insurance industry from a "Buy-and-Hold" risk-taker to an "Aggregate-Manage-Distribute" risk manager since 2015 (INDUSTRY_USMI_RESILIENCY_2023-11; INDUSTRY_USMI_WHITE_PAPER_2020-10). The industry uses three principal structures — quota share reinsurance ("QSR") with traditional reinsurers, excess-of-loss ("XOL") reinsurance, and insurance-linked notes ("ILNs") issued through special-purpose insurers — to cede portions of risk in exchange for premium, ceding commissions, and PMIERs capital relief under Section 707 of the PMIERs framework (INDUSTRY_PMIERS_2.0_BASE; see [[topics/pmiers]]). Per USMI, since 2015 the industry has transferred nearly $73.8 billion of risk on more than $3.4 trillion of insurance-in-force; through November 2023, MIs had executed 53 QSR/XOL reinsurance deals ($51.5 billion of risk ceded) and 56 ILN transactions ($22.3 billion of risk ceded on more than $2.3 trillion of notional mortgages) (INDUSTRY_USMI_RESILIENCY_2023-11). Today every MI runs a layered CRT program; at year-end 2025, MGIC reports total reinsurance arrangements reduced PMIERs required assets by approximately $2.8 billion (~47%) (MTG_TRANSCRIPT_2025-12-31), and Essent reports approximately 98% of its mortgage insurance portfolio is subject to some form of reinsurance (ESNT_TRANSCRIPT_2025-12-31). Separately, the GSEs themselves operate large CRT programs (Fannie Mae's CIRT/CAS and Freddie Mac's ACIS/STACR) that transfer Enterprise credit risk to private investors and reinsurers, creating a second venue in which the MIs (notably Essent Re, Enact Re, and Arch) participate as reinsurers (INDUSTRY_FHFA_ANNUAL_REPORT_2024).

## What it is

The U.S. private mortgage insurance industry runs **two parallel CRT activities**: (a) the MIs cede risk on their own insured portfolios to third parties, and (b) the MIs (through their Bermuda reinsurers and Arch's mortgage operations) take on risk by participating in the GSEs' CRT programs.

### MI-CRT — the MIs cede their own risk

Three principal structures, as defined in the PMIERs framework (see [[topics/pmiers]]):

**Quota Share Reinsurance ("QSR").** Under a QSR transaction, the MI cedes a fixed percentage of premiums earned and the same fixed percentage of incurred losses on covered policies, in exchange for a ceding commission and a profit commission that varies inversely with ceded losses (ESNT_10-K_2025-12-31; ACT_10-K_2025-12-31). PMIERs Section 707 grants reinsurance credit (a reduction in the risk-based required asset amount) for QSR transactions if the reinsurance arrangement: (a) is not structured with a limit of liability; (b) provides coverage on an incurred basis for the lesser of ten years or the remaining life of the reinsured policies; (c) covers a profile of loans not materially different from the profile of all loans of similar vintage covered by the MI; and (d) the reinsurer entity meets the rating-and-collateral requirements (INDUSTRY_PMIERS_2.0_BASE Section 707; Exhibit A). The reinsurer must post collateral — the required percentage scales with the reinsurer's average S&P / A.M. Best / Moody's rating, with below-investment-grade reinsurers facing a 75% required collateral percentage and the MI's available assets including the trust balance instead of receiving an RBRAA reduction (INDUSTRY_PMIERS_2.0_BASE Section 707).

**Excess-of-Loss Reinsurance ("XOL").** Under an XOL transaction, the reinsurer indemnifies the MI for losses in excess of a specified attachment point, up to a specified detachment point. PMIERs grants reinsurance credit for the layer covered if the attachment point (in dollars) is below what the RBRAA would be on the direct RIF; direct RIF is reduced proportionally based on the loss layer covered (INDUSTRY_PMIERS_2.0_BASE Exhibit A, paragraph 4). Example from PMIERs 2.0: for an XOL with attachment point of 4% and detachment point of 7% (a 3% loss layer) covering a loan population for which the RBRAA equals 7%, the direct RIF reduction equals 3% / 7% = 42.9% (INDUSTRY_PMIERS_2.0_BASE Exhibit A).

**Insurance-Linked Notes ("ILNs").** ILN transactions are XOL reinsurance executed through unaffiliated special-purpose insurers ("SPVs") domiciled in Bermuda, which finance the reinsurance coverage by issuing mortgage insurance-linked notes to investors in the capital markets. The MI's risk is fully collateralized by the trust account funded by the SPV's note issuance. PMIERs Section 707 explicitly addresses SPVs: "with respect to any special purpose vehicle or other similar entity ... related to an approved insurer's reinsurance securitization structure, Fannie Mae may permit a reduction in the approved insurer's risk-based required asset amount for the risk ceded to the SPV in an amount determined by Fannie Mae" (INDUSTRY_PMIERS_2.0_BASE Section 707). The MIs typically retain the first 185-250 basis points of risk to align incentives with investors (INDUSTRY_USMI_RESILIENCY_2023-11; INDUSTRY_USMI_WHITE_PAPER_2020-10).

The MI-side ILN programs by company:
- **MGIC's Home Re Entities**: unaffiliated special purpose insurers domiciled in Bermuda that participate in MGIC's aggregate XOL transactions through the ILN market (MTG_10-K_2025-12-31). MGIC completed its eighth ILN transaction in January 2026, providing $324 million of additional loss protection on policies written between January 2022 and March 2025 (MTG_TRANSCRIPT_2025-12-31).
- **Radian's Eagle Re Issuers**: unaffiliated Bermuda-domiciled special purpose insurers that participate in Radian's XOL Program through ILN issuances (RDN_10-K_2025-12-31).

**Why MI-CRT exists**: The 2008 financial crisis exposed MI portfolios to "uncapped liability ... significant franchise and return volatility during down cycles" (INDUSTRY_USMI_WHITE_PAPER_2020-10). The post-crisis transformation, captured in USMI's framework:

| Pre-Crisis ("Buy-and-Hold") | Post-2015 ("Aggregate-Manage-Distribute") |
|---|---|
| Exposure-based capital (Statutory) | Risk-based capital (PMIERs) |
| Less granular, relatively static pricing | More granular, risk-based and dynamic pricing |
| Manage risk through credit policy alone | Manage risk through credit policy and pricing |
| Focus on avoiding adverse credit selection | Proactive portfolio selection based on economic value |
| "Buy and hold" risk-taking | Active risk manager (aggregate, manage, and distribute risk) |

(Source: INDUSTRY_USMI_RESILIENCY_2023-11; INDUSTRY_USMI_WHITE_PAPER_2020-10.)

USMI's framing: "Deploying MI-CRT allows private MIs to hedge against adverse losses and mitigate volatility through housing and business cycles ... Transferring credit risk is not only an effective hedge to exposure to cyclical mortgage risk but can also be accretive to returns by freeing up capital at a fraction of the cost of equity capital without adding financial leverage to the balance sheet" (INDUSTRY_USMI_RESILIENCY_2023-11).

### GSE CRT — the MIs take on Enterprise risk

Each Enterprise has, since 2013, transferred portions of its single-family mortgage credit risk to the private sector through structured CRT programs that combine capital-markets security issuances and insurance/reinsurance transactions (INDUSTRY_FHFA_ANNUAL_REPORT_2024). The 2024 vehicle activity disclosed by FHFA covers principally the multifamily book:

- **Fannie Mae multifamily**: Multifamily Connecticut Avenue Securities ("MCAS") and Multifamily Credit Insurance Risk Transfer ("MCIRT") transactions, alongside the Delegated Underwriting and Servicing ("DUS") program. In 2024, Fannie Mae transferred risk on approximately $55 billion of multifamily production through DUS plus three CRT transactions (one MCAS, two MCIRT) covering ~$26 billion of acquisitions (INDUSTRY_FHFA_ANNUAL_REPORT_2024).
- **Freddie Mac multifamily**: K-deal securitization program, Multifamily Structured Credit Risk ("MSCR") notes, and Multifamily Credit Insurance Pool ("MCIP") transactions. In 2024, Freddie Mac's K-deal program transferred risk on ~$28 billion of new multifamily acquisitions plus two companion MSCR/MCIP transactions covering ~$17 billion (INDUSTRY_FHFA_ANNUAL_REPORT_2024).
- **Single-family programs**: Each Enterprise also runs single-family CRT through both capital-markets security issuances and reinsurance / insurance transactions; the FHFA Annual Report 2024 reports combined 2024 single-family CRT volume of approximately $365 billion of UPB and $11.9 billion of RIF, and cumulative single-family CRT since 2013 of approximately $7 trillion of UPB and $222 billion of RIF (INDUSTRY_FHFA_ANNUAL_REPORT_2024).

The MIs participate in GSE CRT through their Bermuda reinsurance subsidiaries:

- **Essent Re** writes GSE credit-risk-transfer business; at year-end 2025 it provided insurance or reinsurance relating to GSE risk-share and other reinsurance transactions covering approximately $2.3 billion of risk (ESNT_10-K_2025-12-31).
- **Enact Re** participates in GSE single-family and multifamily credit-risk-share transactions (ACT_10-K_2025-12-31).
- **Arch** has mortgage operations that include "participation in GSE credit risk-sharing transactions" alongside U.S. and international primary mortgage insurance (ACGL_10-K_2025-12-31).

## Why it matters

Three reasons CRT and reinsurance are operationally consequential for U.S. mortgage insurance.

**First, CRT is now the dominant tool for capital management at every MI**. The PMIERs cushion (Available Assets in excess of Minimum Required Assets) at every MI is materially driven by the reinsurance credit obtained under PMIERs Section 707. At year-end 2025, MGIC reports total reinsurance arrangements reduced PMIERs required assets by approximately $2.8 billion (~47%) (MTG_TRANSCRIPT_2025-12-31). Enact reports that third-party reinsurance provided $1,932 million of PMIERs credit (vs. $1,885 million at YE 2024) (ACT_10-K_2025-12-31). Essent reports that approximately 98% of its mortgage insurance portfolio was subject to some form of reinsurance at YE 2025 (ESNT_TRANSCRIPT_2025-12-31). NMI characterizes its forward-flow reinsurance program as a standing source of "deep, secure, and efficient PMIERs growth capital" (NMIH_TRANSCRIPT_2025-12-31).

**Second, CRT structurally caps tail-risk exposure to a known cost of capital**. The post-crisis transformation cited by USMI is that "transferring credit risk is not only an effective hedge to exposure to cyclical mortgage risk but can also be accretive to returns by freeing up capital at a fraction of the cost of equity capital" (INDUSTRY_USMI_RESILIENCY_2023-11). NMIH characterizes its full-2028 forward-flow program as costing approximately 4% pretax cost of capital (NMIH_TRANSCRIPT_2025-12-31), well below the cost of incremental equity. MGIC notes that its Q4 2025 reinsurance program renegotiation on 2022 NIW QSR treaties is expected to reduce that treaty's ongoing cost by approximately 40% beginning in 2026 (MTG_TRANSCRIPT_2025-12-31).

**Third, the second leg — GSE CRT participation — is a material earnings stream for the Bermuda reinsurance subsidiaries**. Essent Re generated approximately $80 million of third-party net income in 2025 alongside its $2.3 billion of risk in force (ESNT_TRANSCRIPT_2025-12-31). For Arch, mortgage segment underwriting income (which includes both U.S. primary MI and GSE CRT participation) was $1.0 billion in 2025 — the fourth consecutive year above the $1.0 billion threshold (ACGL_TRANSCRIPT_2025-12-31).

USMI's view of the value of MI-CRT to the housing finance system:

| To the MI | To the housing finance system |
|---|---|
| Diversifies capital beyond entity-based equity capital | Strengthens private MIs as counterparties |
| Protects portfolio against adverse losses in housing downturns | MIs underwrite/actively manage the mortgage credit risk, ensuring quality control and a "second pair of eyes" on risk |
| Enhances counterparty strength | Reduces investor risk exposure (private MIs hold the first 185-250 bps of risk for ILN and XOL transactions, ensuring alignment of incentives) |
| Provides capital credit for PMIERs, rating agencies, and state regulatory requirements | Offers significant potential for growth in the MI-related liquidity pool |
| Cost-effective source of funding that allows private MIs to hold excess capital | |

(Source: INDUSTRY_USMI_RESILIENCY_2023-11.)

## Current state (as of 2025-12-31)

**Industry-level CRT volumes** (cumulative from 2015 through November 2023, per INDUSTRY_USMI_RESILIENCY_2023-11):
- Total risk transferred: nearly $73.8 billion
- Insurance-in-force covered: more than $3.4 trillion
- Reinsurance market deals (QSR + XOL): 53 deals ceding $51.5 billion of risk (as of September 30, 2023)
- ILN transactions: 56 deals transferring $22.3 billion of risk on more than $2.3 trillion of notional mortgages (as of November 2, 2023)

**Per-MI reinsurance program detail at year-end 2025**:

**MGIC**:
- Approximately 73.8% of YE 2025 IIF subject to QSR transactions (vs. 68.2% at YE 2024); 87.2% of 2025 NIW subject to QSR (vs. 86.9% in 2024) (MTG_10-K_2025-12-31).
- Q4 2025 actions: a $250 million XOL transaction covering 2021 NIW; a 40% quota share covering most of 2027 NIW; renegotiation of the 2022-NIW QSR treaties to reduce ongoing cost by approximately 40% beginning in 2026 (MTG_TRANSCRIPT_2025-12-31).
- January 2026: an eighth ILN transaction providing $324 million of loss protection on policies written between January 2022 and March 2025 (MTG_TRANSCRIPT_2025-12-31).
- Total reinsurance impact on PMIERs required assets: ~$2.8 billion (~47% of MRA) at YE 2025 (MTG_TRANSCRIPT_2025-12-31).
- Reinsurance vehicles: traditional XOL transactions plus the **Home Re Entities** (Bermuda special-purpose insurers participating in MGIC's aggregate XOL transactions through the ILN market) (MTG_10-K_2025-12-31).

**Radian**:
- A layered set of QSR Agreements (2012, 2016 Single Premium, 2018 Single Premium, 2020 Single Premium, 2022, 2023, 2024, 2025, 2026, 2027) and XOL Agreements (2023 XOL, 2025 XOL), each covering specific NIW periods (RDN_10-K_2025-12-31).
- Q4 2025: a $373 million excess-of-loss reinsurance agreement covering certain policies written from 2016 through 2021 (RDN_TRANSCRIPT_2025-12-31).
- ILN program: the **Eagle Re Issuers** (unaffiliated Bermuda-domiciled special-purpose insurers) (RDN_10-K_2025-12-31).
- PMIERs Cushion at YE 2025: $1.6 billion, materially supported by reinsurance credit (RDN_TRANSCRIPT_2025-12-31).

**Essent**:
- Intercompany QSR with **Essent Re** (Bermuda Class 3B): 50% of NIW from January 1, 2025 onward (up from 35% during 2021-2024 and 25% prior to 2021) (ESNT_10-K_2025-12-31).
- Third-party QSR program: QSR-2025 (25% of 2025 NIW), forward 2026 (25% of 2026 NIW), forward 2027 (20% of 2027 NIW) (ESNT_10-K_2025-12-31).
- Approximately $1.3 billion of XOL coverage on NIW from January 2018 through August 2019 and August 2020 through December 2025 (ESNT_10-K_2025-12-31).
- ~98% of mortgage insurance portfolio reinsured at YE 2025 (ESNT_TRANSCRIPT_2025-12-31).
- Essent Re Q4 2025 entry into the **Lloyd's market** via Funds-at-Lloyd's ($50M FAL on Essent Re's existing balance sheet) to write property-and-casualty reinsurance starting in 2026 — expected $100-150M written premium in 2026 (ESNT_TRANSCRIPT_2025-12-31).
- Essent Re GSE CRT and other reinsurance covering ~$2.3 billion of risk at YE 2025; ~$80M of third-party net income in 2025 (ESNT_10-K_2025-12-31; ESNT_TRANSCRIPT_2025-12-31).

**Enact**:
- Intercompany QSR with **Enact Re** (Bermuda) — Enact Re reinsures EMICO's NIW (capitalized with a $500M contribution in 2023) (ACT_10-K_2025-12-31).
- Third-party CRT program combines XOL, QSR, and ILNs; new QS signed September 23, 2025 ceding approximately 34% of *a portion of* expected 2027 NIW (ACT_10-K_2025-12-31).
- 2024 program: two QSR agreements ceding ~27% of 2025 and 2026 NIW; forward XOL transactions providing $225M and $260M of coverage on 2025 and 2026 books (ACT_TRANSCRIPT_2024-12-31).
- Third-party reinsurance PMIERs credit at YE 2025: $1,932 million (vs. $1,885M at YE 2024) (ACT_10-K_2025-12-31).
- Enact Re ratings: A- (stable) by both A.M. Best and S&P (ACT_10-K_2025-12-31).

**NMI Holdings**:
- A layered QSR + XOL program with forward-flow coverage for all new business produced through 2028 — established by Q4 2025 transactions (NMIH_TRANSCRIPT_2025-12-31).
- Estimated cost: approximately 4% pretax cost of capital (NMIH_TRANSCRIPT_2025-12-31).
- Re One (Wisconsin-domiciled) historically provided intercompany reinsurance to NMIC; that coverage has been commuted and Re One does not currently have active insurance exposures (NMIH_10-K_2025-12-31).

**Arch**:
- Three-segment structure (Insurance, Reinsurance, Mortgage) means Arch operates as both an MI ceding risk and a reinsurer assuming risk; mortgage segment underwriting income was $1.0 billion in 2025, fourth consecutive year above $1.0 billion (ACGL_TRANSCRIPT_2025-12-31).
- Arch's mortgage operations include U.S. and international primary MI plus participation in GSE credit-risk-sharing transactions (ACGL_10-K_2025-12-31).

**GSE CRT activity in 2024** (per FHFA):
- Combined Enterprise single-family CRT: approximately $365 billion of UPB / $11.9 billion of RIF (the second consecutive year of reduced CRT volume) (INDUSTRY_FHFA_ANNUAL_REPORT_2024).
- Cumulative CRT since 2013: approximately $7 trillion of UPB / $222 billion of RIF (INDUSTRY_FHFA_ANNUAL_REPORT_2024).
- 2024 multifamily activity at Fannie Mae: ~$55B through the Delegated Underwriting and Servicing (DUS) program; three CRT transactions (one MCAS, two MCIRT) collectively transferring credit risk on ~$26B of acquisitions (INDUSTRY_FHFA_ANNUAL_REPORT_2024).
- 2024 multifamily activity at Freddie Mac: K-deal program transferred risk on ~$28B of new acquisitions; two MSCR/MCIP transactions transferred risk on ~$17B; one floating-rate K-deal reinsurance transaction and one senior housing loan MSCR transferred risk on ~$16B (INDUSTRY_FHFA_ANNUAL_REPORT_2024).

## How it has evolved

**Pre-2008**: U.S. MI portfolios were managed on a "Buy-and-Hold" basis, with limited use of reinsurance. The industry was "significantly levered to U.S. housing and economic cycles" (INDUSTRY_USMI_WHITE_PAPER_2020-10). Capital was primarily entity-based equity, exposed to franchise and return volatility during down cycles (INDUSTRY_USMI_RESILIENCY_2023-11).

**2008-2014**: Post-crisis losses prompt industry-wide rethinking. Three MIs (legacy entities) are placed into run-off by their state regulators (INDUSTRY_PMIERS_OVERVIEW_FHFA). The PMIERs framework is drafted with explicit provisions (Section 707) for reinsurance credit.

**December 31, 2015**: Original PMIERs effective. Section 707 codifies the reinsurance-credit framework, with collateral and counterparty rating requirements (INDUSTRY_PMIERS_2.0_BASE; see [[topics/pmiers]]). Same year, the industry begins MI-CRT through ILNs: in 2015, the industry issued $298.9 million in ILNs covering $32.4 billion of insurance in force (Urban Institute, cited in INDUSTRY_USMI_RESILIENCY_2023-11).

**2015-2023 buildout**: ILN volumes grow rapidly. By 2021, annual ILN issuance reached $6.3 billion, protecting $652.2 billion in mortgage loans (Urban Institute, cited in INDUSTRY_USMI_RESILIENCY_2023-11). By November 2023, the industry has executed 56 ILN transactions transferring $22.3 billion of risk on more than $2.3 trillion of notional mortgages (INDUSTRY_USMI_RESILIENCY_2023-11). Concurrently, traditional QSR and XOL deals expand: 53 deals ceding $51.5 billion of risk through September 30, 2023 (INDUSTRY_USMI_RESILIENCY_2023-11).

**September 27, 2018**: PMIERs 2.0 base text published. Section 707 reinsurance-credit framework codifies collateral requirements (Table 707-1) and counterparty risk haircuts (Table 707-2), with explicit treatment of SPVs in reinsurance securitization structures (INDUSTRY_PMIERS_2.0_BASE).

**2020-2022**: COVID-19 stress validates the industry's reinsurance posture — losses on stressed portions of the portfolio are ceded to reinsurers, capping MI-side cycle-volatility (INDUSTRY_USMI_RESILIENCY_2023-11). Per BTIG analyst Mark Palmer in April 2020: "Private mortgage insurers (PMIs) are now better positioned to withstand the impact of the COVID-19 pandemic versus during the [2008] financial crisis, as a result of much stricter underwriting standards and the widespread use of quota share reinsurance, among others" (cited in INDUSTRY_USMI_WHITE_PAPER_2020-10).

**2023**: Forward-flow QSR programs become standard practice. MIs begin signing multi-year forward QSR commitments covering NIW through 2026 and 2027.

**Q4 2025**: Forward-flow programs extended further. Several MIs sign QSR / XOL coverage extending through 2028 (NMI Holdings, Essent's 2027 forward QS) (NMIH_TRANSCRIPT_2025-12-31; ESNT_10-K_2025-12-31). MGIC restructures its 2022-NIW QSR treaties to reduce ongoing cost by ~40% beginning 2026 (MTG_TRANSCRIPT_2025-12-31). Essent Re enters the **Lloyd's market** via Funds-at-Lloyd's to write property-and-casualty reinsurance starting in 2026 — a notable expansion beyond pure mortgage CRT (ESNT_TRANSCRIPT_2025-12-31). On the same vector, **Radian Group acquires Inigo Limited** (a Lloyd's specialty insurer) on February 2, 2026 in a $1.67 billion all-cash transaction, marking a structural pivot toward a multi-line specialty platform (RDN_10-K_2025-12-31).

**Forward**: GSE CRT programs continue to evolve under FHFA oversight. The Enterprises' January 1, 2025 PSPA amendments removed the prior limitations on higher-risk loan acquisitions (see [[topics/gse_relationship]]), potentially increasing the volume of MI-eligible NIW that flows to GSE CRT vehicles. MIs continue to extend forward-flow QSR and XOL coverage as the industry consolidates around the "Aggregate-Manage-Distribute" operating model (INDUSTRY_USMI_RESILIENCY_2023-11).

## Sources

- [INDUSTRY_USMI_RESILIENCY_2023-11] — Industry-level CRT statistics (since 2015: $73.8B risk transferred / $3.4T IIF; 53 reinsurance deals / $51.5B; 56 ILN deals / $22.3B / $2.3T notional through November 2023); Urban Institute citations on ILN growth ($298.9M / $32.4B in 2015 → $6.3B / $652.2B in 2021); Buy-and-Hold-vs-Aggregate-Manage-Distribute industry transformation framework; the 185-250 bps first-loss retention; the dual benefits of MI-CRT (to the MI and to the housing finance system); 2023 framing that private MI is the most-used execution for low-down-payment borrowers since 2018; FHFA Director Sandra Thompson 2023 quote on MI's first-loss role.
- [INDUSTRY_USMI_WHITE_PAPER_2020-10] — Pre-Crisis vs. post-2015 MI business-model transformation; BTIG analyst quote (April 2020) on widespread use of quota share reinsurance positioning the industry for COVID-19; Goldman Sachs 2020 quote on agency CRT benefiting from MI credit enhancement.
- [INDUSTRY_PMIERS_2.0_BASE] — Section 707 (Reinsurance and Risk Sharing Transactions) framework: required collateral percentages by reinsurer rating (Table 707-1); counterparty risk haircuts (Table 707-2); eligible collateral; Section 708 lender captive reinsurance contracts; SPV treatment ("Fannie Mae may permit a reduction"); Exhibit A reinsurance-credit framework for QSR (1.a-d criteria) and XOL (paragraph 4 attachment-point logic with 4%/7% example yielding 42.9% reduction); the 5.6% prudential floor on performing primary RIF.
- [INDUSTRY_FHFA_ANNUAL_REPORT_2024] — GSE CRT volume statistics: 2024 single-family CRT activity ($365B UPB / $11.9B RIF — second consecutive year of reduced volume); cumulative since 2013 ($7T UPB / $222B RIF); 2024 multifamily CRT activity at Fannie ($55B DUS, $26B across one MCAS and two MCIRT); at Freddie ($28B K-deal, $17B MSCR/MCIP, $16B reinsurance + senior housing); the Enterprise CRT mandate as "a core part of their single-family credit guarantee businesses" reducing taxpayer risk.
- [MTG_10-K_2025-12-31] — MGIC YE 2025 reinsurance posture: 73.8% of IIF and 87.2% of NIW under QSR; the Home Re Entities (Bermuda special-purpose insurers participating in aggregate XOL through the ILN market); aggregate reinsurance reducing PMIERs MRA by ~$2.8B / ~47%.
- [MTG_TRANSCRIPT_2025-12-31] — Q4 2025 actions ($250M XOL on 2021 NIW; 40% QS on 2027 NIW; 2022-NIW QSR renegotiation cutting cost ~40%; January 2026 eighth ILN with $324M loss protection on January 2022-March 2025 policies); the "$2.8B / ~47%" reinsurance impact on PMIERs MRA.
- [RDN_10-K_2025-12-31] — Radian's layered QSR Agreements (2012-2027) and XOL Agreements (2023 XOL, 2025 XOL); the Eagle Re Issuers (Bermuda-domiciled SPVs); Q4 2025 $373M XOL on 2016-2021 policies; Inigo acquisition closing February 2, 2026 for $1.67B.
- [RDN_TRANSCRIPT_2025-12-31] — Radian Q4 2025 $373M XOL transaction; YE 2025 $1.6B PMIERs Cushion.
- [ESNT_10-K_2025-12-31] — Essent intercompany QSR schedule (25% pre-2021, 35% 2021-2024, 50% from January 1, 2025); third-party QSR program (QSR-2025 25%, forward 2026 25%, forward 2027 20%); $1.3B XOL coverage on specified NIW periods; Essent Re GSE CRT covering $2.3B of risk at YE 2025; Bermuda Class 3B regulation of Essent Re.
- [ESNT_TRANSCRIPT_2025-12-31] — Essent Q4 2025 disclosures (~98% portfolio reinsured; Essent Re ~$80M third-party net income; Lloyd's entry via Funds-at-Lloyd's).
- [ACT_10-K_2025-12-31] — Enact CRT program (XOL + QSR + ILNs); $500M Enact Re capitalization in 2023; $1,932M PMIERs reinsurance credit at YE 2025; September 23, 2025 quota share for 2027 NIW (~34%); Enact Re A- ratings.
- [ACT_TRANSCRIPT_2024-12-31] — 2024 QSR agreements ceding ~27% of 2025 and 2026 NIW; forward XOL transactions ($225M and $260M).
- [NMIH_TRANSCRIPT_2025-12-31] — Q4 2025 forward-flow program covering all NIW through 2028 at ~4% pretax cost of capital; reinsurance as "a deep, secure, and efficient source of PMIERs growth capital."
- [NMIH_10-K_2025-12-31] — Re One historical role and current commuted/inactive status.
- [ACGL_10-K_2025-12-31] — Arch's mortgage segment structure (U.S. + international primary MI + GSE CRT participation).
- [ACGL_TRANSCRIPT_2025-12-31] — Mortgage segment $1.0B underwriting income in 2025 (fourth consecutive year above $1.0B threshold).
- [INDUSTRY_PMIERS_GUIDANCE_2024-01] — referenced for the August 2024 PMIERs Update affecting Available Assets (full discussion in [[topics/pmiers]]).

## Related

- [[topics/pmiers]]
- [[topics/gse_relationship]]
- [[topics/us_mortgage_market]]
- [[topics/mi_regulatory_landscape]]
- [[topics/catastrophe_impact_on_mi]]
- [[companies/mtg_mgic]]
- [[companies/esnt_essent]]
- [[companies/act_enact]]
- [[companies/rdn_radian]]
- [[companies/nmih_nmi]]
- [[companies/acgl_arch]]
