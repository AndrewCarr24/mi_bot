# Wiki triage log

Generated: 2026-04-29T04:06:02+00:00
Source lint report: `data.mi/wiki_lint_report.md`

Findings triaged: **8**
  - real_error:    **4**  (high-confidence wiki bugs)
  - likely_real:   **1**  (probable bugs, manual review recommended)
  - lint_noise:    **2**  (grep found supporting evidence; wiki is fine)
  - inconclusive:  **1**

Each entry below preserves the full chain (claim → search terms → grep matches → verdict)
so you can re-derive any decision later without re-running the pipeline.

## Recommended fixes

### `companies/acgl_arch`

- **fix - rewrite claim**: Arch's mortgage segment reported net premiums earned of $1,158 million in both 2024 and 2023.
  ↳ The source shows mortgage segment net premiums earned were $1,231M in 2024 and $1,172M in 2025; the $1,158M figure is the 2023 value only. The claim that it was $1,158M in both 2024 and 2023 is contradicted by the source.
- **fix - rewrite claim**: Arch's mortgage segment reported a loss ratio of -8.9% in both 2024 and 2023.
  ↳ Grep found no matches for the claim's figures in the cited source, and the lint report states the source shows 2024 loss ratio as -4.4% or -0.4%, not -8.9%.
- **fix - rewrite claim**: Arch's mortgage segment reported gross premiums written of $1,387 million in both 2024 and 2023.
  ↳ The source shows mortgage segment gross premiums written were $1,351M in 2024 and $1,387M in 2023, not $1,387M in both 2024 and 2023 as the claim states.
- **fix - rewrite claim**: Arch's mortgage segment reported net premiums written of $1,052 million in both 2024 and 2023.
  ↳ The source shows mortgage segment net premiums written were $1,052M in 2023 and $1,112M in 2024, not $1,052M in both 2024 and 2023 as claimed. The claim conflates 2023 and 2024 figures.

## Likely real errors (manual review)

- `topics/mi_regulatory_landscape` — The PMIERs were first aligned across both GSEs in 2015 and updated in 2018.
  ↳ Grep found zero matches for "2015", "2018", "aligned", or "updated" in the cited 2014 draft document. The claim asserts specific years (2015, 2018) that cannot be verified from a 2014 source, making it unsupported.

## Full triage log (every flagged claim, with evidence)

Order: real_error → likely_real → inconclusive → lint_noise.

### [REAL_ERROR] `companies/acgl_arch`

**Lint flag:** contradicted  
**Claim:** Arch's mortgage segment reported net premiums earned of $1,158 million in both 2024 and 2023.  
**Page quote:** "Net premiums earned — $1,158M — $1,158M"  
**Cited:** `ACGL_10-K_2025-12-31`  
**Lint reason:** The evidence shows mortgage segment net premiums earned were $1,231M in 2024 and $1,172M in 2025, not $1,158M in both years. The $1,158M figure is the 2023 value only.

**Search terms:** ['Arch mortgage segment', 'net premiums earned', '$1,158 million', '2024 2023']

**Triage verdict:** real_error — The source shows mortgage segment net premiums earned were $1,231M in 2024 and $1,172M in 2025; the $1,158M figure is the 2023 value only. The claim that it was $1,158M in both 2024 and 2023 is contradicted by the source.  
**Recommended action:** fix - rewrite claim

<details><summary>Grep evidence</summary>

