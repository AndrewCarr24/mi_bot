# Credit & delinquency

## Why this matters to MI analysts

Credit performance is the single largest driver of P&L volatility for the six US private MIs. The income statement is dominated by the loss ratio, and the loss ratio in turn is a function of the new-notice rate, cure-vs-claim mix on the delinquency inventory, and severity at claim. An MI analyst spends most of their day triangulating: (a) the *level* of the default rate (e.g., MGIC 2.10s, ESNT 2.50, NMI 1.17 entering 2026), (b) the *vintage mix* of new notices (post-2021 cohorts now season into peak default years 3-7), and (c) the recurrence of *favorable reserve development* — which has been a structural earnings tailwind for MGIC and Essent for eight consecutive quarters.

Beyond the headline rate, analysts care about the tails: hurricane/wildfire concentrations in FL/CA/TX, the proportion of new defaults that are "FEMA-flagged" and therefore likely to cure, RIF distribution by FICO band and LTV band (which feeds PMIERs Minimum Required Assets), claim severity drift as 2021-2024 vintages bring higher loan sizes into the claim cohort, and IBNR/case-reserve adequacy. Cohort-level disclosure varies wildly across the six issuers — MGIC and Radian provide the most granular vintage tables; NMI and Enact provide less — making cross-issuer questions an important and difficult class of inquiry.

## Sources consulted
- https://www.usmi.org/wp-content/uploads/2023/11/Private-MI-Resiliency-White-Paper-11.08.23.pdf
- https://www.milliman.com/en/insight/pmi-market-trends-2q-2025
- https://www.milliman.com/en/insight/pmi-market-trends-1q-2025
- https://www.nationalmortgagenews.com/list/mgic-radian-enact-essent-nmih-arch-report-2q-results
- https://www.nationalmortgagenews.com/list/mi-volumes-jump-12-competitive-pressure-builds
- https://www.fool.com/earnings/call-transcripts/2026/02/13/essent-group-esnt-q4-2025-earnings-transcript/
- https://www.fool.com/earnings/call-transcripts/2026/04/30/mgic-mtg-q1-2026-earnings-call-transcript/
- https://news.alphastreet.com/mgic-investment-corporation-mtg-q3-2025-earnings-call-transcript/
- https://www.investing.com/news/transcripts/earnings-call-transcript-essent-group-q3-2025-misses-eps-forecast-stock-falls-93CH-4343244
- https://ir.nationalmi.com/news-releases/news-release-details/nmi-holdings-inc-reports-fourth-quarter-and-full-year-2025
- https://www.fhfa.gov/policy/pmiers
- https://www.fhfaoig.gov/sites/default/files/WPR-2025-001.pdf
- https://www.radian.com/-/media/Files/Enterprise/Investor-Relations/Quarterly-Results/10K/RDN10K2025-22026-427pm-FINAL-FILED.pdf
- https://www.globenewswire.com/news-release/2025/10/30/3177955/0/en/Enact-Mortgage-Insurance-Enters-Into-a-Forward-XOL-Reinsurance-Transaction-as-Part-of-its-Diversified-Credit-Risk-Transfer-Program.html
- https://www.urban.org/sites/default/files/2023-08/Mortgage%20Insurance%20Data%20At%20A%20Glance%202023.pdf

## Questions

### Q1: What was MGIC's primary default rate at year-end 2024 and 2025, and how did the size of the delinquency inventory change?
- **Shape:** longitudinal
- **Source:** https://www.fool.com/earnings/call-transcripts/2026/02/05/ (MGIC Q4 2025 transcript) and 10-K Selected Financial Data
- **KB doc-types likely to contain answer:** MGIC 10-K 2024 and 2025 (Item 7 MD&A "Insurance in Force and Risk in Force"; Item 8 financial supplements), Q4 2024 and Q4 2025 8-K earnings releases
- **Current-agent-difficulty:** easy
  Rationale: Single issuer, two point-in-time numbers from a standard 10-K table.
- **Expected-answer notes:** ~26,791 delinquent loans at YE 2024 per MGIC 10-K; default rate ~2.10s at YE 2024, low-2s at YE 2025.

