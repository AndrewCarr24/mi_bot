# Insurance in Force (IIF)

> Insurance in Force (IIF) represents the total aggregate unpaid principal balance of all loans insured by a mortgage insurer at a given point in time. It is the primary measure of an MI's in-force book size and a key driver of future premium revenue. IIF grows through new insurance written (NIW) and shrinks through policy cancellations, principal paydowns, and claims paid. As of year-end 2024, the six MIs collectively held over $1.7 trillion in primary IIF, with MGIC and Radian reporting $295.4 billion and $275.1 billion respectively.

## What it is

IIF is the sum of the unpaid principal balances (UPB) of all loans in an MI's primary insurance portfolio. It is distinct from Risk in Force (RIF), which is the portion of IIF that the insurer is actually on the hook for — typically 25-30% of IIF, reflecting the coverage percentage on each loan. The Freddie Mac PMI Handbook notes that standard coverage requirements range from 6% to 35% of the loan balance depending on LTV and loan type (INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09).

The roll-forward of IIF is straightforward: beginning IIF + NIW − cancellations − principal paydowns − claims paid = ending IIF. MGIC's 2024 10-K illustrates this dynamic: $55.7 billion of NIW was offset by $53.8 billion in cancellations, principal payments, and other reductions, yielding a net increase of $1.9 billion (MTG_10-K_2024-12-31). Radian's comparable figures show $275.1 billion in primary IIF at December 31, 2024, up from $270.0 billion a year earlier (RDN_10-K_2024-12-31).

## Why it matters

IIF is the fundamental top-line metric for a mortgage insurer. Premiums earned are directly proportional to IIF — more IIF means more premium revenue, all else equal. The relationship is especially strong for monthly premium policies, which now dominate the industry. Radian notes that 90% of its primary RIF is on monthly and other recurring premium policies, meaning "an increase in IIF generally has a corresponding positive impact on premiums earned" (RDN_10-K_2024-12-31).

Analysts watch IIF growth as a proxy for the health of the origination market (NIW) and the stickiness of the existing book (persistency). A flat or declining IIF signals either weak origination volumes or elevated refinancing activity that erodes the book. Conversely, rising IIF in a high-rate environment — as seen in 2023-2024 — indicates that high persistency (borrowers unwilling to refinance into higher rates) is offsetting lower NIW.

IIF also determines capital requirements under PMIERs. More IIF means more required assets, so IIF growth must be supported by commensurate capital generation or reinsurance usage.

## Current state (as of 2024-12-31)

Primary insurance in force across the six US MIs at December 31, 2024:

| MI | Primary IIF (2024) | Source |
|---|---|---|
| MGIC | $295.4B | MTG_10-K_2024-12-31 |
| Arch (US primary mortgage) | $290.4B | ACGL_10-K_2024-12-31 |
| Radian | $275.1B | RDN_10-K_2024-12-31 |
| Enact | $268.8B | ACT_10-K_2024-12-31 |
| Essent | $243.6B | ESNT_10-K_2024-12-31 |
| NMI Holdings | $210.2B | NMIH_10-K_2024-12-31 |

The six MIs collectively held roughly $1.58 trillion of primary IIF at year-end 2024 (excluding Arch's CRT and international mortgage books, which add another ~$210B of IIF on the Arch platform alone). MGIC is the largest by IIF, narrowly ahead of Arch's US primary book.

Trajectory: MGIC's IIF was up 0.6% from $293.5 billion at year-end 2023, with $55.7 billion of NIW in 2024 (up from $46.1 billion in 2023) (MTG_10-K_2024-12-31). Radian's IIF was up from $270.0 billion at year-end 2023, with an average coverage percentage of 26.2% (RDN_10-K_2024-12-31). MGIC's management expects IIF to remain "relatively flat in 2025" given the interest rate outlook (MTG_10-K_2024-12-31); Radian subsequently reported $282.5 billion of IIF at year-end 2025 (RDN_10-K_2025-12-31), and NMIH grew to $221.4 billion (NMIH_10-K_2025-12-31).

## How it has evolved

IIF across the industry has grown steadily since the post-GFC recovery, but the trajectory has been shaped by interest rate cycles. From 2018 through early 2021, low mortgage rates drove a refinancing wave that depressed persistency and caused IIF to shrink or grow slowly — MGIC's persistency bottomed at 60.7% in March 2021 (MTG_10-K_2024-12-31). As rates rose sharply in 2022-2023, refinancing collapsed, persistency surged to the mid-80% range, and IIF began growing again even as NIW declined.

Radian's IIF trajectory illustrates the trend: $261.0 billion at year-end 2022, $270.0 billion at year-end 2023, and $275.1 billion at year-end 2024 (RDN_10-K_2024-12-31). The growth rate has decelerated as the initial persistency boost from rate increases has matured.

The composition of IIF has also shifted toward higher-credit-quality vintages. Radian reports that 60.1% of its primary RIF carries FICO scores of 740 or above, and 67.7% has LTVs of 90% or below (RDN_10-K_2024-12-31). This credit quality improvement is a structural feature of the post-2009 origination environment.

## Sources

- [MTG_10-K_2024-12-31] — Provided MGIC's IIF of $295.4B, NIW of $55.7B, the IIF roll-forward, persistency history, and management's 2025 outlook.
- [RDN_10-K_2024-12-31] — Provided Radian's IIF of $275.1B, average coverage percentage, premium type composition, and credit profile breakdown.
- [RDN_10-K_2025-12-31] — Provided Radian's year-end 2025 IIF of $282.5B and continuing-operations financial framing.
- [ACGL_10-K_2024-12-31] — Provided Arch's US primary mortgage IIF of $290.4B at year-end 2024 and the segment composition (US primary / US CRT / international).
- [ACT_10-K_2024-12-31] — Provided Enact's primary IIF of $268.8B at year-end 2024.
- [ESNT_10-K_2024-12-31] — Provided Essent's primary IIF of $243.6B at year-end 2024.
- [NMIH_10-K_2024-12-31] — Provided NMI Holdings' primary IIF of $210.2B at year-end 2024.
- [NMIH_10-K_2025-12-31] — Provided NMI Holdings' primary IIF of $221.4B at year-end 2025.
- [INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09] — Provided the regulatory context for standard MI coverage requirements by LTV tier.

## Related

- [[metrics/niw]]
- [[metrics/persistency]]