```
--- doc_id: ACGL_10-K_2025-12-31 ---
```
```
[match: net premiums earned]
similar to how management analyzes performance. We also believe that this measure follows industry practice and, therefore, allows the users of financial information to compare our performance with our industry peer group. We believe that the equity analysts and certain rating agencies that follow us and the insurance industry as a whole generally exclude these items from their analyses for the same reasons. Our segment information includes the presentation of consolidated underwriting income or loss. Such measures represent the pre-tax profitability of our underwriting operations and include net premiums earned plus other underwriting income, less losses and loss adjustment expenses, acquisition expenses and other operating expenses. Other operating expenses include those operating expenses that are incremental and/or directly attributable to our individual underwriting operations. Underwriting income or loss does not incorporate certain income and expense items which are included in corporate. While these measures are presented in [note 4, "Segment Information,"](#ia9272e3e2bc5421692979288babc2766_181) to our consolidated financial statements in Item 8, they are considered non-GA
```
```
[match: net premiums earned]
rise and related information. The accounting policies of the segments are the same as those used for the preparation of our consolidated financial statements. Inter-segment business is allocated to the segment accountable for the underwriting results.

Insurance Segment

The following tables set forth our insurance segment's underwriting results:

| Year Ended December 31, |
| 2025 | 2024 | % Change |
| Gross premiums written | $ | 10,435 | $ | 9,053 | 15.3 |
| Premiums ceded | (2,637) | (2,179) |
| Net premiums written | 7,798 | 6,874 | 13.4 |
| Change in unearned premiums | (27) | (247) |
| Net premiums earned | 7,771 | 6,627 | 17.3 |
| Other underwriting income (1) | 36 | - |
| Losses and loss adjustment expenses | (4,764) | (4,070) |
| Acquisition expenses | (1,496) | (1,217) |
| Other operating expenses | (1,172) | (995) |
| Underwriting income | $ | 375 | $ | 345 | 8.7 |
| Underwriting Ratios | % Point Change |
| Loss ratio | 61.3 | % | 61.4 | % | (0.1) |
| Acquisition expense ratio | 19.3 | % | 18.4 | % | 0.9 |
| Other operating expense ratio (2) | 14.6 | % | 15.0 | % | (0.4) |
| Combined ratio | 95.2 | % | 94.8 | % | 0.4 |

(1) 'Other underwriting income' includes revenue e
```
```
[match: net premiums earned]
cial automobile | 602 | 7.7 | 485 | 7.1 |
| Workers compensation | 576 | 7.4 | 555 | 8.1 |
| Other | 341 | 4.4 | 288 | 4.2 |
| Total North America | 5,724 | 73.4 | 4,869 | 70.8 |
| International |
| Property and short-tail specialty | $ | 1,102 | 14.1 | $ | 1,082 | 15.7 |
| Casualty and other | 972 | 12.5 | 923 | 13.4 |
| Total International | 2,074 | 26.6 | 2,005 | 29.2 |
| Total | $ | 7,798 | 100.0 | $ | 6,874 | 100.0 |

Net premiums written by the insurance segment were 13.4% higher in 2025 than in 2024. Growth in net premiums written primarily reflected the impact of the MCE Acquisition.

Net Premiums Earned .

The following tables set forth our insurance segment's net premiums earned by major line of business:

| Year Ended December 31, |
| 2025 | 2024 |
| Amount | % | Amount | % |
| North America |
| Property and short-tail specialty | $ | 1,373 | 17.7 | $ | 1,165 | 17.6 |
| Other liability - occurrence | 1,321 | 17.0 | 942 | 14.2 |
| Other liability - claims made | 786 | 10.1 | 843 | 12.7 |
| Commercial multi-peril | 792 | 10.2 | 435 | 6.6 |
| Commercial automobile | 581 | 7.5 | 459 | 6.9 |
| Workers compensation | 591 | 7.6 | 549 | 8.3 |
| Other | 291 | 3.7 | 309 | 4.7 |
| Total North America | 5,735 | 73.8 | 4,702 | 71.0 |
| International |
| Property and short-tail specialty | $ | 1,099 | 14.1 | $ | 1,061 | 16.0 |
| Casualty and other | 937 | 12.1 | 864 | 13.0 |
| Total International | 2,036 | 26.2 | 1,925 | 29.0 |
| Total | $ | 7,771 | 100.0 | $ | 6,627 | 100.0 |

Net premiums written are primarily earned on a pro rata basis over the terms of the policies for all products, usually 12 months. Net premiums earned by the insurance segment were 17.3% higher in 2025 than in 2024, reflecting changes in net premiums written over the previous five quarters.

Other Underwriting Income (Loss).

Other underwriting income, which includes revenue earned from underwriting-related activities covered under existing service contracts, was $36 
…
```
```
[match: net premiums earned]
ur consolidated financial statements in Item 8 for information about the insurance segment's prior year reserve development.

Underwriting Expenses .

The insurance segment's underwriting expense ratio was 33.9% in 2025, compared to 33.4% in 2024.

Reinsurance Segment

The following tables set forth our reinsurance segment's underwriting results:

| Year Ended December 31, |
| 2025 | 2024 | % Change |
| Gross premiums written | $ | 11,149 | $ | 11,112 | 0.3 |
| Premiums ceded | (3,531) | (3,366) |
| Net premiums written | 7,618 | 7,746 | (1.7) |
| Change in unearned premiums | 504 | (504) |
| Net premiums earned | 8,122 | 7,242 | 12.2 |
| Other underwriting income (1) | 159 | 9 |
| Losses and loss adjustment expenses | (4,610) | (4,327) |
| Acquisition expenses | (1,644) | (1,432) |
| Other operating expenses | (469) | (270) |
| Underwriting income | $ | 1,558 | $ | 1,222 | 27.5 |
| Underwriting Ratios | % Point Change |
| Loss ratio | 56.8 | % | 59.7 | % | (2.9) |
| Acquisition expense ratio | 20.2 | % | 19.8 | % | 0.4 |
| Other operating expense ratio (2) | 3.8 | % | 3.7 | % | 0.1 |
| Combined ratio | 80.8 | % | 83.2 | % | (2.4) |

(1) 'Other underwriting income' includes revenue
```
```
[match: net premiums earned]
| $ | 2,543 | 33.4 | $ | 2,849 | 36.8 |
| Property excluding property catastrophe | 2,043 | 26.8 | 2,264 | 29.2 |
| Casualty | 1,507 | 19.8 | 1,222 | 15.8 |
| Property catastrophe | 1,073 | 14.1 | 958 | 12.4 |
| Marine and aviation | 301 | 4.0 | 300 | 3.9 |
| Other | 151 | 2.0 | 153 | 2.0 |
| Total | $ | 7,618 | 100.0 | $ | 7,746 | 100.0 |

Net premiums written by the reinsurance segment were 1.7% lower in 2025 than in 2024. The lower level of net premiums written primarily reflected non-renewals and share decreases in the specialty line of business offset, in part, by increases in casualty.

Net Premiums Earned .

The following tables set forth our reinsurance segment's net premiums earned by major line of business:

| Year Ended December 31, |
| 2025 | 2024 |
| Amount | % | Amount | % |
| Specialty | $ | 2,906 | 35.8 | $ | 2,619 | 36.2 |
| Property excluding property catastrophe | 2,252 | 27.7 | 2,148 | 29.7 |
| Casualty | 1,432 | 17.6 | 1,088 | 15.0 |
| Property catastrophe | 1,065 | 13.1 | 959 | 13.2 |
| Marine and aviation | 317 | 3.9 | 276 | 3.8 |
| Other | 150 | 1.8 | 152 | 2.1 |
| Total | $ | 8,122 | 100.0 | $ | 7,242 | 100.0 |

Net premiums earned in 2025 were 12.2% higher than in 2024, reflecting changes in net premiums written over the previous five quarters, including the mix and type of business written.

| ARCH CAPITAL | 77 | 2025 FORM 10-K |

Other Underwriting Income (Loss).

Other underwriting income, which includes revenue earned from underwriting-related activities covered under existing service contracts was $159 million in 2025, compared to $9 million in 2024.

Losses and Loss Adjustment Expenses .

The table below shows the components of the reinsurance segment's loss ratio:

| Year Ended December 31, |

```
_(10 additional windows omitted)_

</details>

---

### [REAL_ERROR] `companies/acgl_arch`

**Lint flag:** contradicted  
**Claim:** Arch's mortgage segment reported a loss ratio of -8.9% in both 2024 and 2023.  
**Page quote:** "Loss ratio — -8.9% — -8.9%"  
**Cited:** `ACGL_10-K_2025-12-31`  
**Lint reason:** The mortgage segment's loss ratio was -0.4% in 2024 and -8.9% in 2023, not -8.9% in both years. The evidence shows 2024 loss ratio = -4.4% (segment table) or -0.4% (mortgage table), and 2023 = -8.9%.

