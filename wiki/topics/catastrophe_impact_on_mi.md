# Catastrophe Impact on MI

> Natural disasters affect U.S. private mortgage insurance through three distinct channels: (1) immediate increases in delinquencies in disaster-affected geographies (typically driven by FEMA-declared major disaster areas); (2) the master-policy provisions that allow MIs to exclude or adjust claims where the property damage was the proximate cause of default and to require the home to be habitable before paying a claim; and (3) the PMIERs 0.30x multiplier on the risk-based required asset factor for non-performing loans backed by properties in FEMA-Declared Major Disaster Areas eligible for individual assistance, which reduces required PMIERs capital while the loan remains in disaster-related forbearance or recovery (INDUSTRY_PMIERS_GUIDANCE_2024-02). The 0.30x disaster multiplier was originally codified in PMIERs guidance effective June 30, 2020, with a parallel COVID-era extension that was discontinued effective March 31, 2025; the FEMA-disaster baseline remains in effect (INDUSTRY_PMIERS_GUIDANCE_2024-02). In 2024-2025, two events tested the framework: Hurricane Helene (September 26, 2024) and Hurricane Milton (October 9, 2024) drove a Q4 2024 step-up in delinquencies — Essent identified 2,119 hurricane-related defaults among its 3,620-loan year-over-year increase (ESNT_10-K_2025-12-31) — but cure rates on disaster-related defaults have historically been very high. The January 2025 California wildfires affected less than 0.1% of Essent's IIF and did not have a material impact on reserves (ESNT_10-K_2025-12-31). The Q4 2025 Hurricane Melissa was one factor in Arch's $164 million of Q4 2025 catastrophe losses, but Arch management framed full-year 2025 as having "only one major cat" — the California wildfires — a benign year by reinsurance-cycle standards (ACGL_TRANSCRIPT_2025-12-31).

## What it is

Three structural mechanisms shape how natural disasters affect MI economics.

**Master-policy claim provisions.** Under each MI's master policy, the MI is generally permitted to exclude a claim entirely where damage to the property underlying a mortgage was the proximate cause of the default, and to adjust a claim where the property is subject to unrestored physical damage. Mortgage insurance does not provide protection against property loss or physical damage from hurricanes or other severe weather events; that is the function of hazard and flood insurance (RDN_10-K_2025-12-31; ESNT_10-K_2025-12-31; INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09). Enact's transcript framing is that "our MI policy excludes property damage, it requires homes to be habitable before we pay a claim" (ACT_TRANSCRIPT_2024-12-31). This means an MI's exposure to disaster-driven delinquency is materially less than the headline delinquency rate would suggest.

**PMIERs treatment of disaster-related delinquencies.** Under PMIERs Exhibit A, Table 8, footnote 1 (as restated by Guidance 2024-02), MIs apply a **0.30x multiplier** to the risk-based required asset amount factor for each insured loan in default backed by a property in a FEMA-Declared Major Disaster Area eligible for Individual Assistance, provided the loan either (i) is subject to a forbearance plan with terms materially consistent with Fannie Mae or Freddie Mac forbearance plans, or (ii) has an initial missed payment within 30 days before through 90 days after the FEMA-declared incident period (capped at 180 days from the start of the incident period) (INDUSTRY_PMIERS_GUIDANCE_2024-02 Section I.a).

The 0.30x multiplier is applied for a defined window:

- **In the case of forbearance (clause 1)**: relief applies until the earlier of (i) the date the loan is reported as no longer in such forbearance plan, repayment plan, or loan modification trial period, or (ii) **18 months** following the date of the initial missed monthly payment (INDUSTRY_PMIERS_GUIDANCE_2024-02 Section I.a).
- **In the case of incident-period proximity (clause 2), absent a forbearance plan**: the 0.30x multiplier applies for **no longer than three calendar months** beginning with the month the loan reaches two missed monthly payments (INDUSTRY_PMIERS_GUIDANCE_2024-02 Section I.a).

The mechanical effect: the risk-based required asset amount factor for the non-performing loan becomes the **greater of** (a) the factor for a performing loan if it weren't delinquent, or (b) 0.30 × the standard non-performing loan factor (INDUSTRY_PMIERS_GUIDANCE_2024-02 Section I.a). The recognition behind the multiplier is that disaster-driven non-performing loans "generally have a higher likelihood of curing following the conclusion of the event" (RDN_10-K_2025-12-31).

**GSE forbearance frameworks.** Both Fannie Mae and Freddie Mac require servicers to offer disaster-related forbearance of up to 12 months for borrowers in FEMA-Designated Areas (depending on factors including the delinquency status of the loan at the time of the disaster) (RDN_10-K_2025-12-31). At the conclusion of any applicable forbearance term, a borrower may bring the loan current, defer missed payments until the end of the loan, or have the loan modified through a change in payments or extension of term (RDN_10-K_2025-12-31). Historically, MIs have seen forbearance plans used for disaster-affected loans with forbearance limited to 12 months (RDN_10-K_2025-12-31).

