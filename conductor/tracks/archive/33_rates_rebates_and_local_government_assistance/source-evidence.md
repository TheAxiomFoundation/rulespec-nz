# Source Evidence: Rates rebates and local-government-adjacent assistance

## Track

- Track id: `33_rates_rebates_and_local_government_assistance`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/58
- Policy family: Rates rebates and local-government-adjacent assistance

## Official Source Family

- Act, regulation, order, or official agency table: Rates Rebate Act 1973; Rates Rebate Regulations; DIA rates rebate guidance.
- Administering agency: Relevant administering agency.
- Source status: source inventory and legal scope were pinned during implementation.
- Publication state checked: yes.
- Core official references: Rates Rebate Act 1973; Rates Rebate (Specified Amounts) Orders 2024, 2025, and 2026; DIA rates rebate guidance.

## Corpus Evidence

- Corpus source manifest: not retained in this archive slice.
- Corpus citation path(s): recorded in the RuleSpec module `source_verification` entries.
- Source ingestion command or run id: implemented from official law and agency guidance during the track.
- Known extraction gaps: local-authority administration details may still be expanded in later rates-related slices.

## RuleSpec Scope

- Rules: rates rebate maximum allowable; income threshold; initial contribution; additional dependant amount; local authority interaction.
- Parameters: thresholds, rate tables, and entitlement limits where applicable.
- Definitions: legal predicates and income-interface primitives where needed.
- Eligibility predicates: entitlement and exclusion conditions.
- Date-effective surfaces: rate and threshold changes by effective date.
- Comparison oracles remain non-authoritative and must be recorded separately from legal source text.

## Current Implementation Slice

- income thresholds, SuperGold threshold variant, household-income aggregation, and territorial authority application gating

## Companion Tests

- Scenario families: boundary, threshold, and date-effective cases.
- Expected outputs: entitlement holds / not_holds predicates, weekly or annual amounts, and reduced or zero-payment outcomes.
- Edge cases: threshold crossings, term transitions, and dependent-status changes.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: not applicable for this archived slice.
- Comparison role: non-authoritative only.
- Known divergences: none recorded for this archived slice.
- Upstream comparison guidance: compare against pinned oracle/reference fixtures only.

## Residual Risk

- Interpretation questions: later local-government-adjacent assistance slices may still be added separately.
- Missing official evidence: none for this archived slice.
- Blockers: none for this archived slice; oracle comparison remains non-authoritative.