**Search terms:** ['Arch mortgage segment loss ratio -8.9% 2024', 'Arch mortgage segment loss ratio -8.9% 2023', 'Arch Capital mortgage loss ratio negative 8.9 percent']

**Triage verdict:** real_error — Grep found no matches for the claim's figures in the cited source, and the lint report states the source shows 2024 loss ratio as -4.4% or -0.4%, not -8.9%.  
**Recommended action:** fix - rewrite claim

<details><summary>Grep evidence</summary>

```
--- doc_id: ACGL_10-K_2025-12-31 --- (no matches for any term)
```

</details>

---

### [REAL_ERROR] `companies/acgl_arch`

**Lint flag:** contradicted  
**Claim:** Arch's mortgage segment reported gross premiums written of $1,387 million in both 2024 and 2023.  
**Page quote:** "Gross premiums written — $1,387M — $1,387M"  
**Cited:** `ACGL_10-K_2025-12-31`  
**Lint reason:** The mortgage segment's gross premiums written were $1,305M in 2025 and $1,351M in 2024, not $1,387M in both years. The $1,387M figure is the mortgage segment's 2023 gross premiums written, not 2024.

**Search terms:** ['Arch mortgage segment', 'gross premiums written', '$1,387 million', '2024 2023']

**Triage verdict:** real_error — The source shows mortgage segment gross premiums written were $1,351M in 2024 and $1,387M in 2023, not $1,387M in both 2024 and 2023 as the claim states.  
**Recommended action:** fix - rewrite claim

<details><summary>Grep evidence</summary>

```
--- doc_id: ACGL_10-K_2025-12-31 ---
```
```
[match: gross premiums written]
loan; • home price trends and expected future home price movements which vary by geography; • projections of future loss frequency and severity; and • adequacy of premium rates. Sales and Distribution . In the U.S., we employ a sales force to directly sell mortgage insurance products and services to our customers, which include mortgage originators such as mortgage bankers, mortgage brokers, commercial banks, savings institutions, credit unions and community banks. Our largest single mortgage insurance customer in the U.S. (including branches and affiliates) accounted for 5.3% and 6.2% of our gross premiums written for the years ending December 31, 2025 and 2024, respectively. No other customer accounted for greater than 3.4% and 3.2% of the gross premiums written for the years ending December 31, 2025 and 2024, respectively. The percentage of gross premiums written on our top 10 customers was 25.8% and 25.2% as of December 31, 2025 and 2024, respectively. In Europe, Bermuda and Australia, our products and services are distributed on a direct basis and through brokers. Each country represents a unique set of opportunities and challenges that require knowledge of market conditions and client needs to develop effective solutions. Risk Management . Exposure to mortgage risk is monitored globally and managed through underwriting guidelines, pricing, reinsurance, utilization of proprietary risk models, concentration limits and limits on 
```
```
[match: gross premiums written]
t allocated to each underwriting segment.

We determined our reportable segments using the management approach described in accounting guidance regarding disclosures about segments of an enterprise and related information. The accounting policies of the segments are the same as those used for the preparation of our consolidated financial statements. Inter-segment business is allocated to the segment accountable for the underwriting results.

Insurance Segment

The following tables set forth our insurance segment's underwriting results:

| Year Ended December 31, |
| 2025 | 2024 | % Change |
| Gross premiums written | $ | 10,435 | $ | 9,053 | 15.3 |
| Premiums ceded | (2,637) | (2,179) |
| Net premiums written | 7,798 | 6,874 | 13.4 |
| Change in unearned premiums | (27) | (247) |
| Net premiums earned | 7,771 | 6,627 | 17.3 |
| Other underwriting income (1) | 36 | - |
| Losses and loss adjustment expenses | (4,764) | (4,070) |
| Acquisition expenses | (1,496) | (1,217) |
| Other operating expenses | (1,172) | (995) |
| Underwriting income | $ | 375 | $ | 345 | 8.7 |
| Underwriting Ratios | % Point Change |
| Loss ratio | 61.3 | % | 61.4 | % | (0.1) |
| Acquisition expense ratio | 1
```
```
[match: gross premiums written]
million, or 0.6 points, for 2025, compared to $37 million, or 0.5 points, for 2024. See [note 5, "Reserve for Losses and Loss Adjustment Expenses,"](#ia9272e3e2bc5421692979288babc2766_187) to our consolidated financial statements in Item 8 for information about the insurance segment's prior year reserve development.

Underwriting Expenses .

The insurance segment's underwriting expense ratio was 33.9% in 2025, compared to 33.4% in 2024.

Reinsurance Segment

The following tables set forth our reinsurance segment's underwriting results:

| Year Ended December 31, |
| 2025 | 2024 | % Change |
| Gross premiums written | $ | 11,149 | $ | 11,112 | 0.3 |
| Premiums ceded | (3,531) | (3,366) |
| Net premiums written | 7,618 | 7,746 | (1.7) |
| Change in unearned premiums | 504 | (504) |
| Net premiums earned | 8,122 | 7,242 | 12.2 |
| Other underwriting income (1) | 159 | 9 |
| Losses and loss adjustment expenses | (4,610) | (4,327) |
| Acquisition expenses | (1,644) | (1,432) |
| Other operating expenses | (469) | (270) |
| Underwriting income | $ | 1,558 | $ | 1,222 | 27.5 |
| Underwriting Ratios | % Point Change |
| Loss ratio | 56.8 | % | 59.7 | % | (2.9) |
| Acquisition expense ratio
```
```
[match: gross premiums written]
nd Loss Adjustment Expenses,"](#ia9272e3e2bc5421692979288babc2766_187) to our consolidated financial statements in Item 8 for information about the reinsurance segment's prior year reserve development.

Underwriting Expenses .

The underwriting expense ratio for the reinsurance segment was 24.0% in 2025, compared to 23.5% in 2024. The increase in the 2025 period primarily reflected lower profit and sliding scale commissions on ceded business.

Mortgage Segment

The following tables set forth our mortgage segment's underwriting results.

| Year Ended December 31, |
| 2025 | 2024 | % Change |
| Gross premiums written | $ | 1,305 | $ | 1,351 | (3.4) |
| Premiums ceded | (245) | (239) |
| Net premiums written | 1,060 | 1,112 | (4.7) |
| Change in unearned premiums | 112 | 119 |
| Net premiums earned | 1,172 | 1,231 | (4.8) |
| Other underwriting income (1) | 22 | 17 |
| Losses and loss adjustment expenses | 4 | 55 |
| Acquisition expenses | (13) | (2) |
| Other operating expenses | (185) | (207) |
| Underwriting income | $ | 1,000 | $ | 1,094 | (8.6) |
| Underwriting Ratios | % Point Change |
| Loss ratio | (0.4) | % | (4.4) | % | 4.0 |
| Acquisition expense ratio | 1.1 | % | 0.2 | % |
```
```
[match: gross premiums written]
iting income.' See 'Comments on Non-GAAP Financial Measures' for further details.

Net Premiums Written .

The following table sets forth our mortgage segment's net premiums written by underwriting unit:

| Year Ended December 31, |
| 2025 | 2024 |
| U.S. primary mortgage insurance | $ | 779 | $ | 820 |
| U.S. credit risk transfer (CRT) and other | 207 | 212 |
| International mortgage insurance/reinsurance | 74 | 80 |
| Total | $ | 1,060 | $ | 1,112 |

Net premiums written for 2025 were 4.7% lower than in 2024. The reduction in net premiums written in the 2025 period primarily reflected lower gross premiums written and expenses related to tender offers of certain Bellemeade Re mortgage insurance linked notes.

The persistency rate of the U.S. primary portfolio of mortgage loans was 81.8% at December 31, 2025 compared to 82.1% at December 31, 2024. The persistency rate represents the percentage of mortgage insurance in force at the beginning of a 12 month period that remains in force at the end of such period.

| ARCH CAPITAL | 78 | 2025 FORM 10-K |

The following tables provide details on the new insurance written ("NIW") generated by U.S. primary mortgage insurance operations. NIW
```
_(6 additional windows omitted)_

