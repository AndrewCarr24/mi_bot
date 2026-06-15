# Macro & housing

## Why this matters to MI analysts

Mortgage insurance is a derivative bet on the agency-conforming housing finance system. NIW is a function of (a) the size of the purchase mortgage market, (b) the high-LTV (>80%) share within agency, (c) MI's penetration vs. FHA/VA, and (d) refi mix — refis are typically lower-LTV and skew the high-LTV pie toward purchase. Persistency, the second-most-important driver of insurance-in-force (IIF) and earned-premium economics, is almost entirely a rate-environment story: the gap between the WAC of the embedded book and prevailing rates determines refi-driven runoff.

Analysts covering ACGL/ACT/ESNT/MTG/NMIH/RDN have to triangulate company disclosure (NIW, IIF, persistency, FICO/LTV mix) against external macro views (MBA/Fannie/MI competitors' market sizing, ICE Mortgage Monitor, FHFA reports, Case-Shiller HPA). When rates trend down (e.g., the late-2025 / early-2026 setup with 30-year fixed near 6.5–6.7% and Fannie Mae projecting sub-6% by year-end 2026), analysts need to model a step-up in refi share, persistency erosion on 2024–25 vintages, and a structural shift toward FHA/VA at the margin — all simultaneously.

## Sources consulted
- https://www.mba.org/news-and-research/newsroom/news/2025/10/19/mba-forecast--total-single-family-mortgage-originations-to-increase-8-percent-to--2.2-trillion-in-2026
- https://www.housingwire.com/articles/mba-forecasts-2-2t-mortgage-origination-in-2026/
- https://www.fanniemae.com/newsroom/fannie-mae-news/mortgage-rates-expected-move-below-6-percent-end-2026
- https://www.nationalmortgagenews.com/list/mi-volumes-jump-12-competitive-pressure-builds
- https://www.milliman.com/en/insight/pmi-market-trends-2q-2025
- https://www.milliman.com/en/insight/mortgage-market-and-housing-trends-q3-2025
- https://mortgagetech.ice.com/resources/data-reports/may-2025-mortgage-monitor
- https://mortgagetech.ice.com/publicdocs/mortgage/imt-september-2025-mortgage-monitor-report-5Bbzsj9QEEEa.pdf
- https://www.cotality.com/press-releases/home-prices-have-fallen-for-most-of-2025
- https://fred.stlouisfed.org/series/CSUSHPINSA
- https://www.urban.org/sites/default/files/2026-03/February%20v3.pdf
- https://www.federalregister.gov/documents/2025/12/23/2025-23746/2026-2028-enterprise-housing-goals
- https://www.housingwire.com/articles/fhfa-housing-goals-2026-2028/
- https://www.hud.gov/program_offices/housing/rmra/oe/rpts/fhamktsh/fhamktqtrly
- https://www.insidemortgagefinance.com/data/3751-mortgage-insurance-trends
- https://mtg.mgic.com/events-and-presentations

## Questions

### Q1: What was the 2026 MBA forecast for total single-family origination volume, and what is the implied purchase vs. refinance split?
- **Shape:** point-in-time
- **Source:** https://www.mba.org/news-and-research/newsroom/news/2025/10/19/mba-forecast--total-single-family-mortgage-originations-to-increase-8-percent-to--2.2-trillion-in-2026
- **KB doc-types likely to contain answer:** 10-K MD&A "Mortgage Insurance Market" / "Industry Conditions" sections, MI investor day decks, INDUSTRY_MBA_*, transcript prepared remarks.
- **Current-agent-difficulty:** easy
  Rationale: Single external data point; if MBA reference doc is in the KB the agent can lift it; otherwise it shows up in nearly every MI 10-K MD&A.
- **Expected-answer notes:** $2.2T total in 2026 (+8% YoY from ~$2.0T in 2025); purchase ~$1.46T (+7.7%), refi ~$737B (+9.2%).

### Q2: How did the six private MIs' aggregate NIW in 4Q25 compare to 4Q24, and which two issuers grew NIW fastest year-over-year?
- **Shape:** cross-issuer
- **Source:** https://www.nationalmortgagenews.com/list/mi-volumes-jump-12-competitive-pressure-builds
- **KB doc-types likely to contain answer:** Each of ACGL/ACT/ESNT/MTG/NMIH/RDN 4Q25 earnings press release / 10-K, 4Q25 transcripts.
- **Current-agent-difficulty:** hard
  Rationale: Six-issuer cohort retrieval; NIW figure plus a YoY growth derivation per issuer; classic >60K-token cohort problem where trim drops chunks.
- **Expected-answer notes:** Industry +12% FY25 vs FY24; Q4 NIW: MGIC $17.1B (+7.5%), Radian $15.9B (+20%), Enact $14.4B (+8.3%), Arch $14.3B (+21.2%), NMI $14.2B (+19.3%), Essent $11.8B (-3.3%). Fastest growers: Arch and Radian.

### Q3: Across the cohort, what are the latest disclosed 12-month persistency rates, and how does each issuer attribute movement to the rate environment?
- **Shape:** cross-issuer + qualitative
- **Source:** https://www.milliman.com/en/insight/mortgage-market-and-housing-trends-q3-2025 ; individual issuer 10-Ks
- **KB doc-types likely to contain answer:** 10-K "Persistency" disclosure, transcript Q&A on rate-environment outlook.
- **Current-agent-difficulty:** hard
  Rationale: Six-issuer numeric retrieval combined with qualitative synthesis on a rate-environment narrative — agent's known weakness on synthesis genericness for cohort qualitative questions.
- **Expected-answer notes:** Industry persistency normalized into the 84–86% range during 2025 as 30-year rates held 6.5–7%. Enact disclosed ~59% of book carries note rates below 6%, supporting "elevated persistency."

### Q4: What share of the existing mortgage universe was "in the money" for refinance at end-2025, and how should that translate to MI runoff under MBA's 2026 rate path?
- **Shape:** mixed
- **Source:** https://mortgagetech.ice.com/publicdocs/mortgage/imt-september-2025-mortgage-monitor-report-5Bbzsj9QEEEa.pdf
- **KB doc-types likely to contain answer:** ICE Mortgage Monitor (industry ref), MI 10-K risk-factor / persistency disclosure, transcript Q&A.
- **Current-agent-difficulty:** hard
  Rationale: Requires combining external ICE refi-incentive data with each issuer's WAC-of-IIF disclosure; multi-source synthesis with quantitative leg.

### Q5: How has the MI industry's penetration of the agency purchase market trended over the last eight quarters, and is private MI losing share to FHA?
- **Shape:** longitudinal
- **Source:** https://www.urban.org/sites/default/files/2026-03/February%20v3.pdf ; https://www.hud.gov/program_offices/housing/rmra/oe/rpts/fhamktsh/fhamktqtrly
- **KB doc-types likely to contain answer:** FHFA / Urban Institute / HUD industry references, MI 10-K MD&A "Industry Conditions."
- **Current-agent-difficulty:** moderate
  Rationale: Single data series across time, but spread across multiple references; the FHA-share decline and VA-share rise (FHA 33.2% → 32.0%, VA 25.6% → 30.0% Q4'24 → Q4'25 of MI composition) is the kind of longitudinal table the wiki tools handle reasonably.

### Q6: What was the first-time-homebuyer share of agency purchase originations in Q1 2025, and how did MGIC, Essent, and Radian each frame its FTHB exposure on the most recent earnings call?
- **Shape:** mixed
- **Source:** https://mortgagetech.ice.com/resources/data-reports/may-2025-mortgage-monitor
- **KB doc-types likely to contain answer:** ICE Mortgage Monitor reference, three-issuer transcript Q&A.
- **Current-agent-difficulty:** hard
  Rationale: One macro stat plus three-issuer qualitative synthesis; transcripts often bury FTHB commentary outside obvious keywords.
- **Expected-answer notes:** ICE reported FTHBs at 58% of agency purchase lending in Q1 2025, a record share. Issuers typically point to ~80%+ of NIW being FTHB-skewed.

### Q7: How does each MI issuer's geographic concentration in California and Florida compare, and which issuer carries the highest concentrated-market exposure?
- **Shape:** cross-issuer
- **Source:** https://www.fhfa.gov/ ; issuer 10-Ks
- **KB doc-types likely to contain answer:** 10-K "Geographic Concentration" tables (typically a top-10-state IIF table).
- **Current-agent-difficulty:** moderate
  Rationale: Six 10-K table lookups; tables are stable and named, so retrieval is OK if not over-trimmed.

### Q8: What is the most recent S&P Cotality Case-Shiller National HPI year-over-year reading, and which MI issuers cited it directly in their latest MD&A or earnings call?
- **Shape:** mixed
- **Source:** https://fred.stlouisfed.org/series/CSUSHPINSA ; https://www.cotality.com/press-releases/home-prices-have-fallen-for-most-of-2025
- **KB doc-types likely to contain answer:** Industry reference, six issuers' 10-K MD&A and transcripts.
- **Current-agent-difficulty:** hard
  Rationale: Cohort qualitative — which issuers explicitly cited Case-Shiller — requires careful exact-phrase retrieval; agent's known weakness in citation-attribution questions.
- **Expected-answer notes:** ~+1.3% YoY Sep 2025; +0.9% YoY Feb 2026 (slowest since July 2023).

### Q9: What does each issuer disclose about HPA assumptions in its loss-reserving methodology, and how have those assumptions changed YoY?
- **Shape:** cross-issuer + longitudinal
- **Source:** Issuer 10-K Critical Accounting Estimates sections; supplemented by https://www.cotality.com/press-releases/home-prices-have-fallen-for-most-of-2025
- **KB doc-types likely to contain answer:** 10-K Critical Accounting Estimates / Loss Reserves footnote.
- **Current-agent-difficulty:** hard
  Rationale: Six-issuer narrative retrieval with YoY comparison embedded in dense accounting policy text; high token cost, prone to trim.

### Q10: How have MGIC and Radian framed the impact of FHFA's 2026–2028 enterprise housing goals on conventional MI demand?
- **Shape:** qualitative + cross-issuer
- **Source:** https://www.federalregister.gov/documents/2025/12/23/2025-23746/2026-2028-enterprise-housing-goals ; https://www.housingwire.com/articles/fhfa-housing-goals-2026-2028/
- **KB doc-types likely to contain answer:** Two issuers' transcripts (Q&A on regulatory backdrop), 10-K Regulation/Risk Factors.
- **Current-agent-difficulty:** hard
  Rationale: Specific regulatory event (Very-Low-Income purchase goal cut from 6% to 3.5%); two-issuer qualitative pull; framing rarely uses exact MBA terminology.

### Q11: For the most recent quarter, what was MGIC's NIW from refinances vs. purchase, and how does the refi mix compare to the same quarter one year ago?
- **Shape:** longitudinal (single-issuer)
- **Source:** https://mtg.mgic.com/events-and-presentations
- **KB doc-types likely to contain answer:** MGIC 10-Q, earnings supplement, investor presentation.
- **Current-agent-difficulty:** easy
  Rationale: Classic single-issuer point-in-time + YoY comparison the agent does well on.

### Q12: Across the cohort, which issuer disclosed the highest weighted-average FICO and lowest weighted-average LTV on its 2024–2025 NIW vintages?
- **Shape:** cross-issuer
- **Source:** https://www.milliman.com/en/insight/pmi-market-trends-2q-2025 ; six issuers' 10-Ks
- **KB doc-types likely to contain answer:** 10-K Risk-in-Force tables, investor decks, MIPC compliance disclosures.
- **Current-agent-difficulty:** hard
  Rationale: Six-issuer numeric retrieval over similarly-named tables; ranking-style question prone to chunk trim losing entire issuers.
- **Expected-answer notes:** MGIC 2025 originations weighted-avg FICO ~755, >50% with FICO ≥760.

### Q13: How sensitive is MI NIW to a 100 bps decline in 30-year fixed rates, based on the issuers' own scenario commentary, and how does this square with Fannie Mae's "rates below 6% by end-2026" base case?
- **Shape:** mixed
- **Source:** https://www.fanniemae.com/newsroom/fannie-mae-news/mortgage-rates-expected-move-below-6-percent-end-2026
- **KB doc-types likely to contain answer:** Transcript Q&A across issuers, MI 10-K Risk Factors.
- **Current-agent-difficulty:** hard
  Rationale: Quantitative-qualitative blend across multiple issuers; sensitivity disclosure usually lives in transcript Q&A and is easy to miss in retrieval ranking.

### Q14: Within the most recent quarter's earnings calls, which CEOs explicitly described the MI industry as in a "price war" or "competitive pricing" environment, and how did each contrast its strategy?
- **Shape:** cross-issuer + qualitative
- **Source:** https://www.nationalmortgagenews.com/list/mi-volumes-jump-12-competitive-pressure-builds
- **KB doc-types likely to contain answer:** Six issuers' transcripts.
- **Current-agent-difficulty:** hard
  Rationale: Exact attribution across multiple transcripts; classic synthesis-genericness failure where the agent paraphrases instead of pinning quotes to issuers (e.g., Casale/Essent on "unit economics not price game"; Mattke/MGIC on "discipline").

### Q15: How has VA loan share of low-down-payment originations evolved 2023–2025, and which MI issuer has the most-explicit competitive-positioning language vs. VA?
- **Shape:** longitudinal + cross-issuer
- **Source:** https://www.urban.org/sites/default/files/2026-03/February%20v3.pdf
- **KB doc-types likely to contain answer:** Urban Institute / FHFA references; MI 10-K "Industry Conditions" section.
- **Current-agent-difficulty:** moderate
  Rationale: Public reference data + qualitative single-source pull; mid-tier difficulty.
- **Expected-answer notes:** VA share of MI composition rose from 25.6% → 30.0% Q4'24→Q4'25.

### Q16: What is each issuer's disclosed insurance-in-force (IIF) at year-end 2025, and which crossed key thresholds (e.g., MGIC $300B, Essent $221B)?
- **Shape:** cross-issuer
- **Source:** https://www.nationalmortgagenews.com/list/mi-volumes-jump-12-competitive-pressure-builds
- **KB doc-types likely to contain answer:** Six issuers' 10-K Selected Operating Data.
- **Current-agent-difficulty:** moderate
  Rationale: Six-issuer numeric pull; standard table; only failure mode is over-trimming the cohort.
- **Expected-answer notes:** MGIC ~$303B (+3% YoY); Essent ~$221.4B record; National MI ~$221B; others lower.

### Q17: How did regional housing-market divergence (Northeast/Midwest appreciation vs. West/Florida softness) show up in any MI issuer's commentary on delinquency or geographic risk in 2025?
- **Shape:** qualitative + cross-issuer
- **Source:** https://www.cotality.com/press-releases/home-prices-have-fallen-for-most-of-2025
- **KB doc-types likely to contain answer:** Transcripts Q&A, 10-K Risk Factors / MD&A on geographic concentration.
- **Current-agent-difficulty:** hard
  Rationale: Synthesis across issuers on a directional macro narrative; agent tends to produce generic commentary on cohort qualitative questions.

### Q18: How do issuer-disclosed refi-share-of-NIW figures track Fannie Mae's projection that refi rises from 26% of total originations in 2025 to 35% in 2026?
- **Shape:** longitudinal + cross-issuer
- **Source:** https://www.fanniemae.com/newsroom/fannie-mae-news/mortgage-rates-expected-move-below-6-percent-end-2026
- **KB doc-types likely to contain answer:** Six issuers' MD&A NIW-mix table; Fannie Mae industry reference.
- **Current-agent-difficulty:** hard
  Rationale: Cohort numeric pull plus reconciliation against external benchmark; multi-source synthesis is exactly where the agent struggles.

### Q19: Which MI issuers have explicitly cited MBA, Fannie Mae, or ICE Mortgage Technology data in MD&A "Industry Conditions" sections of their FY24 10-Ks, and which sources are favored by which issuer?
- **Shape:** cross-issuer + qualitative
- **Source:** Issuer 10-Ks
- **KB doc-types likely to contain answer:** Six 10-K MD&A "Industry Conditions" / "Mortgage Insurance Market" sections.
- **Current-agent-difficulty:** moderate
  Rationale: Citation-presence question; benefits from exact-string retrieval but six-issuer scope creates trim risk.

### Q20: What is each issuer's stated outlook for 2026 NIW relative to 2025, and how does it square with the MBA's $1.46T purchase forecast plus $737B refi forecast?
- **Shape:** cross-issuer + qualitative
- **Source:** https://www.mba.org/news-and-research/newsroom/news/2025/10/19/mba-forecast--total-single-family-mortgage-originations-to-increase-8-percent-to--2.2-trillion-in-2026
- **KB doc-types likely to contain answer:** Six issuers' 4Q25 / FY25 transcripts and investor decks.
- **Current-agent-difficulty:** hard
  Rationale: Cohort forward-looking qualitative pull plus reconciliation against an external forecast — combines all three failure modes (cohort, synthesis, multi-source).

## Capability gaps observed

Q2, Q12, Q14, Q16, and Q20 are textbook cohort-retrieval problems for the current agent. Each requires pulling matching disclosures from six issuers — NIW figures, FICO/LTV mix, executive quotes on competitive pricing, IIF totals, forward outlook. The known >60K-token trim behavior tends to drop one or two issuers from the synthesis, producing answers that look complete but silently omit (typically) NMIH or ACT because the wiki/transcript chunks for those smaller issuers are deprioritized in ranking.

Q3, Q9, Q14, and Q17 layer qualitative cohort synthesis on top of cross-issuer retrieval. Persistency narrative, HPA-assumption changes, "price war" framing, and regional-divergence commentary are exactly where the agent's documented synthesis-genericness shows up — the answer paraphrases the consensus instead of pinning each statement to the issuer that said it. Direct-quote attribution should be the eval target here.

Q4, Q10, Q13, Q18, and Q20 require reconciling internal disclosure with an external benchmark (ICE refi-incentive data, FHFA goals, Fannie's rate path, MBA's purchase/refi split). The agent does well on either leg in isolation but tends to under-cite the external reference and produce a single-source answer when the question is explicitly multi-source. These are the most diagnostic items for testing whether industry-reference docs in the KB are actually being retrieved alongside issuer filings.
