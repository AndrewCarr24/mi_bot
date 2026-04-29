# Catastrophe and Hurricane Impact on MIs

> Natural catastrophes — hurricanes, wildfires, floods — can trigger a surge in mortgage delinquencies in affected areas, but private mortgage insurance policies cover borrower default, not physical property damage. The MIs have managed recent events (Hurricanes Helene and Milton in 2024, California wildfires in January 2025) with minimal expected losses, reflecting strong home equity, FEMA disaster assistance, and conservative reserving practices. The key risk is not the immediate delinquency spike but whether a catastrophe causes prolonged local economic damage that depresses home prices and elevates claim rates.

## What it is

Private mortgage insurance protects lenders against borrower default, not against physical damage to the property. When a hurricane, wildfire, or other natural disaster strikes, borrowers in the affected area may become delinquent because of job loss, displacement, or property damage that impairs their ability to pay. However, MI policies generally exclude coverage for property loss itself — the insurer's exposure is to the borrower's default, not the structural damage (RDN_10-K_2024-12-31).

The claim cycle on catastrophe-related defaults follows the same pattern as any other delinquency: the servicer reports the missed payment, the loan enters the insurer's delinquency inventory, and if the borrower does not cure (through reinstatement, loan modification, or sale), the insurer pays a claim. The critical difference is that catastrophe-related defaults often cure at higher rates than economic defaults because borrowers may receive insurance proceeds, FEMA assistance, or loan forbearance that allows them to bring the loan current (ESNT_10-K_2024-12-31).

## Why it matters

Catastrophes are a tail risk for MIs that is difficult to model precisely. Unlike credit risk, which can be priced through FICO scores and LTV ratios, catastrophe risk depends on weather patterns, climate change, and the geographic concentration of the insurer's book. Analysts watch three things:

1. **Delinquency spike magnitude** — how many new notices arrive from FEMA-designated disaster areas in the quarter following the event.
2. **Cure rates** — whether catastrophe-related defaults cure faster than normal defaults, which determines whether the spike translates into paid claims.
3. **Home price impact** — if a catastrophe destroys housing stock in a concentrated area, it can depress local home prices, increasing claim severity on loans that do go to claim.

The MIs have consistently stated that they do not expect material losses from recent events, but the risk is asymmetric: a single large catastrophe in a high-concentration area (e.g., a major hurricane hitting Miami-Dade County, where several MIs have elevated exposure) could produce a meaningful earnings event.

## Current state (as of 2025-02-28)

**Hurricanes Helene and Milton (September–October 2024):** Helene made landfall on September 26, 2024, causing damage across Florida, Georgia, South Carolina, North Carolina, Tennessee, and Virginia. Milton made landfall on October 9, 2024, primarily affecting Florida. As expected, new defaults from the affected areas increased in Q4 2024. Radian stated that absent a prolonged negative impact on local economies, it did not expect material losses from these hurricanes (RDN_10-K_2024-12-31). Essent noted that based on prior industry experience, it expected the ultimate number of hurricane-related defaults that result in claims to be less than the default-to-claim experience of non-hurricane-related defaults (ESNT_10-K_2024-12-31).

**California Wildfires (January 2025):** Multiple wildfires caused property damage in Southern California in January 2025. Essent reported that as of January 31, 2025, its insurance in force in areas with FEMA disaster declarations due to these wildfires was less than 0.1% of total insurance in force (ESNT_10-K_2024-12-31). Other MIs have not yet disclosed specific exposure figures, but given the high-value, low-LTV nature of California coastal properties, the claim severity on any defaults that do occur could be elevated.

**General reserving approach:** MIs do not establish a separate "catastrophe reserve." Instead, they set case reserves on each delinquency notice received, using the same default-to-claim and severity assumptions as for non-catastrophe defaults, adjusted for the expectation that catastrophe-related defaults cure at higher rates (ESNT_10-K_2024-12-31). This means the earnings impact is recognized as new notices come in, not as a lump-sum charge at the time of the event.

## How it has evolved

The MI industry's experience with catastrophes has been relatively benign in the post-GFC era. The COVID-19 pandemic (2020) was the most significant "disaster" event, but it was an economic shock rather than a physical catastrophe. The forbearance programs and foreclosure moratoriums that followed COVID-19 demonstrated that policy intervention can dramatically alter the default-to-claim pipeline (MTG_10-K_2024-12-31).

Prior to the current period, the most notable catastrophe events for MIs were Hurricanes Harvey, Irma, and Maria (2017), which produced delinquency spikes but ultimately resulted in manageable losses because of strong home price appreciation and FEMA assistance. The industry has not faced a catastrophe during a period of falling home prices since Hurricane Katrina (2005), which occurred in a different regulatory and housing market environment.

The key structural change is that today's MI books reflect tighter underwriting than pre-GFC business. MIs explicitly carve out their 2005-2008 vintage from later vintages in their disclosures, reflecting the higher-risk profile of that pre-crisis period (MTG_10-K_2024-12-31). The industry now conducts substantially more diligence on delegated underwriting loans than it did before the financial crisis, with MGIC's recent NIW carrying weighted-average FICOs in the high 740s (vs the lower-quality books written in 2005-2008) (MTG_10-K_2024-12-31; INDUSTRY_USMI_RESILIENCY_2023-11). This means that even if a catastrophe triggers a wave of delinquencies, borrowers in current vintages are more likely to cure through a sale (because they have equity) or to qualify for a loan modification. The MIs' risk factors acknowledge that a severe catastrophe combined with a housing downturn could produce material losses, but that scenario has not materialized in the current cycle.

## Sources

- [RDN_10-K_2024-12-31] — Describes how MI policies do not cover physical property damage, reports that Hurricanes Helene and Milton increased new defaults in Q4 2024 but that material losses are not expected absent prolonged local economic damage.
- [ESNT_10-K_2024-12-31] — Reports that hurricane-related defaults are expected to result in claims at lower rates than non-hurricane defaults; discloses California wildfire exposure was less than 0.1% of total IIF as of January 31, 2025.
- [MTG_10-K_2024-12-31] — Discusses how pandemics, hurricanes, and other disasters could trigger economic downturns in affected areas; notes that losses generally follow a seasonal trend and that natural disasters may cause delinquencies to deviate from typical patterns. Distinguishes 2005-2008 vintage NIW from later vintages and reports current weighted-average decision FICO of 747 (2024) and 753 (2023).
- [INDUSTRY_USMI_RESILIENCY_2023-11] — Industry white paper documenting post-crisis tightening of MI underwriting standards, including the shift from ~10-15% non-delegated underwriting to a substantially higher rate today.

## Related

- [[metrics/loss_ratio]]
- [[metrics/iif]]