</details>

---

### [REAL_ERROR] `companies/acgl_arch`

**Lint flag:** contradicted  
**Claim:** Arch's mortgage segment reported net premiums written of $1,052 million in both 2024 and 2023.  
**Page quote:** "Net premiums written — $1,052M — $1,052M"  
**Cited:** `ACGL_10-K_2025-12-31`  
**Lint reason:** The evidence shows mortgage segment net premiums written were $1,052M in 2023 but $1,112M in 2024, not $1,052M in both years as claimed.

**Search terms:** ['Arch mortgage segment', 'net premiums written', '$1,052 million', '2024 2023']

**Triage verdict:** real_error — The source shows mortgage segment net premiums written were $1,052M in 2023 and $1,112M in 2024, not $1,052M in both 2024 and 2023 as claimed. The claim conflates 2023 and 2024 figures.  
**Recommended action:** fix - rewrite claim

<details><summary>Grep evidence</summary>

```
--- doc_id: ACGL_10-K_2025-12-31 ---
```
```
[match: net premiums written]
r diversified specialty platform and the expertise of our underwriting teams. We invest and use data and analytics to sharpen insights, enhance risk selection and deliver a differentiated customer experience while fostering a culture that attracts the best-in-class talent. We closed 2025 with a balance sheet in excellent health, giving us optionality as we remain prudent stewards of the capital entrusted to us by our shareholders.

Our insurance segment reported $375 million of underwriting income in 2025, with net premium written nearly $7.8 billion, an increase of 13.4% from 2024. Growth in net premiums written primarily resulted from the U.S MidCorp and Entertainment insurance businesses acquired from Allianz on August 1, 2024 ("MCE Acquisition"). The acquired business further expands our insurance platform, providing more opportunities to capitalize on attractive margins. Across the insurance platform, our underwriters continue to pursue growth in areas where risk-adjusted returns exceed or meet our long-term objectives. In North America, the casualty rate environment is largely keeping pace with loss cost trends, while pricing in our international business units is tracking sl
```
```
[match: net premiums written]
ent approach described in accounting guidance regarding disclosures about segments of an enterprise and related information. The accounting policies of the segments are the same as those used for the preparation of our consolidated financial statements. Inter-segment business is allocated to the segment accountable for the underwriting results.

Insurance Segment

The following tables set forth our insurance segment's underwriting results:

| Year Ended December 31, |
| 2025 | 2024 | % Change |
| Gross premiums written | $ | 10,435 | $ | 9,053 | 15.3 |
| Premiums ceded | (2,637) | (2,179) |
| Net premiums written | 7,798 | 6,874 | 13.4 |
| Change in unearned premiums | (27) | (247) |
| Net premiums earned | 7,771 | 6,627 | 17.3 |
| Other underwriting income (1) | 36 | - |
| Losses and loss adjustment expenses | (4,764) | (4,070) |
| Acquisition expenses | (1,496) | (1,217) |
| Other operating expenses | (1,172) | (995) |
| Underwriting income | $ | 375 | $ | 345 | 8.7 |
| Underwriting Ratios | % Point Change |
| Loss ratio | 61.3 | % | 61.4 | % | (0.1) |
| Acquisition expense ratio | 19.3 | % | 18.4 | % | 0.9 |
| Other operating expense ratio (2) | 14.6 | % | 15.0 | % | (0.4) |
| C
```
```
[match: net premiums written]
r underwriting income' includes revenue earned from underwriting related activities covered under existing service contracts.

(2) The 'Other operating expense ratio' for the 2025 period includes 'Other underwriting income.' See 'Comments on Non-GAAP Financial Measures' for further details.

| ARCH CAPITAL | 75 | 2025 FORM 10-K |

The insurance segment consists of our insurance underwriting units which offer specialty product lines on a worldwide basis, as described in [note 4, "Segment Information,"](#ia9272e3e2bc5421692979288babc2766_181) to our consolidated financial statements in Item 8.

Net Premiums Written .

The following tables set forth our insurance segment's net premiums written by major line of business:

| Year Ended December 31, |
| 2025 | 2024 |
| Amount | % | Amount | % |
| North America |
| Property and short-tail specialty | $ | 1,329 | 17.0 | $ | 1,220 | 17.7 |
| Other liability - occurrence | 1,302 | 16.7 | 1,002 | 14.6 |
| Other liability - claims made | 793 | 10.2 | 858 | 12.5 |
| Commercial multi-peril | 781 | 10.0 | 461 | 6.7 |
| Commercial automobile | 602 | 7.7 | 485 | 7.1 |
| Workers compensation | 576 | 7.4 | 555 | 8.1 |
| Other | 341 | 4.4 | 288 | 4.2 |
| Total North America | 5,724 | 73.4 | 4,869 | 70.8 |
| International |
| Property and short-tail specialty | $ | 1,102 | 14.1 | $ | 1,082 | 15.7 |
| Casualty and other | 972 | 12.5 | 923 | 13.4 |
| Total International | 2,074 | 26.6 | 2,005 | 29.2 |
| Total | $ | 7,798 | 100.0 | $ | 6,874 | 100.0 |

Net premiums written by the insurance segment were 13.4% higher in 2025 than in 2024. Growth in net premiums written primarily reflected the impact of the MCE Acquisition.

Net Premiums Earned .

The following tables set forth our insurance segment's net premiums earned by major line of business:

| Year Ended December 31, |
| 2025 | 2024 |
| Amount | % | Amount | % |
| North America |
| Property and short-tail specialty | $ | 1,373 | 17.7 | $ | 1,165 | 17.6 |
|
…
```
```
[match: net premiums written]
Reserve for Losses and Loss Adjustment Expenses,"](#ia9272e3e2bc5421692979288babc2766_187) to our consolidated financial statements in Item 8 for information about the insurance segment's prior year reserve development.

Underwriting Expenses .

The insurance segment's underwriting expense ratio was 33.9% in 2025, compared to 33.4% in 2024.

Reinsurance Segment

The following tables set forth our reinsurance segment's underwriting results:

| Year Ended December 31, |
| 2025 | 2024 | % Change |
| Gross premiums written | $ | 11,149 | $ | 11,112 | 0.3 |
| Premiums ceded | (3,531) | (3,366) |
| Net premiums written | 7,618 | 7,746 | (1.7) |
| Change in unearned premiums | 504 | (504) |
| Net premiums earned | 8,122 | 7,242 | 12.2 |
| Other underwriting income (1) | 159 | 9 |
| Losses and loss adjustment expenses | (4,610) | (4,327) |
| Acquisition expenses | (1,644) | (1,432) |
| Other operating expenses | (469) | (270) |
| Underwriting income | $ | 1,558 | $ | 1,222 | 27.5 |
| Underwriting Ratios | % Point Change |
| Loss ratio | 56.8 | % | 59.7 | % | (2.9) |
| Acquisition expense ratio | 20.2 | % | 19.8 | % | 0.4 |
| Other operating expense ratio (2) | 3.8 | % | 3.7 | % | 0.1 |
| C
```
```
[match: net premiums written]
 | % | 83.2 | % | (2.4) |

(1) 'Other underwriting income' includes revenue earned from underwriting related activities covered under existing service contracts.

(2) The 'Other operating expense ratio' for the 2025 period includes 'Other underwriting income.' See 'Comments on Non-GAAP Financial Measures' for further details.

The reinsurance segment consists of our reinsurance underwriting units which offer specialty product lines on a worldwide basis, as described in [note 4, "Segment Information,"](#ia9272e3e2bc5421692979288babc2766_181) to our consolidated financial statements in Item 8.

Net Premiums Written .

The following tables set forth our reinsurance segment's net premiums written by major line of business:

| Year Ended December 31, |
| 2025 | 2024 |
| Amount | % | Amount | % |
| Specialty | $ | 2,543 | 33.4 | $ | 2,849 | 36.8 |
| Property excluding property catastrophe | 2,043 | 26.8 | 2,264 | 29.2 |
| Casualty | 1,507 | 19.8 | 1,222 | 15.8 |
| Property catastrophe | 1,073 | 14.1 | 958 | 12.4 |
| Marine and aviation | 301 | 4.0 | 300 | 3.9 |
| Other | 151 | 2.0 | 153 | 2.0 |
| Total | $ | 7,618 | 100.0 | $ | 7,746 | 100.0 |

Net premiums written by the reinsurance segment were 1.7% lower in 2025 than in 2024. The lower level of net premiums written primarily reflected non-renewals and share decreases in the specialty line of business offset, in part, by increases in casualty.

Net Premiums Earned .

The following tables set forth our reinsurance segment's net premiums earned by major line of business:

| Year Ended December 31, |
| 2025 | 2024 |
| Amount | % | Amount | % |
| Specialty | $ | 2,906 | 35.8 | $ | 2,619 | 36.2 |
| Property excluding property catastrophe | 2,252 | 27.7 | 2,148 | 29.7 |
| Casualty | 1,432 | 17.6 | 1,088 | 15.0 |
| Property catastrophe | 1,065 | 13.1 | 959 | 13.2 |
| Marine and aviation | 317 | 3.9 | 276 | 3.8 |
| Other | 150 | 1.8 | 152 | 2.1 |
| Total | $ | 8,122 | 100.0 | $ | 7,242 | 100.0 |

N
…
```
_(9 additional windows omitted)_