### Q2: Across the six MIs, rank year-end 2025 primary default rates and identify the issuer with the largest year-over-year increase.
- **Shape:** cross-issuer
- **Source:** https://www.milliman.com/en/insight/pmi-market-trends-2q-2025 plus each issuer's Q4 2025 8-K
- **KB doc-types likely to contain answer:** Q4 2024 and Q4 2025 earnings press release 8-Ks for ACGL, ACT, ESNT, MTG, NMIH, RDN; financial supplements
- **Current-agent-difficulty:** hard
  Rationale: Six-issuer cohort retrieval from earnings releases — the agent's known failure mode (>60K tokens, often misses one issuer and synthesizes as complete).
- **Expected-answer notes:** Essent ~2.50% (largest YoY rise), NMI ~1.17% (lowest), MGIC ~2.1, Radian and Enact in between.

### Q3: How did MGIC's favorable reserve development evolve quarter-by-quarter through 2024-2025, and which delinquency notice vintages drove it?
- **Shape:** longitudinal
- **Source:** https://www.fool.com/earnings/call-transcripts/2026/04/22/mgic-mtg-q3-2024-earnings-call-transcript/ and subsequent quarterly transcripts
- **KB doc-types likely to contain answer:** MGIC TRANSCRIPT Q3 2024, Q4 2024, Q1-Q4 2025; 10-Q "Losses Incurred" footnote; 10-K Note on loss reserves
- **Current-agent-difficulty:** moderate
  Rationale: Five-quarter longitudinal series; transcripts contain explicit numbers but agent may need multiple retrievals and could double-count.
- **Expected-answer notes:** $66M Q3 2024, $54M Q2 2025, $47M Q3 2025, $31M Q4 2025, $31M Q1 2026; primarily 2022-2024 notices with rising 2024-2025 contribution.

### Q4: For each MI, what is the disclosed sensitivity of loss reserves to a 1-percentage-point change in the assumed claim rate?
- **Shape:** cross-issuer
- **Source:** 10-K critical accounting estimates section (each issuer)
- **KB doc-types likely to contain answer:** 10-K FY 2024 Item 7 "Critical Accounting Estimates - Loss Reserves" for ACGL, ACT, ESNT, MTG, NMIH, RDN
- **Current-agent-difficulty:** hard
  Rationale: Six-issuer retrieval into a specific MD&A subsection that's worded differently by each issuer; ranking-miss risk is high.
- **Expected-answer notes:** Each MI discloses a sensitivity table; figures range mid-eight to low-nine figures for a 100 bp claim-rate shock.

### Q5: How does Essent characterize the credit performance of its 2021 and earlier vintages versus 2022+ vintages, and what share of Q4 2025 defaults came from pre-2022 books?
- **Shape:** point-in-time
- **Source:** https://www.fool.com/earnings/call-transcripts/2026/02/13/essent-group-esnt-q4-2025-earnings-transcript/
- **KB doc-types likely to contain answer:** ESNT TRANSCRIPT Q4 2025; ESNT Q4 2025 8-K supplement
- **Current-agent-difficulty:** easy
  Rationale: Single-issuer, single-quarter quote.
- **Expected-answer notes:** ~70% of defaults from 2021 or earlier; mark-to-market LTV ~61%; management said no material vintage divergence.

### Q6: Compare RIF distribution by FICO band (≥760, 720-759, 680-719, <680) at year-end 2025 across MGIC, Radian, Essent, and NMI.
- **Shape:** cross-issuer
- **Source:** Each issuer's Q4 2025 financial supplement and 10-K Item 1 "Risk in Force by FICO"
- **KB doc-types likely to contain answer:** 10-K FY 2025 (or Q4 2025 8-K supplement) for ACGL/ACT/ESNT/MTG/NMIH/RDN
- **Current-agent-difficulty:** hard
  Rationale: Four-issuer table-stitching; FICO bands sometimes bucketed differently, requires alignment. Tables likely indexed but answer requires column-by-column compare.
- **Expected-answer notes:** All four >55% RIF in 760+ bucket; sub-680 typically <3% of RIF.

