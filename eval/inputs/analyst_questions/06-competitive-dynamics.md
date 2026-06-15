# Competitive dynamics & market share

## Why this matters to MI analysts

The U.S. private MI cohort is a six-issuer oligopoly competing on a roughly homogeneous product (GSE-eligible MI on conforming loans), so quarter-to-quarter NIW share is the cleanest read on how each issuer is balancing pricing discipline against volume. With FHA having taken ~500 bp of insurance-in-force share from PMIs since Q3 2022 and KBW projecting only ~2% PMI IIF growth through 2027, the competitive question is no longer just intra-cohort — it is whether the private MIs can defend pricing without ceding more ground to the government channel.

Risk-based "black-box" pricing engines (MGIC Go, Radian RADAR Rates, EssentEDGE, Arch RateStar, NMI Rate GPS, Enact's engine) make competitive moves harder to detect from rate cards alone, which is why analysts now press management on call Q&A for "willingness to cede share," gross premium yield trajectory, and lender concentration. Risk Factor sections in 10-Ks are where issuers disclose competitor names, pricing-engine branding, and customer-concentration thresholds — the only public source for top-10 lender NIW share.

## Sources consulted
- https://www.nationalmortgagenews.com/list/mi-volumes-jump-12-competitive-pressure-builds
- https://www.nationalmortgagenews.com/news/fha-takes-mortgage-insurance-market-share-from-private-mi
- https://www.nationalmortgagenews.com/list/mortgage-insurers-expect-to-have-just-as-good-of-a-2025-as-2024
- https://www.nationalmortgagenews.com/list/mgic-essent-enact-radian-nmi-arch-report-1q25-profits
- https://www.nationalmortgagenews.com/news/mgic-radian-arch-enact-essent-national-mi-3q25-profits
- https://www.nationalmortgagenews.com/news/radian-essent-to-offer-black-box-mortgage-insurance-pricing
- https://www.nationalmortgagenews.com/news/why-the-pmi-industry-is-finally-ready-to-embrace-black-box-pricing
- https://www.milliman.com/en/insight/pmi-market-trends-1q-2025
- https://www.milliman.com/en/insight/pmi-market-trends-2q-2025
- https://www.urban.org/sites/default/files/2025-12/Final_Mortgage_Insurance_Data_at_a_Glance_2025_0.pdf
- https://www.fool.com/earnings/call-transcripts/2026/02/13/essent-group-esnt-q4-2025-earnings-transcript/
- https://www.gurufocus.com/stock/STU:MGC/transcripts/3173587
- https://www.ainvest.com/news/mgic-investment-q1-2025-unpacking-key-contradictions-pricing-market-share-regulatory-focus-2505/
- https://www.essent.us/mortgage-insurance/rates
- https://ir.nationalmi.com/news-releases/news-release-details/national-mi-launches-rate-gps-risk-based-pricing-0
- https://nationalmortgageprofessional.com/news/56201/arch-mi-releases-new-risk-based-ratestar-pricing-program
- https://www.fhfaoig.gov/sites/default/files/WPR-2025-001.pdf
- https://www.usmi.org/filter_data/pmi-by-the-numbers/
- https://www.inman.com/2024/07/30/private-mortgage-insurers-again-losing-market-share-to-fha-va/

## Questions

### Q1: Rank the six private MIs by NIW market share for each quarter of FY2025 and identify which issuer gained the most share Q4'24 to Q4'25.
- **Shape:** cross-issuer
- **Source:** https://www.nationalmortgagenews.com/news/mgic-radian-arch-enact-essent-national-mi-3q25-profits
- **KB doc-types likely to contain answer:** 10-Q MD&A, 8-K earnings exhibits, transcript scripts (issuers commonly cite their own NIW $ but not cohort share)
- **Current-agent-difficulty:** hard
  Rationale: Six-issuer cohort retrieval over four quarters; >60K tokens of MD&A; share computation requires summing across issuers.
- **Expected-answer notes:** MGIC ~20.1% Q2'25; Radian narrowed gap to 1.2pp; Essent NIW declined sequentially.

### Q2: For Q3 2025, what was each issuer's reported NIW dollar volume, and how does the cohort total compare to the $84.3B figure cited by Inside Mortgage Finance?
- **Shape:** cross-issuer
- **Source:** https://www.nationalmortgagenews.com/news/mgic-radian-arch-enact-essent-national-mi-3q25-profits
- **KB doc-types likely to contain answer:** 10-Q, 8-K earnings releases, investor presentations
- **Current-agent-difficulty:** moderate
  Rationale: Six point-in-time lookups; arithmetic but no synthesis trap.

### Q3: Trace each issuer's IIF growth rate (annual) for FY23, FY24, and FY25, and compare to FHA's 9.7% annual IIF growth.
- **Shape:** longitudinal cross-issuer
- **Source:** https://www.nationalmortgagenews.com/news/fha-takes-mortgage-insurance-market-share-from-private-mi
- **KB doc-types likely to contain answer:** 10-K MD&A (IIF roll-forwards), industry references on FHA
- **Current-agent-difficulty:** hard
  Rationale: 18 datapoints across 6 issuers x 3 years plus government benchmark; FHA data lives in industry-references partition, not issuer filings.

### Q4: List the top-10 customer NIW concentration disclosure (or top-customer share) for MGIC, Radian, Essent, NMIH, ACT, and ACGL most recent 10-K, and flag any issuer where the largest customer exceeds 10% of NIW.
- **Shape:** cross-issuer
- **Source:** https://www.sec.gov/Archives/edgar/data/876437/000087643719000018/exhibit99_q119.htm (illustrative format) and 10-K Risk Factors sections
- **KB doc-types likely to contain answer:** 10-K Risk Factors, "Customers" subsection, sometimes Schedule under Item 1
- **Current-agent-difficulty:** hard
  Rationale: Buried in Risk Factors; phrasing varies ("our top 10 customers accounted for X%"); ranking misses likely.

### Q5: What is the brand name of each issuer's risk-based pricing engine, and when was each launched?
- **Shape:** cross-issuer qualitative
- **Source:** https://www.essent.us/mortgage-insurance/rates ; https://ir.nationalmi.com/news-releases/news-release-details/national-mi-launches-rate-gps-risk-based-pricing-0 ; https://nationalmortgageprofessional.com/news/56201/arch-mi-releases-new-risk-based-ratestar-pricing-program
- **KB doc-types likely to contain answer:** 10-K Business overview, 10-K Risk Factors / Competition, 8-K product announcements, transcripts
- **Current-agent-difficulty:** moderate
  Rationale: Six fact lookups; product names well-disclosed but launch dates may require older 8-Ks.
- **Expected-answer notes:** MGIC Go, Radian RADAR Rates, EssentEDGE, Arch RateStar, NMI Rate GPS, Enact (verify name).

### Q6: In Mark Casale's Q4 2025 Essent earnings call Q&A, what did he say about willingness to cede market share, and which analyst pressed the question?
- **Shape:** point-in-time qualitative
- **Source:** https://www.fool.com/earnings/call-transcripts/2026/02/13/essent-group-esnt-q4-2025-earnings-transcript/
- **KB doc-types likely to contain answer:** TRANSCRIPT (ESNT 4Q25)
- **Current-agent-difficulty:** easy
  Rationale: Single-issuer single-transcript Q&A lookup.
- **Expected-answer notes:** Casale: "I would rather have better unit economics at a smaller share than the other way around"; "we are not incented on market share."

### Q7: Compare how MGIC's Tim Mattke and Essent's Mark Casale framed the price-vs-share trade-off across their FY2025 earnings calls. Whose language was more share-tolerant?
- **Shape:** qualitative cross-issuer
- **Source:** https://www.nationalmortgagenews.com/list/mortgage-insurers-expect-to-have-just-as-good-of-a-2025-as-2024 ; https://www.fool.com/earnings/call-transcripts/2026/02/13/essent-group-esnt-q4-2025-earnings-transcript/
- **KB doc-types likely to contain answer:** TRANSCRIPT (MTG, ESNT 1Q-4Q 2025)
- **Current-agent-difficulty:** hard
  Rationale: Eight transcripts; qualitative synthesis prone to genericness; both CEOs use overlapping "discipline" vocabulary.
- **Expected-answer notes:** Mattke: "price neutral with the market"; Casale: "fine being at the bottom of the pack."

### Q8: Quote each issuer's Risk Factor language describing competitors by name in their FY2024 10-K. Which issuer is most explicit about naming peers?
- **Shape:** cross-issuer qualitative
- **Source:** SEC EDGAR 10-Ks
- **KB doc-types likely to contain answer:** 10-K Risk Factors / Competition section
- **Current-agent-difficulty:** hard
  Rationale: Six 10-Ks; competition language distributed; retrieval ranking often surfaces generic risk language over peer-naming passages.

### Q9: What was the gross premium yield (or earned premium rate) reported by each issuer for Q4 2025, and which issuer reported the highest? Cite Casale's specific claim about Essent's relative position.
- **Shape:** cross-issuer mixed
- **Source:** https://www.fool.com/earnings/call-transcripts/2026/02/13/essent-group-esnt-q4-2025-earnings-transcript/
- **KB doc-types likely to contain answer:** 10-Q/10-K MD&A premium rate disclosures, transcripts
- **Current-agent-difficulty:** moderate
  Rationale: Six metric lookups plus quote retrieval; Essent claims "highest in the industry, like three points higher than the average."

### Q10: How has FHA's share of total mortgage insurance IIF moved since Q3 2022, and what drivers do MI executives cite in 2025 calls for the shift?
- **Shape:** longitudinal mixed
- **Source:** https://www.nationalmortgagenews.com/news/fha-takes-mortgage-insurance-market-share-from-private-mi ; https://www.inman.com/2024/07/30/private-mortgage-insurers-again-losing-market-share-to-fha-va/
- **KB doc-types likely to contain answer:** transcripts (qualitative), industry-references partition (USMI, KBW), 10-K market overview
- **Current-agent-difficulty:** hard
  Rationale: Cross-document synthesis between government MI references and issuer-narrative; affordability/FHA premium-cut narrative spread across many sources.
- **Expected-answer notes:** PMI IIF share fell from 55.1% to 50.1% (Q3 2022 to Q3 2025); affordability and FHA's 30bp MIP cut as drivers.

### Q11: Has any issuer disclosed a specific NIW market-share target in 2025 disclosures? Quote the language and contrast with peers who explicitly disclaim a target.
- **Shape:** qualitative cross-issuer
- **Source:** https://www.fool.com/earnings/call-transcripts/2026/02/13/essent-group-esnt-q4-2025-earnings-transcript/ ; https://www.gurufocus.com/stock/STU:MGC/transcripts/3173587
- **KB doc-types likely to contain answer:** TRANSCRIPT, 10-K MD&A
- **Current-agent-difficulty:** moderate
  Rationale: Cohort qualitative; MGIC and Essent both disclaim targets — agent must avoid false-positive matches.

### Q12: What barriers to entry for a new MI does each issuer cite in their Risk Factors? Specifically reference PMIERs Available Assets thresholds and GSE-approval timing language.
- **Shape:** cross-issuer qualitative
- **Source:** https://www.fhfaoig.gov/sites/default/files/WPR-2025-001.pdf ; 10-K Risk Factors
- **KB doc-types likely to contain answer:** 10-K Risk Factors, industry-references (FHFA OIG WPR-2025-001)
- **Current-agent-difficulty:** hard
  Rationale: Cross-document synthesis (FHFA-OIG report + 6 10-Ks); long Risk Factor sections cause trim drops.

### Q13: For NMIH and Essent, what percentage of NIW comes from the top single customer in the most recent 10-K, and how has that ratio evolved since FY2022?
- **Shape:** longitudinal cross-issuer
- **Source:** SEC EDGAR 10-Ks
- **KB doc-types likely to contain answer:** 10-K Risk Factors customer-concentration paragraph; sometimes only top-10 aggregate is disclosed
- **Current-agent-difficulty:** hard
  Rationale: Multi-year point lookups in semantically similar Risk Factor paragraphs; ranking often returns the most recent year for all queries.

### Q14: Reconstruct the history of risk-based pricing engine adoption across the cohort. Who launched first, and what does each 10-K say about why the issuer adopted black-box pricing?
- **Shape:** longitudinal qualitative cross-issuer
- **Source:** https://www.nationalmortgagenews.com/news/why-the-pmi-industry-is-finally-ready-to-embrace-black-box-pricing
- **KB doc-types likely to contain answer:** 10-K Business overview, 8-K product launch announcements, transcripts
- **Current-agent-difficulty:** hard
  Rationale: Engine launches span 2018-2021; 8-K announcements often lack Item-code header; cross-issuer narrative synthesis.

### Q15: Which 2025 transcripts contain analyst questions explicitly using the phrase "irrational pricing" or "rational pricing"? Summarize each CEO's response.
- **Shape:** qualitative cross-issuer
- **Source:** https://www.nationalmortgagenews.com/list/mi-volumes-jump-12-competitive-pressure-builds
- **KB doc-types likely to contain answer:** TRANSCRIPT Q&A across all 6 issuers, 4 quarters
- **Current-agent-difficulty:** hard
  Rationale: 24 transcripts; phrase-level retrieval prone to misses; agent likely to over-summarize.

### Q16: How does Arch CFO Francois Morin describe the trade-off between Arch MI's ~16-17% market share and gross-margin compression? Quote and cite the call.
- **Shape:** point-in-time qualitative
- **Source:** https://www.nationalmortgagenews.com/list/mortgage-insurers-expect-to-have-just-as-good-of-a-2025-as-2024
- **KB doc-types likely to contain answer:** ACGL TRANSCRIPT
- **Current-agent-difficulty:** moderate
  Rationale: Single-issuer single-quote lookup, but ACGL transcripts cover broader specialty lines so MI-specific Q&A may be diluted.

### Q17: Has any issuer announced consolidation activity (acquisition, exit, run-off) in the MI cohort during 2023-2025? If none, summarize each issuer's M&A-related Risk Factor language.
- **Shape:** mixed cross-issuer
- **Source:** https://www.usmi.org/filter_data/pmi-by-the-numbers/ ; 10-K Risk Factors
- **KB doc-types likely to contain answer:** 10-K Risk Factors, 8-K M&A items, transcripts
- **Current-agent-difficulty:** moderate
  Rationale: Negative-result question — agent must distinguish between "no activity disclosed" and "retrieval miss."

### Q18: Compare 2025 base premium rate guidance from Essent (~40bp) with disclosed/observed average premium rates at MGIC, Radian, Arch, Enact, and NMIH. What is the cohort spread?
- **Shape:** cross-issuer
- **Source:** https://www.fool.com/earnings/call-transcripts/2026/02/13/essent-group-esnt-q4-2025-earnings-transcript/ ; https://www.milliman.com/en/insight/pmi-market-trends-2q-2025
- **KB doc-types likely to contain answer:** transcripts (forward guidance), 10-Q/10-K (realized rates)
- **Current-agent-difficulty:** hard
  Rationale: Mixed forward-guidance vs realized rates; six issuers; basis-point precision required; XBRL premium rate concepts often missing.

### Q19: For each issuer, identify the specific 8-K (Item code and date) announcing pricing engine launches or material pricing actions in 2024-2025. Flag any that lack a clear Item header.
- **Shape:** cross-issuer point-in-time
- **Source:** https://ir.nationalmi.com/news-releases/news-release-details/national-mi-launches-rate-gps-risk-based-pricing-0
- **KB doc-types likely to contain answer:** 8-K (Items 7.01, 8.01)
- **Current-agent-difficulty:** hard
  Rationale: Known agent failure mode — exhibits without Item header. Pricing actions often go via 7.01 Reg FD or 8.01 Other Events without a press-release header.

### Q20: What does each issuer's FY24 10-K say about the prospect of new entrants into the U.S. private MI market? Has anyone disclosed knowledge of a new applicant to GSE approval?
- **Shape:** cross-issuer qualitative
- **Source:** https://www.fhfaoig.gov/sites/default/files/WPR-2025-001.pdf
- **KB doc-types likely to contain answer:** 10-K Risk Factors / Competition, FHFA-OIG references
- **Current-agent-difficulty:** moderate
  Rationale: Standard Risk Factor passage in all six issuers; risk of generic synthesis.

## Capability gaps observed

The agent's documented "heavy multi-issuer cohort retrieval" failure is most acute in Q1, Q3, Q14, Q15, and Q18 — each requires pulling Risk Factor or transcript Q&A passages from all six issuers across multiple periods, and the trimming behavior tends to drop chunks before synthesis. A tool-side mitigation would be to add per-issuer retrieval budgets so cohort coverage is enforced rather than emergent.

The 8-K-without-Item-header gap (Q19) is unavoidable for pricing-action disclosures because most pricing engine launches come through Reg FD/Other Events 8-Ks where companies attach a press-release exhibit but the parsed Item code is generic. Customer-concentration questions (Q4, Q13) are likely to suffer ranking misses because Risk Factor passages on "our largest customer" share embedding space with unrelated counterparty-risk language.

Qualitative synthesis genericness will likely show up on Q7, Q11, Q15, Q17, and Q20 where every CEO uses overlapping "discipline / prudent / risk-adjusted" vocabulary; the agent tends to merge nearly-identical phrasings into bland summaries rather than surface the precise quote that distinguishes one CEO from another. Q6 and Q16 are easier because they target a specific named executive on a specific call.