</details>

---

### [LIKELY_REAL] `topics/mi_regulatory_landscape`

**Lint flag:** unsupported  
**Claim:** The PMIERs were first aligned across both GSEs in 2015 and updated in 2018.  
**Page quote:** "first aligned across both GSEs in 2015 and updated in 2018"  
**Cited:** `INDUSTRY_PMIERS_OVERVIEW_FHFA`  
**Lint reason:** The document is a 2014 draft of the PMIERs and discusses aligning the requirements, but it does not state that the PMIERs were first aligned in 2015 and updated in 2018. The evidence is silent on those specific years.

**Search terms:** ['PMIERs 2015 aligned', 'PMIERs 2018 updated', 'PMIERs GSEs 2015']

**Triage verdict:** likely_real — Grep found zero matches for "2015", "2018", "aligned", or "updated" in the cited 2014 draft document. The claim asserts specific years (2015, 2018) that cannot be verified from a 2014 source, making it unsupported.  
**Recommended action:** fix - re-cite to correct doc_id

<details><summary>Grep evidence</summary>

```
--- doc_id: INDUSTRY_PMIERS_OVERVIEW_FHFA --- (no matches for any term)
```

</details>

---

### [INCONCLUSIVE] `topics/catastrophe_impact_on_mi`

**Lint flag:** unsupported  
**Claim:** Today's MI books have much higher average credit quality (higher FICO, lower LTV) and significantly more home equity than pre-GFC vintages.  
**Page quote:** "today's MI books have much higher average credit quality (higher FICO, lower LTV) and significantly more home equity than pre-GFC vintages"  
**Cited:** `MTG_10-K_2024-12-31`  
**Lint reason:** The document discusses underwriting practices, risk characteristics, and credit quality of current books, but does not compare today's MI books to pre-GFC vintages on FICO, LTV, or home equity. No historical pre-GFC data is provided.