In aggregate, the combination of master-policy exclusions, the PMIERs 0.30x multiplier, and the disaster-forbearance framework means that the **headline delinquency increase from a hurricane or wildfire substantially overstates the ultimate claim impact**. Industry experience is that hurricane-related defaults historically have a lower default-to-claim conversion rate than non-hurricane-related defaults (ESNT_10-K_2025-12-31; ACT_TRANSCRIPT_2024-12-31).

## Why it matters

Three reasons catastrophe risk is operationally relevant for MI analysts.

**First, disaster-driven delinquency spikes are noisy but ultimately small in claims terms.** Q4 2024 hurricane activity (Helene + Milton) produced visible step-ups in delinquencies at multiple MIs, but the 0.30x multiplier and master-policy exclusions limit the through-flow to the loss ratio. Essent applied "a lower estimated claim rate to new default notices received in the fourth quarter of 2024 from the affected areas than the claim rate we apply to other notices in our default inventory" — and management's expectation is that "the ultimate number of hurricane-related defaults that result in claims will be less than the default-to-claim experience of non-hurricane-related defaults" (ESNT_10-K_2025-12-31). Enact applied a 2% claim rate to hurricane-related delinquencies vs. its 9% standard claim rate on new delinquencies, reflecting historically high cure rates (ACT_TRANSCRIPT_2024-12-31).

**Second, geographic concentration matters for the size of any single-event exposure**. Hurricane Milton affected only Florida; Hurricane Helene affected Florida, Georgia, South Carolina, North Carolina, Tennessee, and Virginia (ESNT_10-K_2025-12-31). The January 2025 California wildfires affected less than 0.1% of Essent's IIF in FEMA-disaster-declared areas — limiting the materiality of that event for MI insurers (ESNT_10-K_2025-12-31). Hurricane Melissa was one of the cat events contributing to Arch's $164 million Q4 2025 catastrophe loss recognition (alongside U.S. severe convective storms and a series of global events), but Arch's full-year 2025 cat losses were materially below seasonally adjusted expectations because "we had only one major cat, which was the California wildfires" (ACGL_TRANSCRIPT_2025-12-31).

