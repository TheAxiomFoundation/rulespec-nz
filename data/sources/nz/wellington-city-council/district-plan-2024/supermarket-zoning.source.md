# Official source snapshot — Wellington City 2024 District Plan (supermarket zoning)

Retained provenance artifact for
`nz/regulations/rma_district_plans/wellington_city/supermarket_zoning.yaml`.
Per .github#39 rule 7, a new encoding whose provisions are not yet in the bound
corpus release must land the official source snapshot with URL + retrieval date +
sha256 alongside. This district plan is an instrument made under Schedule 1 of the
Resource Management Act 1991; it is not PCO legislation and is not in the bound
release `nz-rulespec-2026-07-10`.

## Source

- Publisher: Wellington City Council (territorial authority).
- Instrument: **Wellington City 2024 District Plan** (operative), served via the
  IsoPlan ePlan as "Wellington City 2024 District Plan: Appeals Version".
- Plan version fetched: IsoPlan revision **137**, as at **14-Jul-2026**.
- Retrieved (UTC date): **2026-07-15**.
- Operative status: the 2024 District Plan became operative in stages; parts were
  made operative from 7 June 2024 following the Council's ISPP decisions
  (notified 20 March 2024). The zone provisions below are served as operative in
  the ePlan (marked with the "made operative" gavel).

## Endpoints and payload digests (sha256 of the exact JSON retrieved)

Host: `https://eplan.wellington.govt.nz/proposed/`

| Content | URL | sha256 |
| --- | --- | --- |
| Definitions + chapter index (rev 137) | `api/l/rev/137/14-Jul-2026/1` | `942da6652498c50d25acc99e0d6c83fe3ca227d1552d0a211eaf802b1c0e507a` |
| City Centre Zone (CCZ), section 228 | `api/l/r/228/0/false/14-Jul-2026/false` | `c7ff26d3efe96851e1f07665ffe8be7549a40ed9444a078f11e6e0e8c499d9ea` |
| Metropolitan Centre Zone (MCZ), section 229 | `api/l/r/229/0/false/14-Jul-2026/false` | `1b6001ee1272ee1989d798303257c18e3c3a22c87fb9332e18edfb1ff736b7b1` |
| Mixed Use Zone (MUZ), section 231 | `api/l/r/231/0/false/14-Jul-2026/false` | `f26eb6a4f0d13d4978f662da26c177163e479f59da9e295ff6c6a4e589e1cdb6` |
| Local Centre Zone (LCZ), section 232 | `api/l/r/232/0/false/14-Jul-2026/false` | `366226df467e74f5b835958dd060565381a79d365b9d7990c22e418543566d07` |
| Neighbourhood Centre Zone (NCZ), section 233 | `api/l/r/233/0/false/14-Jul-2026/false` | `09c3d98f6efef5c675dec6de2c6a14c3bddf9b0fa16c7c79001f79c5316e87b7` |
| General Industrial Zone (GIZ), section 235 | `api/l/r/235/0/false/14-Jul-2026/false` | `ee6cab9e05e78c6289160ed3cebd389f9bda5df99e3a9122fecf41c30d8d117d` |

## Definitions (verbatim)

- **Supermarket** — "means a retail shop selling a wide range of foodstuffs,
  including fresh produce, meat, fish, dairy, alcoholic and other beverages, and
  packaged food for consumption off-site, as well as non-food grocery items and
  household goods. This definition includes discount stores, hypermarkets,
  department stores and warehouse club stores, where foodstuffs comprise more than
  10% of the total gross floor area."
- **Retail activity** — "an activity displaying or offering services or goods for
  the sale or hire to the trade or public and includes, but is not limited to:
  integrated retail developments, trade supply retail, yard based retail,
  supermarkets, service retail, and ancillary retail."
- **Gross floor area** — "means the sum of the total area of all floors of a
  building or buildings (including any void area in each of those floors, such as
  service shafts, liftwells or stairwells), measured: where there are exterior
  walls, from the exterior faces of those exterior walls; where there are walls
  separating two buildings, from the centre lines of the walls separating the two
  buildings; where a wall or walls are lacking (for example, a mezzanine floor) and
  the edge of the floor is discernible, from the edge of the floor."
- **Commercial activity** — "means any activity trading in goods, equipment or
  services. It includes any ancillary activity to the commercial activity (for
  example administrative or head offices)."
- **Integrated retail activity** — "means an individual retail development, or a
  collection of any two or more retail activities that are developed and operate as
  a coherent entity ... This definition includes shopping malls and large-format
  retail parks, but does not include trade supply retail, wholesale retail..."
- **Large format retail** — "means any individual retail activity exceeding 450m²
  gross floor area."

## Zone rules (verbatim — activity status for a supermarket)

- **CCZ-R1 Commercial activities** — "Activity status: Permitted" (no integrated-retail
  carve-out; no GFA cap). (No supermarket-specific rule in CCZ.)
- **MCZ-R1 Commercial activities** — "Activity status: Permitted Where: The activity is
  not an Integrated Retail Activity (refer to Rule MCZ-R13)."
  **MCZ-R13 Integrated retail activity** — "Activity status: Permitted" (no GFA cap).
- **LCZ-R1 Commercial activities** — "Activity status: Permitted Where: The activity is
  not an Integrated Retail Activity (refer to Rule LCZ-R11)."
  **LCZ-R11 Integrated retail activity** — "Activity status: Permitted Where: The total
  gross floor area does not exceed 20,000m²." (else Restricted Discretionary).
- **NCZ-R1 Commercial activities** — "Activity status: Permitted Where: The activity is
  not an Integrated Retail Activity (refer to Rule NCZ-R11)."
  **NCZ-R11 Integrated retail activity** — "Activity status: Permitted Where: The total
  gross floor area does not exceed 10,000m²." (else Restricted Discretionary).
- **MUZ-R1 Commercial activities** — "Activity status: Permitted Where: The activity is
  not an Integrated Retail Activity (refer to Rule MUZ-R12); and The activity is not a
  supermarket (refer to MUZ-R13)."
  **MUZ-R13 Supermarkets** —
    - MUZ-R13.1: "Activity status: Permitted Where: The total gross floor area does not
      exceed 1,500m²."
    - MUZ-R13.2: "Activity status: Restricted Discretionary Where: Compliance with the
      requirements of MUZ-R13.1 is not achieved. Matters of discretion are: The matters
      in MUZ-P3."
  **MUZ-P3 Managing larger-scale retail activities** — "Only allow the establishment of
  integrated retail activities and large supermarkets in the Mixed Use Zone if it can be
  demonstrated that they will: Not result in significant adverse impacts on the vitality,
  role and function of the City Centre or any Metropolitan, Local or Neighbourhood
  Centres; Not result in significant adverse impacts on the sustainability, safety or
  efficiency of the transport network and the hierarchy of roads from trip patterns,
  travel demand or vehicle use; and Be compatible with adjoining land uses."
- **GIZ-R5 Commercial activities** — "Activity status: Permitted Where: The activity is
  trade supply retail, a wholesaler, a building improvement centre, service retail or
  yard based retail." / "Activity status: Non-complying Where: Compliance with the
  requirements of GIZ-R5.1 is not achieved."
  **GIZ-P4 Commercial activities** — "Avoid commercial activities in the General
  Industrial Zone except for: Office, retail and other commercial activities which are
  ancillary to industrial activities; and Trade supply retail, wholesalers, building
  improvement centres, service retail and yard based retail."