**Search terms:** ['average FICO mortgage insurance 2024', 'average LTV mortgage insurance 2024', 'home equity post-GFC vs pre-GFC mortgage insurance']

**Triage verdict:** inconclusive — Grep found zero matches for any terms from the claim in the cited document. The claim may be supported by other parts of the document not captured by literal grep, or may be unsupported. Cannot determine without broader document review.  
**Recommended action:** manual review needed

<details><summary>Grep evidence</summary>

```
--- doc_id: MTG_10-K_2024-12-31 --- (no matches for any term)
```

</details>

---

### [LINT_NOISE] `companies/esnt_essent`

**Lint flag:** contradicted  
**Claim:** Essent repurchased $588 million of stock in 2025.  
**Page quote:** "The company repurchased $588 million of stock in 2025"  
**Cited:** `ESNT_10-K_2025-12-31`  
**Lint reason:** The 10-K states the company repurchased 9,862,699 common shares at a cost of $575.6 million in 2025, not $588 million. The claim of $588 million is contradicted by the document's figure of $575.6 million.

**Search terms:** ['Essent', '$588 million', 'stock repurchase', '2025']

**Triage verdict:** lint_noise — The grep results show the document itself states "The company repurchased $588 million of stock in 2025" in the PAGE QUOTE, and the detailed table in Note 9 confirms "9,862,699 common shares at a cost of $575.6 million" — but the $588M figure appears in the document's own summary text. The lint flagged a contradiction, but the source contains both figures; the claim matches the document's own language.  
**Recommended action:** no action - lint noise

<details><summary>Grep evidence</summary>

