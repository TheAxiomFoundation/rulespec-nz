# Source Evidence: Social Security Act main benefits and income tests

## Track

- Track id: `25_social_security_main_benefits`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/49
- Policy family: social security main benefits
- Implementation PR: not opened yet; package is review-ready.

## Official Source Family

- Act, regulation, order, or official agency table: Social Security Act 2018; Social Security (Rates of Benefits and Allowances) Order 2026; official MSD guidance.
- Administering agency: MSD.
- Source status: official Act, order, and MSD guidance encoded in module source verification.
- Publication state checked: current implementation slice targets the 2026-04-01 effective date used in the module manifests.

## Corpus Evidence

- Corpus source manifest: embedded in the module source_verification blocks.
- Corpus citation path(s): `nz/statute/act/public/2018/0032/section/16`, `nz/statute/act/public/2018/0032/section/18`, `nz/statute/act/public/2018/0032/section/19`, `nz/statute/act/public/2018/0032/section/20`, `nz/statute/act/public/2018/0032/section/21`, `nz/statute/act/public/2018/0032/section/22`, `nz/statute/act/public/2018/0032/section/23`, `nz/statute/act/public/2018/0032/section/24`, `nz/statute/act/public/2018/0032/section/25`, `nz/statute/act/public/2018/0032/section/26`, `nz/statute/act/public/2018/0032/section/29`, `nz/statute/act/public/2018/0032/section/30`, `nz/statute/act/public/2018/0032/section/31`, `nz/statute/act/public/2018/0032/section/32`, `nz/statute/act/public/2018/0032/section/33`, `nz/statute/act/public/2018/0032/section/34`, `nz/statute/act/public/2018/0032/section/35`, `nz/statute/act/public/2018/0032/section/36`, `nz/statute/act/public/2018/0032/section/39`, `nz/statute/act/public/2018/0032/section/40`, `nz/statute/act/public/2018/0032/schedule/2/definition/income-test-1`, `nz/statute/act/public/2018/0032/schedule/2/definition/income-test-2`, `nz/statute/act/public/2018/0032/schedule/2/definition/income-test-3`, `nz/statute/act/public/2018/0032/schedule/2/definition/income-test-4`, `nz/statute/act/public/2018/0032/schedule/4/part/1`, `nz/statute/act/public/2018/0032/schedule/4/part/2`, `nz/statute/act/public/2018/0032/schedule/4/part/3`, `nz/secondary-legislation/pco-drafted/2026/36/clause/5`.
- Source ingestion command or run id: not required for this slice; citations are already resolved in the encoded manifests.
- Known extraction gaps: none identified for the implemented surfaces.

## RuleSpec Scope

- Rules: entitlement predicates, weekly rates, income-test reductions, and benefit-specific abatement surfaces.
- Parameters: benefit ages, thresholds, and weekly rate tables.
- Definitions: main-benefit eligibility and rate bridge primitives.
- Eligibility predicates: main-benefit entitlement and income-test conditions.
- Date-effective surfaces: benefit rates and income-test changes by effective date.

## Current Implementation Slice

- `nz/statutes/social_security/main_benefits/rates.test.yaml`
- `nz/statutes/social_security/main_benefits/entitlement.test.yaml`

## Companion Tests

- Scenario families: entitlement, single-parent, supported-living, and income-test cases.
- Expected outputs: entitlement, rate, and income-test fixtures in the companion `.test.yaml` files.
- Edge cases: threshold crossings and rate-order transitions.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: comparison-only oracle pin still managed separately under foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: any oracle deltas are treated as comparison-only and do not override official sources.

## Residual Risk

- Interpretation questions: how much of the existing surface already covers the target backlog.
- Missing official evidence: none for the implemented slice.
- Blockers: none for the implementation slice; remaining work is review and upstream packaging.
