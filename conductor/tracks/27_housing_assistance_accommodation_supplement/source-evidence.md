# Source Evidence: Housing assistance, especially Accommodation Supplement

## Track

- Track id: `27_housing_assistance_accommodation_supplement`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/34
- Policy family: Housing assistance and Accommodation Supplement

## Official Source Family

- Act, regulation, order, or official agency table: Social Security Act 2018; Social Security Regulations 2018; official MSD Accommodation Supplement guidance and rate tables.
- Administering agency: MSD.
- Source status: source inventory recorded for the Accommodation Supplement surface.
- Publication state checked: yes.
- Core official references:
  - data/corpus/provisions/nz/statute/2026-06-17-accommodation-supplement-core.jsonl
  - data/corpus/provisions/nz/regulation/2026-06-17-accommodation-supplement-regulations.jsonl

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: pending.

## RuleSpec Scope

- Rules: entitlement, assets tests, area tables, and accommodation-cost abatement surfaces.
- Parameters: cash-asset thresholds, max weekly rates, area and family-category tables, and income-abatement ratios.
- Definitions: accommodation costs, weekly qualifying accommodation costs, and assessed base-rate primitives.
- Eligibility predicates: entitlement and exclusion conditions.
- Date-effective surfaces: rate and threshold changes by effective date.
- Main-benefit logic remains in the separate social-security track.

## Current Implementation Slice

- `nz/statutes/social_security/accommodation_supplement/core.yaml`
- Companion tests where already present in the module

## Companion Tests

- Scenario families: entitlement, asset threshold, area, base-rate, and income-abatement cases.
- Expected outputs: entitlement holds / not_holds predicates, assessed base rates, abatements, and net weekly supplement amounts.
- Edge cases: threshold crossings, family-category boundaries, and rate-table transitions.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Interpretation questions: how much of the existing surface already covers the target backlog.
- Missing official evidence: source citation paths pending.
- Blockers: foundation gates #30, #31, #32; oracle comparison remains blocked until pinned manifests are published.