**Third, the cycle interaction with Arch's broader (P&C / specialty) book is different from the monoline MIs**. For Arch, USMI cat losses are a small component of group-level cat exposure; the company's peak-zone net 1-in-250 PML is $1.9 billion (8.2% of tangible shareholders' equity) and is largely driven by P&C / specialty cat exposures, not USMI (ACGL_TRANSCRIPT_2025-12-31). The five monoline MIs (Enact, Essent, MGIC, NMI, Radian) have meaningfully smaller direct cat exposure but face the indirect risk of disaster-driven regional housing-market stress that could degrade home values and increase default-to-claim conversion outside the immediate disaster window — a longer-term risk that climate change is expected to increase the frequency and severity of (RDN_10-K_2025-12-31).

The Industry's framing in INDUSTRY_USMI_RESILIENCY_2023-11 is that the post-2008 reforms — Master Policy clarity, Rescission Relief Principles, regular GSE-MI dialogue on emerging risk trends — make the industry well-positioned to handle disaster events: each MI company has released specific announcements concerning the treatment of loans impacted by recent natural-disaster events and the COVID-19 pandemic.

## Current state (as of 2025-12-31)

**Hurricane Helene + Milton (Q4 2024) — through-2025 status:**
- **Affected geography**: Helene (September 26, 2024): FL, GA, SC, NC, TN, VA; Milton (October 9, 2024): FL (ESNT_10-K_2025-12-31).
- **Default impact at Essent**: 2,119 hurricane-related defaults out of a 3,620-loan year-over-year increase in defaults in 2024 (i.e., approximately 58% of the YoY increase) (ESNT_10-K_2025-12-31).
- **Default impact at Enact**: of Enact's approximately 13,700 new delinquencies received in Q4 2024 (with total delinquencies increasing sequentially from 21,000 to 23,600 as new delinquencies outpaced cures), an estimated 1,000 were hurricane-related; Enact applied a 2% claim rate to hurricane-related delinquencies (vs. its 9% standard claim rate on new delinquencies), reflecting the historically high cure rate (ACT_TRANSCRIPT_2024-12-31).
- **Reserve treatment**: Essent applied a lower estimated claim rate to Q4 2024 affected-area defaults than to other defaults; Enact applied a 2% claim rate to hurricane-related notices (ESNT_10-K_2025-12-31; ACT_TRANSCRIPT_2024-12-31).

**January 2025 California wildfires:**
- **Affected geography**: Southern California (ESNT_10-K_2025-12-31).
- **Exposure**: Essent's IIF in FEMA-declared affected areas was less than 0.1% of total IIF; "did not have a material impact on our reserves" (ESNT_10-K_2025-12-31).
- **Q4 2024 / 2025 cycle context**: Arch management framed 2025 as a year with "only one major cat, which was the California wildfires" — supporting record reinsurance-segment results across the broader P&C cycle (ACGL_TRANSCRIPT_2025-12-31).

**Q4 2025 Hurricane Melissa and other events:**
- **Arch Q4 2025 catastrophe losses**: $164 million net of reinsurance and reinstatement premiums — "lower than our seasonally adjusted expectations, but higher than last quarter, mostly as a result of U.S. severe convective storms, hurricane Melissa, and a series of global events" (ACGL_TRANSCRIPT_2025-12-31).
- **For the five monoline MIs**: no material discrete catastrophe loss recognition in Q4 2025 above seasonal patterns; Q4 2025 cure activity remained strong across the industry, with MGIC reporting $31 million of Q4 2025 favorable loss reserve development and Radian reporting $35 million of Q4 favorable reserve development (MTG_TRANSCRIPT_2025-12-31; RDN_TRANSCRIPT_2025-12-31).

**Industry-level defaults at YE2025** (some of which include residual Q4 2024 hurricane-related cases that have not yet cured):

| MI | YE 2025 Default Inventory | YE 2024 |
|---|---|---|
| MGIC | (delinquency rate 2.43%) | 2.40% |
| Radian | ~25,000 | n/a |
| Essent | 20,210 | 18,439 |
| Enact (UMI) | (default rate 2.4% range) | n/a |
| Arch (USMI) | (delinquency rate 2.17%) | n/a |
| NMI | 7,661 | n/a |

(MTG_10-K_2025-12-31; RDN_TRANSCRIPT_2025-12-31; ESNT_10-K_2025-12-31; ACGL_TRANSCRIPT_2025-12-31; NMIH_TRANSCRIPT_2025-12-31).

**PMIERs 0.30x multiplier status (as of YE 2025):**
- The June 2020 0.30x PMIERs multiplier remains operative for FEMA-Declared Major Disaster Areas going forward, as restated in INDUSTRY_PMIERS_GUIDANCE_2024-02 Table 8 footnote 1.
- The COVID-era extension of the 0.30x multiplier (applied to forbearance-related non-performing loans not necessarily in disaster zones) was discontinued effective March 31, 2025 — see [[topics/pmiers]] (INDUSTRY_PMIERS_GUIDANCE_2024-02; ACT_10-K_2025-12-31).
- At Enact, the COVID-era extension had benefited 2024 PMIERs required assets by approximately $28 million; that benefit was removed at March 31, 2025 (ACT_10-K_2025-12-31).

## How it has evolved

**Pre-2020 baseline**: Master-policy provisions allow MIs to exclude or adjust claims where property damage is the proximate cause of default — the long-standing structural protection against direct catastrophe loss (RDN_10-K_2025-12-31; ESNT_10-K_2025-12-31; INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09).

**June 30, 2020**: PMIERs Guidance (later replaced by Guidance 2021-01 and then Guidance 2024-02) introduces the 0.30x multiplier on the risk-based required asset amount factor for non-performing loans backed by properties in FEMA Declared Major Disaster Areas eligible for individual assistance. The COVID-19 National Emergency was later assimilated into this framework — i.e., the multiplier was extended to apply to COVID-19-era forbearance-related non-performing loans more broadly during the COVID-19 Crisis Period (initial missed monthly payment occurring on or after March 1, 2020 and prior to April 1, 2021) (INDUSTRY_PMIERS_GUIDANCE_2024-02 Section I.b and Appendix A).

**Pandemic period (2020-2022)**: Mass forbearance programs and the COVID-extended 0.30x multiplier dampen MI loss-ratio impact from a wave of pandemic-related delinquencies; reserves established in 2020-2021 are subsequently released as cures materialize.

**April 10, 2023**: COVID-19 National Emergency, declared on March 13, 2020, ends (INDUSTRY_PMIERS_GUIDANCE_2024-02 Appendix A).

**Q4 2024 (September-October 2024)**: Hurricane Helene (Sep 26) and Hurricane Milton (Oct 9) drive material short-term default increases concentrated in Florida and the Carolinas. MIs apply lower claim-rate assumptions to disaster-affected defaults (Essent, Enact, etc.) (ESNT_10-K_2025-12-31; ACT_TRANSCRIPT_2024-12-31).

**January 2025**: Southern California wildfires occur but affect <0.1% of MI IIF in FEMA-declared zones; not material to reserves (ESNT_10-K_2025-12-31).

**March 31, 2025**: Per Guidance 2024-02, the COVID-era extension of the 0.30x multiplier is discontinued (the FEMA-disaster baseline 0.30x multiplier remains in effect via Table 8 footnote 1) (INDUSTRY_PMIERS_GUIDANCE_2024-02; ACT_10-K_2025-12-31).

**Q4 2025**: Hurricane Melissa and other global cat events contribute to Arch's Q4 2025 cat losses of $164M; the five monoline MIs see continued strong cure activity on residual Q4 2024 hurricane-related delinquencies, with favorable reserve development continuing (though at a moderating pace as the post-COVID cushion winds down) (ACGL_TRANSCRIPT_2025-12-31; MTG_TRANSCRIPT_2025-12-31; RDN_TRANSCRIPT_2025-12-31).

**Forward**: Climate change is expected to increase the frequency and severity of natural disasters; Radian's 10-K notes this as a forward risk that could "drive other ecologically related changes such as rising sea waters" (RDN_10-K_2025-12-31). For the monoline MIs, the indirect risk pathway (regional housing-market stress, increased default-to-claim conversion outside the immediate disaster window) is the more material long-term watch item.

## Sources

- [INDUSTRY_PMIERS_GUIDANCE_2024-02] — Effective March 31, 2025: source for the substantive text of the FEMA Major Disaster Area 0.30x multiplier (Table 8, footnote 1, restated): the two qualifying conditions (forbearance plan or incident-period proximity), the windows (18 months from initial missed payment in the forbearance case; three calendar months in the incident-proximity case), the formula (greater of performing-loan factor or 0.30 × non-performing factor); the parallel COVID-era extension (footnote 2) and its discontinuation effective March 31, 2025; the COVID-19 Crisis Period definition (March 1, 2020 to April 1, 2021); the April 10, 2023 end of the COVID-19 National Emergency.
- [INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09] — The structural distinction between PMI (which protects against credit default) and hazard/flood insurance (which protects against property damage); claim mechanics and timing.
- [INDUSTRY_USMI_RESILIENCY_2023-11] — Industry framing: each MI company released announcements concerning natural-disaster events and COVID-19; post-2008 reforms (Master Policy clarity, Rescission Relief Principles) make the industry well-positioned for disaster events.
- [ESNT_10-K_2025-12-31] — Most detailed corporate-filing description of Q4 2024 hurricane impact (Helene September 26, 2024 across FL/GA/SC/NC/TN/VA; Milton October 9, 2024 in FL; 2,119 hurricane-related defaults out of 3,620-loan YoY increase); the master-policy exclusion / adjustment provisions for property-damage-caused defaults; the lower estimated claim rate applied to Q4 2024 affected-area defaults; the January 2025 California wildfire materiality assessment (<0.1% of IIF, no material impact on reserves).
- [RDN_10-K_2025-12-31] — Master-policy provisions on property-damage exclusion; Fannie Mae / Freddie Mac disaster-relief servicing guidelines (12-month forbearance maximum); PMIERs recognition that disaster-affected non-performing loans have higher likelihood of curing; climate change forward-risk framing.
- [ACT_10-K_2025-12-31] — March 31, 2025 discontinuation of the COVID-era extension of the 0.30x multiplier; the $28M YE 2024 benefit at Enact from the COVID-era extension; the Bermuda CIT and Tax Credits Act context.
- [ACT_TRANSCRIPT_2024-12-31] — Enact's Q4 2024 hurricane-related delinquency estimates (~1,000 of 13,700 new delinquencies received in Q4 2024; total inventory rose from 21,000 to 23,600); Enact's 2% claim rate on hurricane-related defaults vs. 9% standard; CEO's framing that the MI policy excludes property damage and requires habitability before a claim is paid.
- [ACGL_TRANSCRIPT_2025-12-31] — Arch's Q4 2025 $164M cat losses (U.S. severe convective storms, Hurricane Melissa, global events); 2025 management framing that "we had only one major cat, which was the California wildfires"; $1.9B peak-zone 1-in-250 PML / 8.2% of tangible equity; 2026 cat-load estimate of 7-8% of net earned premium.
- [MTG_TRANSCRIPT_2025-12-31; MTG_10-K_2025-12-31] — Q4 2025 favorable reserve development of $31M; YE 2025 delinquency rate 2.43% vs. 2.40% in 2024.
- [RDN_TRANSCRIPT_2025-12-31] — Q4 2025 favorable reserve development of $35M; YE 2025 default inventory ~25,000.
- [NMIH_TRANSCRIPT_2025-12-31] — YE 2025 NMI default count of 7,661 / 1.12% default rate.

## Related

- [[topics/pmiers]]
- [[topics/gse_relationship]]
- [[topics/us_mortgage_market]]
- [[topics/mi_regulatory_landscape]]
- [[topics/crt_reinsurance]]
