# Source Evidence: Social Security Act main benefits and income tests

## Track

- Track id: `25_social_security_main_benefits`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/49
- Policy family: social security main benefits
- Implementation PR: https://github.com/TheAxiomFoundation/rulespec-nz/pull/51

## Official Source Family

- Act, regulation, order, or official agency table: Social Security Act 2018; Social Security (Rates of Benefits and Allowances) Order 2026; official MSD guidance.
- Administering agency: MSD.
- Source status: source inventory recorded for the 2026 main-benefit surface.
- Publication state checked: yes.
- Core official references:
  - https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2026/36/en/latest/
  - https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2026/36/en/2026-03-02B.pdf
  - https://www.msd.govt.nz/about-msd-and-our-work/publications-resources/statistics/benefit/2026/benefit-fact-sheet-snapshot-march-2026.pdf
  - https://www.msd.govt.nz/what-we-can-do/community/carers/guide-for-carers/money/financial-support/supported-living-payment.html

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: pending.

## RuleSpec Scope

- Rules: entitlement predicates, weekly rates, income-test reductions, and benefit-specific abatement surfaces.
- Parameters: benefit ages, thresholds, and weekly rate tables.
- Definitions: main-benefit eligibility and rate bridge primitives.
- Eligibility predicates: main-benefit entitlement and income-test conditions.
- Date-effective surfaces: benefit rates and income-test changes by effective date.
- Accommodation Supplement remains in its separate module at `nz/statutes/social_security/accommodation_supplement/core.yaml`.

## Current Implementation Slice

- `nz/statutes/social_security/main_benefits/rates.test.yaml`
- `nz/statutes/social_security/main_benefits/entitlement.test.yaml`
- Implementation PR 51 also carries the ACC track scaffold and weekly-compensation slice, so the review must be read as a combined branch package.
- Oracle comparison draft: `conductor/tracks/25_social_security_main_benefits/oracle-comparison-draft.md`
- Pinned-manifest draft: `conductor/tracks/25_social_security_main_benefits/oracle-manifest-draft.json`

## Companion Tests

- Scenario families: entitlement, single-parent, supported-living, and income-test cases.
- Expected outputs: entitlement holds / not_holds predicates, weekly rates, income-test reductions, and Supported Living Payment blind subsidy.
- Edge cases: threshold crossings, rate-order transitions, branch coverage for standard jobseeker, under-25 jobseeker, full-time student disqualification, partnered supported-living, and under-18 supported-living paths, long-term residential care halving, and blind subsidy caps.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845
- Local pinned-manifest skeleton: `conductor/tracks/25_social_security_main_benefits/oracle-manifest-draft.json`

## Residual Risk

- Interpretation questions: how much of the existing surface already covers the target backlog.
- Missing official evidence: source citation paths pending.
- Blockers: foundation gates #30, #31, #32; oracle comparison remains blocked until pinned manifests are published.
