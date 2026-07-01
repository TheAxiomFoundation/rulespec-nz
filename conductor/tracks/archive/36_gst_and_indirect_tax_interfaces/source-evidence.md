# Source Evidence: GST and indirect-tax interfaces

## Track

- Track id: 36_gst_and_indirect_tax_interfaces
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/61
- Policy family: GST and indirect-tax interfaces

## Official Source Family

- Act, regulation, order, or official agency table: Goods and Services Tax Act 1985; Customs and Excise Act 2018; IRD GST guidance.
- Administering agency: Inland Revenue.
- Source status: source inventory pinned for the implemented GST slice.
- Publication state checked: yes.
- Core official references:
  - Goods and Services Tax Act 1985: `nz/statute/act/public/1985/0141`
  - Customs and Excise Act 2018: `nz/statute/act/public/2018/0004`
  - Inland Revenue GST guidance: `nz/agency/ird/gst-rates`, `nz/agency/ird/gst-low-value-imported-goods`

## Corpus Evidence

- Corpus source manifest: `data/corpus/inventory/nz/tax-benefit-pco-locators.json`
- Corpus citation path(s):
  - `nz/statute/act/public/1985/0141/section/8-DLM82299`
  - `nz/statute/act/public/1985/0141/section/10`
  - `nz/statute/act/public/1985/0141/section/12`
  - `nz/statute/act/public/2018/0004`
- Source ingestion command or run id: `2026-06-16-pco-latest`
- Known extraction gaps: low-value imported goods are encoded as an interface hook and may be expanded with excise-specific detail later.

## RuleSpec Scope

- Rules: GST rate; GST inclusive/exclusive calculations; low-value imported goods interfaces; excise interfaces for future distributional analysis.
- Parameters: thresholds, rate tables, and entitlement limits where applicable.
- Definitions: legal predicates and income-interface primitives where needed.
- Eligibility predicates: entitlement and exclusion conditions.
- Date-effective surfaces: rate and threshold changes by effective date.
- Comparison oracles remain non-authoritative and must be recorded separately from legal source text.

## Current Implementation Slice

- `nz/statutes/gst/rate.yaml`
- `nz/statutes/gst/rate.test.yaml`

## Companion Tests

- Scenario families: boundary, threshold, and date-effective cases.
- Expected outputs: entitlement holds / not_holds predicates, weekly or annual amounts, and reduced or zero-payment outcomes.
- Edge cases: threshold crossings, term transitions, and dependent-status changes.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Interpretation questions: whether the GST import interface should later be split into a dedicated module if excise hooks grow beyond the low-value goods surface.
- Missing official evidence: none for the implemented GST slice.
- Blockers: foundation gates #30, #31, #32 remain relevant for comparison-only reconciliation, but not for the official-source implementation slice.