### Q7: What is the primary RIF distribution by mark-to-market LTV at year-end 2025 for the cohort, and how many issuers report effective LTV under 80%?
- **Shape:** cross-issuer
- **Source:** Issuer financial supplements; USMI resiliency white paper (https://www.usmi.org/wp-content/uploads/2023/11/Private-MI-Resiliency-White-Paper-11.08.23.pdf) for context
- **KB doc-types likely to contain answer:** 10-K FY 2025 Item 1; Q4 2025 8-K supplements; USMI_RESILIENCY
- **Current-agent-difficulty:** hard
  Rationale: Cohort retrieval where some issuers report original LTV only, requires careful reading.
- **Expected-answer notes:** Essent disclosed ~61% portfolio MTM LTV in Q4 2025; most peers report 60-70% range due to HPA.

### Q8: How did Essent's quarterly new notices, cures, and net default inventory move through 2025, and what was the Q4 2025 net inventory change?
- **Shape:** longitudinal
- **Source:** https://www.essent.us/sites/default/files/2025-11/full-earnings-release-3q25.pdf and Q4 2025 release
- **KB doc-types likely to contain answer:** ESNT 8-K earnings releases Q1-Q4 2025; 10-K 2025; transcripts Q1-Q4 2025
- **Current-agent-difficulty:** moderate
  Rationale: Four-quarter trend in a single issuer — feasible if agent retrieves the right supplements; ranking risk on press release vs supplement.
- **Expected-answer notes:** Q4 2025 inventory rose to 20,210 from 18,583; 11,245 new defaults vs 9,357 cures.

### Q9: What was MGIC's IBNR reserve at year-end 2024, and how does it compare to its case reserves on its delinquency inventory?
- **Shape:** point-in-time
- **Source:** MGIC 10-K 2024 Note "Loss Reserves"
- **KB doc-types likely to contain answer:** MTG 10-K FY 2024 and FY 2025; 10-Qs
- **Current-agent-difficulty:** easy
  Rationale: Single-issuer, single-document line item.
- **Expected-answer notes:** IBNR ~$29M at YE 2024 against ~26,791 loans in delinquency inventory.

### Q10: For Q3 2024 hurricane season (Helene and Milton), how did each MI quantify FEMA-declared-disaster default activity in its Q3 2024 disclosures, and what was management's expectation about cure rates on those notices?
- **Shape:** cross-issuer qualitative
- **Source:** Q3 2024 earnings releases and transcripts for ACGL/ACT/ESNT/MTG/NMIH/RDN
- **KB doc-types likely to contain answer:** Q3 2024 8-K earnings supplements; TRANSCRIPT Q3 2024; possibly 10-Q for Q3 2024 risk factors
- **Current-agent-difficulty:** hard
  Rationale: Multi-issuer qualitative on a specific event; some issuers buried it in MD&A "natural disasters" sub-section, others addressed only in Q&A. Item-code 8-K issue may apply if non-press-release exhibits used.
- **Expected-answer notes:** Each MI typically discloses elevated FL new notices and historically high cure rates (often 70%+) on FEMA-flagged defaults.

### Q11: Quote and explain MGIC management's commentary on why claim severity is drifting upward in recent vintages.
- **Shape:** qualitative
- **Source:** https://www.fool.com/earnings/call-transcripts/2026/04/30/mgic-mtg-q1-2026-earnings-call-transcript/
- **KB doc-types likely to contain answer:** MTG TRANSCRIPT Q1 2026 (and Q4 2025); 10-K MD&A
- **Current-agent-difficulty:** moderate
  Rationale: Single-issuer Q&A pull, but the relevant exchange is buried in dialogue and easily out-ranked by boilerplate severity language in 10-K Risk Factors.
- **Expected-answer notes:** Colson — vintage mix toward 2023-2025 with much higher loan amounts; severity ↑ even as claim rate stays low.

### Q12: How does MGIC's geographic concentration (top 5 states by RIF) compare to NMI Holdings at year-end 2025, and which states are most exposed to hurricane risk?
- **Shape:** cross-issuer
- **Source:** MGIC 10-K 2025 Item 1; NMIH 10-K 2025 Item 1; Q4 2025 8-K supplements
- **KB doc-types likely to contain answer:** MTG 10-K FY 2025; NMIH 10-K FY 2025; financial supplements
- **Current-agent-difficulty:** moderate
  Rationale: Two-issuer table compare with hurricane-state callout; agent must retrieve geographic table and may miss Texas/Florida overlap.
- **Expected-answer notes:** CA, TX, FL typically top three at both; FL ~6-8% RIF, TX ~7-10%; both have hurricane exposure.

### Q13: What did the Nov 2023 USMI resiliency white paper conclude about the post-2008 vintage default progression versus pre-2008 vintages, and what excess-capital sufficiency ratio did USMI report?
- **Shape:** point-in-time qualitative
- **Source:** https://www.usmi.org/wp-content/uploads/2023/11/Private-MI-Resiliency-White-Paper-11.08.23.pdf
- **KB doc-types likely to contain answer:** USMI_RESILIENCY white paper
- **Current-agent-difficulty:** easy
  Rationale: Single document, well-structured headline statistics.
- **Expected-answer notes:** ~169% PMIERs sufficiency; $11B excess capital; post-2008 cumulative default rates a fraction of 2005-2007 vintages.

### Q14: What is the cumulative count of insurance-linked notes (ILNs) and amount of risk transferred reported by USMI through 2024, and how many of those ILNs are sponsored by Enact?
- **Shape:** mixed
- **Source:** https://www.usmi.org/data/credit-risk-transfer/ ; https://www.globenewswire.com/news-release/2025/10/30/3177955/
- **KB doc-types likely to contain answer:** USMI_RESILIENCY; ACT 8-K announcements 2024-2025; ACT 10-K FY 2025 reinsurance footnote
- **Current-agent-difficulty:** moderate
  Rationale: Cross-source synthesis — one count from USMI (industry total), one count from Enact disclosure. Risk of mis-attribution.
- **Expected-answer notes:** USMI: ~56 ILN transactions, ~$22.3B risk transferred; Enact has multiple Triangle Re ILNs plus 2025 forward XOL ($225M and $260M).

### Q15: For Radian, what was the average reserve per primary default at year-end 2024 and year-end 2025, and how does that compare to MGIC and Essent?
- **Shape:** cross-issuer
- **Source:** Each issuer's 10-K loss reserve disclosure / financial supplement (computed: case reserve ÷ delinquent loan count)
- **KB doc-types likely to contain answer:** RDN 10-K FY 2024 and 2025; MTG 10-K FY 2024 and 2025; ESNT 10-K FY 2024 and 2025; Q4 8-K supplements
- **Current-agent-difficulty:** hard
  Rationale: Requires arithmetic across three issuers and two years, with case-reserve and delinquency counts often in different tables; ranking miss risk.
- **Expected-answer notes:** Typically $20-30K per default, drifting up as severity rises.

### Q16: Across the cohort, summarize 2025 commentary on whether 2020-2021 COVID-era originations are now exhibiting cure-rate behavior in line with pre-pandemic peer cohorts.
- **Shape:** qualitative cross-issuer
- **Source:** Q4 2025 transcripts for the six MIs
- **KB doc-types likely to contain answer:** TRANSCRIPT Q4 2025 for ACGL, ACT, ESNT, MTG, NMIH, RDN; possibly 10-K MD&A
- **Current-agent-difficulty:** hard
  Rationale: Synthesis across six transcripts — a known weakness on qualitative cohort questions where the agent often produces generic answers.
- **Expected-answer notes:** Generally yes — cure rates on 2020-2021 vintages in line or modestly better; some forbearance "noise" persisting.

### Q17: Which MI disclosed the highest concentration of RIF in single-premium policies at year-end 2024, and is that mix associated with different cure/claim economics?
- **Shape:** mixed
- **Source:** Each issuer's 10-K Item 1 "Premium Plan" or financial supplement
- **KB doc-types likely to contain answer:** 10-K FY 2024 Item 1 for all six MIs; 10-Q segment notes
- **Current-agent-difficulty:** hard
  Rationale: Cohort retrieval into a less-frequently-asked sub-disclosure; "single premium" is an XBRL tag plus narrative; agent's TextBlock filter may help but cohort coverage gaps likely.
- **Expected-answer notes:** Essent and NMI have meaningful single-premium share; MGIC primarily monthly; mix affects unearned-premium accounting and rescission economics.

### Q18: What does Radian's 2024 10-K say about its Insured Risk by Year of Origination, and how is the 2020-2022 vintage performing relative to the 2007 vintage at the same age?
- **Shape:** longitudinal
- **Source:** https://www.radian.com/-/media/Files/Enterprise/Investor-Relations/Quarterly-Results/10K/ (Radian 10-K)
- **KB doc-types likely to contain answer:** RDN 10-K FY 2024 Item 1 vintage tables; supplemental
- **Current-agent-difficulty:** moderate
  Rationale: Single 10-K, but vintage tables are wide and the comparison is interpretive — agent must align "loan age" not calendar year.
- **Expected-answer notes:** 2020-2022 cumulative defaults at age 3-5 well below 2005-2007 at the same age.

### Q19: How does PMIERs treat delinquent loans differently than performing loans for Minimum Required Assets, and does the 2024 PMIERs revision change that treatment?
- **Shape:** qualitative
- **Source:** https://www.fhfa.gov/policy/pmiers ; https://www.fhfa.gov/news/news-release/fannie-mae-and-freddie-mac-update-their-private-mortgage-insurer-eligibility-requirements-2024
- **KB doc-types likely to contain answer:** PMIERS_BASE; PMIERS_2024_01; PMIERS_2024_02; possibly USMI_RESILIENCY
- **Current-agent-difficulty:** moderate
  Rationale: PMIERs documents are dense; the agent must locate the specific MRA factor table for delinquent loans across two amendments.
- **Expected-answer notes:** Delinquent loans carry materially higher MRA factors based on months in default; 2024 revision tightened asset-quality definition rather than delinquency factors.

### Q20: What is the cohort-wide trend in claims paid (dollar amount) for 2023, 2024, and 2025, and which MI paid the largest dollar amount of claims in 2025?
- **Shape:** longitudinal cross-issuer
- **Source:** 10-K Cash Flow / Loss Triangle for each issuer; financial supplements
- **KB doc-types likely to contain answer:** 10-K FY 2023, 2024, 2025 for ACGL/ACT/ESNT/MTG/NMIH/RDN; "Claims Paid" line in supplemental
- **Current-agent-difficulty:** hard
  Rationale: Six issuers × three years = 18 data points; high token cost and exactly the regime where the agent drops issuers.
- **Expected-answer notes:** Claims paid remained low single-digit millions per quarter for most MIs through 2024, ticking up in 2025 as some 2022 notices roll to claim; MGIC and Radian likely largest absolute dollar amounts given larger books.

## Capability gaps observed

The largest gap is **cross-issuer cohort coverage** (Q2, Q4, Q6, Q15, Q16, Q20). With six MIs and multi-year disclosure each, full retrieval pushes well past the 60K-token failure threshold flagged in known issues. Synthesis quality also degrades on qualitative cohort questions (Q10, Q16) where each issuer's wording differs and the agent tends to produce generic boilerplate rather than tracking specific issuer-by-issuer language.

A second gap is **transcript Q&A retrieval against 10-K boilerplate** (Q3, Q11). Loss-reserve and claim-severity language exists in three places — Risk Factors (formulaic), MD&A (prior-period numerical), and the transcript exchange (the *current* explanation). The agent's ranker historically prefers Risk Factors prose; the analyst nearly always wants the transcript Q&A, so a question phrased as "how did management explain..." should pull TRANSCRIPT first.

A third gap is **cross-document synthesis between USMI/PMIERs/issuer 10-K** (Q14, Q19). These questions need one fact from a regulatory document and one from an issuer-specific source. The agent tends to retrieve only one source-type per query and either misses the regulatory grounding or misses the issuer-level number.