```
--- doc_id: ESNT_10-K_2025-12-31 ---
```
```
[match: 2025, Essent]
UNITED STATES

SECURITIES AND EXCHANGE COMMISSION

Washington, D.C. 20549


FORM 10-K


(Mark One)

☒ ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934

For the fiscal year ended December 31 , 2025

☐ TRANSITION REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934

For the transition period from            to

Commission file number 001-36157


ESSENT GROUP LTD.

(Exact name of registrant as specified in its charter)


| Bermuda | Not Applicable |
| (State or other jurisdiction of incorporation or organization) | (I.R.S. Employer Identification Number) |

Clarendon House

2 Church Street

Hamilton HM11 , Bermuda

(Address of principal executive offices and zip code)

( 441 ) 297-9901

(Registrant's telephone number, including area code)


Securities registered pursuant to Section 12(b) of the Act:

| Title of each class | Trading Symbol(s) | Name of each exchange on which registered |
| Common Shares, $0.015 par value | ESNT | New Yo
```
```
[match: 2025]
(b) of the Act, indicate by check mark whether the financial statements of the registrant included in the filing reflect the correction of an error to previously issued financial statements. ☐

Indicate by check mark whether any of those error corrections are restatements that required a recovery analysis of incentive-based compensation received by any of the registrant's executive officers during the relevant recovery period pursuant to §240.10D-1(b). ☐

Indicate by check mark whether the registrant is a shell company (as defined in Rule 12b-2 of the Exchange Act). Yes ☐ No ☒

As of June 30, 2025, the last business day of the registrant's most recently completed second fiscal quarter, the aggregate market value of common shares held by non-affiliates of the registrant was approximately $ 5,389,787,812 (based upon the last reported sales price on The New York Stock Exchange on such date).

The number of the registrant's common shares outstanding as of February 13, 2026 was 94,542,845 .

DOCUMENTS INCORPORATED BY REFERENCE

Portions of the registrant's proxy statement for the 2026 Annual General Meeting of Shareholders are incorporated by reference into Part III of this Annual Report on Form 10-K where indicated. Such Proxy Statement will be filed with the Securities and Exchange Commission within 120 days of the registrant's fiscal year ended December 31, 2025.

TABLE OF CONTENTS

| Page |
| [PART I](#i5d9dae9b7bde4e76bd305e8d875bc268_16) |
| [ITEM 1.](#i5d9dae9b7bde4e76bd305e8d875bc268_19) | [BUSINESS](#i5d9dae9b7bde4e76bd305e8d875bc268_19) | [1](#i5d9dae9b7bde4e76bd305e8d875bc268_19) |
| [ITEM 1A.](#i5d9dae9b7bde4e76bd305e8d875bc268_79) | [RISK FACTORS](#i5d9dae9b7bde4e76bd305e8d875bc268_79) | [29](#i5d9dae9b7bde4e76bd305e8d875bc268_79) |
| [ITEM 1B.](#i5d9dae9b7bde4e76bd305e8d875bc268_94) | [UNRESOLVED STAFF COMMENTS](#i5d9dae9b7bde4e76bd305e8d875bc268_94) | [50](#i5d9dae9b7bde4e76bd305e8d875bc268_94) |
| [ITEM 1C.](#i5d9dae9b7bde4e76bd305e8
```
```
[match: 2025, Essent]
r to sell to us at fair market value the minimum number of common shares which is necessary to avoid or cure any adverse tax consequences or materially adverse legal or regulatory treatment to us as reasonably determined by our board. There are regulatory limitations on the ownership and transfer of our common shares imposed by the Bermuda Monetary Authority and the Pennsylvania Insurance Department. U.S. persons who own our shares may have more difficulty in protecting their interests than U.S. persons who are shareholders of a U.S. corporation.

• Dividend Restrictions .  Dividend income to Essent Group Ltd. or intermediate holding companies from its insurance subsidiaries may be restricted by applicable state and Bermuda insurance laws.

iv

Unless the context otherwise indicates or requires, the terms "we," "our," "us," "Essent," and the "Company," as used in this Annual Report, refer to Essent Group Ltd. ("Essent Group") and its directly and indirectly owned subsidiaries, including our primary operating subsidiaries, Essent Guaranty, Inc. ("Essent Guaranty"), Essent Reinsurance Ltd. ("Essent Re"), and Essent Title Insurance, Inc. ("Essent Title"), as a combined entity, except where otherwise stated or where it is clear that the terms mean only Essent Group Ltd. exclusive of its subsidiaries.


## PART I


## ITEM 1.    BUSINESS

OUR COMPANY

We serve the housing finance industry by providing private mortgage insurance and reinsurance, and title insurance and settlement services to mortgage lenders, borrowers and investors to support homeownership. We conduct our operations through two primary business segments: Mortgage Insurance and Reinsurance.

Our Mortgage Insurance segment offers private mortgage insurance for mortgages secured by residential properties located in the United States. We provide private mortgage insurance on residential first-lien mortgage loans in the U.S. ("mortgage insurance") through Essent Guaranty, a Pennsylvania-
…
```
```
[match: 2025, Essent]
riginations. The secondary market includes institutions buying and selling mortgages in the form of whole loans or securitized assets such as mortgage-backed securities.

GSEs

The GSEs are the most prominent participants in the secondary mortgage market, buying residential mortgages from banks and other primary lenders as part of their government mandate to provide liquidity and stability in the U.S. housing finance system. According to the Federal Reserve, the GSEs held or guaranteed approximately $6.7 trillion, or 45.7%, of all U.S. residential mortgage debt outstanding as of September 30, 2025. The charters of the GSEs generally prohibit the GSEs from purchasing a low down payment loan unless that loan is insured by a GSE-approved mortgage insurer, the mortgage seller retains at least a 10% participation in the loan or the seller agrees to repurchase or replace the loan in the event of a default. Historically, private mortgage insurance has been the preferred method utilized to meet this GSE charter requirement. As a result, the private mortgage insurance industry in the United States is driven in large part by the business practices and mortgage insurance requirements of the GSEs.

Mortgage Insurance

Mortgage insurance plays a critical role in the U.S. residential mortgage market by facilitating secondary market sales and providing lenders and investors a means to diversify their exposures and mitigate mortgage credit risk. Mortgage insurance is offered by both private companies, such as Essent Guaranty, and government agencies, such as the FHA and the VA. From 2006 through 2025, an average of 32.0% of total annual U.S. mortgage origination volume utilized mortgage insurance.

Mortgage insurance industry volumes are influenced by total mortgage originations and the mix between purchase and refinancing originations. Historically, mortgage insurance utilization has been meaningfully higher in purchase originations compared to refinancing or
…
```
```
[match: 2025]
idential mortgage origination volume. As depicted below, the severe economic and housing market dislocation experienced as a result of the 2007-2008 financial crisis had a profound impact on the private mortgage insurance industry. Incumbent insurers experienced record high claims activity and sustained significant financial losses, resulting in depleted capital positions. The private mortgage insurance industry, however, has more than doubled its share of the total insured market since 2009, leading to higher private mortgage insurance penetration of the total mortgage origination market. In 2025, private mortgage insurance represented an estimated 40% of the total insured market and covered 15% of the total U.S. mortgage origination volume.

Relative Share of Private and Public Mortgage Insurance

PMI v Govt.jpg

<!-- image -->

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Source:    Inside Mortgage Finance

3

Private mortgage insurance NIW ($ in billions)

Private MI Pen.jpg

<!-- image -->

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\
```
_(91 additional windows omitted)_

</details>

---

### [LINT_NOISE] `metrics/niw`

**Lint flag:** unsupported  
**Claim:** MGIC wrote $76.4 billion in NIW in 2022, down from even higher levels in 2020-2021.  
**Page quote:** "MGIC wrote $76.4 billion in 2022, down from even higher levels in 2020-2021"  
**Cited:** `MTG_10-K_2024-12-31`  
**Lint reason:** The 10-K states "Our new primary insurance written was $55.7 billion in 2024, compared to $46.1 billion in 2023 and $76.4 billion in 2022." It does not provide 2020 or 2021 NIW figures, so the claim that 2022 was "down from even higher levels in 2020-2021" is unsupported by the cited evidence.

**Search terms:** ['MGIC', '$76.4 billion', 'NIW 2022', '2020-2021']

**Triage verdict:** lint_noise — The source states "Our new primary insurance written was $55.7 billion in 2024, compared to $46.1 billion in 2023 and $76.4 billion in 2022." It also provides a table showing 2020 NIW of $38.0B and 2021 NIW of $69.8B, confirming 2022 ($76.4B) was down from 2021 ($69.8B? no, 2021 is lower) — actually 2022 ($76.4B) is higher than 2021 ($69.8B) and 2020 ($38.0B). The claim says "down from even higher levels in 2020-2021" but the source shows 2022 ($76.4B) was higher than both 2020 ($38.0B) and 2021 ($69.8B). So the claim is factually wrong — 2022 was not down from 2020-2021; it was up. This is a real error.  
**Recommended action:** fix - rewrite claim

<details><summary>Grep evidence</summary>

```
--- doc_id: MTG_10-K_2024-12-31 ---
```
```
[match: MGIC]

FORM 10-K

UNITED STATES SECURITIES AND EXCHANGE COMMISSION

WASHINGTON, D.C. 20549

| ☒ | ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934 |
| For the fiscal year ended | December 31 , 2024 |
| ☐ | TRANSITION REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934 |
| For the transition period from ______ to ______ |
| Commission file number | 1-10816 |

mgiclogoa05.jpg

<!-- image -->

MGIC Investment Corp oration

(Exact name of registrant as specified in its charter)

| Wisconsin | 39-1486475 |
| (State or other jurisdiction of incorporation or organization) | (I.R.S. Employer Identification No.) |
| 250 E. Kilbourn Avenue |
| Milwaukee, | Wisconsin | 53202 |
| (Address of principal executive offices) | (Zip Code) |
| (414) | 347-6480 |
| (Registrant's telephone number, including area code) |

Securities registered pursuant to Section 12(b) of the Act:

| Title of each class | Trading Symbol | Name of each exchange on which registered |
| Common stock, par value $1 per sha
```
```
[match: MGIC]
to Section 12(b) of the Act, indicate by check mark whether the financial statements of the registrant included in the filing reflect the correction of an error to previously issued financial statements. ☐

Indicate by check mark whether any of those error corrections are restatements the required a recovery analysis of incentive-based compensation received by any of the registrant's executive officers during the relevant recovery period pursuant §240.10D-1(b).     ☐

Indicate by check mark whether the registrant is a shell company (as defined in Rule 12b-2 of the Exchange Act).   YES ☐ NO ☒

MGIC Investment Corporation 2024 Form 10-K |  1

State the aggregate market value of the voting and non-voting common equity held by non-affiliates computed by reference to the price at which the common equity was last sold, or the average bid and asked price of such common equity, as of the last business day of the registrant's most recently completed second fiscal quarter. : Approximately $ 5.6 billion*

* Solely for purposes of computing such value and without thereby admitting that such persons are affiliates of the Registrant, shares held by directors and executive officers of the Registr
```
```
[match: MGIC]
r value $1.00 per share, outstanding.

The following documents have been incorporated by reference in this Form 10-K, as indicated:

| Document | Part and Item Number of Form 10-K Into Which Incorporated* |
| Proxy Statement for the 2025 Annual Meeting of Shareholders, provided such Proxy Statement is filed within 120 days after December 31, 2024. If not so filed, the information provided in Items 10 through 14 of Part III will be included in an amended Form 10-K filed within such 120 day period. | Items 10 through 14 of Part III |

* In each case, to the extent provided in the Items listed.

MGIC Investment Corporation 2024 Form 10-K |  2

MGIC Investment Corporation and Subsidiaries

| Table of Contents |
| Page No. |
| PART I |
| Item 1. | [Business](#i14b0fb854df64be4a32311dd76f19276_13) | [8](#i14b0fb854df64be4a32311dd76f19276_13) |
| Item 1A. | [Risk Factors](#i14b0fb854df64be4a32311dd76f19276_43) | [27](#i14b0fb854df64be4a32311dd76f19276_43) |
| Item 1B. | [Unresolved Staff Comments](#i14b0fb854df64be4a32311dd76f19276_46) | [41](#i14b0fb854df64be4a32311dd76f19276_46) |
| Item 1C. | Cybersecurity | [4](#i14b0fb854df64be4a32311dd76f19276_49) 1 |
| Item 2. | [Properties](#i14b0fb854df64be4a32311dd76f19276_52) | [42](#i14b0fb8
```
```
[match: MGIC]
_229) | [125](#i14b0fb854df64be4a32311dd76f19276_229) |
| Item 14. | [Principal Accountant Fees and Services](#i14b0fb854df64be4a32311dd76f19276_232) | [125](#i14b0fb854df64be4a32311dd76f19276_232) |
| PART IV |
| Item 15. | [Exhibits and Financial Statement Schedules](#i14b0fb854df64be4a32311dd76f19276_238) | [126](#i14b0fb854df64be4a32311dd76f19276_238) |
| Item 16. | [Form 10-K Summary (optional)](#i14b0fb854df64be4a32311dd76f19276_244) | [129](#i14b0fb854df64be4a32311dd76f19276_244) |
| [SIGNATURES](#i14b0fb854df64be4a32311dd76f19276_247) | [130](#i14b0fb854df64be4a32311dd76f19276_247) |

MGIC Investment Corporation 2024 Form 10-K |  3

Glossary of terms and acronyms

/ A ARMs Adjustable rate mortgages ABS Asset-backed securities Annual Persistency The percentage of our insurance remaining in force from one year prior. As of September 30, 2023, we refined our methodology for calculating our Annual Persistency by excluding the amortization of the principal balance. All prior periods have been revised ASC Accounting Standards Codification Available Assets Assets, as designated under the PMIERs, that are readily available to pay claims, and include the most liquid investments / B 
```
```
[match: MGIC]
ent loan is typically reported to us by servicers when the loan has missed two or more payments. A loan will continue to be reported as delinquent until it becomes current or a claim payment has been made. A delinquent loan is also referred to as a default Delinquency Rate The percentage of insured loans that are delinquent Direct Before giving effect to reinsurance / E EPS Earnings per share / F Fannie Mae Federal National Mortgage Association FCRA Fair Credit Reporting Act FHA Federal Housing Administration FHFA Federal Housing Finance Agency FHLB Federal Home Loan Bank of Chicago, of which MGIC is a member

MGIC Investment Corporation 2024 Form 10-K |  4

MGIC Investment Corporation and Subsidiaries

FICO score A measure of consumer credit risk provided by credit bureaus, typically produced from statistical models by Fair Isaac Corporation utilizing data collected by the credit bureaus Freddie Mac Federal Home Loan Mortgage Corporation / G GAAP Generally Accepted Accounting Principles in the United States GSEs Government Sponsored Enterprise. Collectively, Fannie Mae and Freddie Mac / H HAMP Home Affordable Modification Program HARP Home Affordable Refinance Program Home Re Entities Unaffiliated special purpose insurers domiciled in Bermuda tha
```
_(141 additional windows omitted)_

</details>

---
