# Source Evidence: Social Security Act Main Benefits and Income Tests

## Track

- Track id: `22_social_security_main_benefits_income_tests`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/35
- Policy family: Social Security main benefits
- Implementation PR: pending

## Official Source Family

- Act, regulation, order, or official agency table: Social Security Act 2018; Social Security Regulations 2018; official MSD/Work and Income benefit rate tables.
- Administering agency: Ministry of Social Development; Work and Income.
- Source status: pending foundation gate #31.
- Publication state checked: pending.

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: pending.

## RuleSpec Scope

- Rules: Jobseeker Support, Sole Parent Support, Supported Living Payment, Emergency Benefit, Youth Payment, Young Parent Payment.
- Parameters: rates, income thresholds, abatement settings, asset thresholds where relevant.
- Definitions: residence, relationship status, dependent child, work capacity, age.
- Eligibility predicates: benefit-specific eligibility, income/assets, residence, relationship, dependent-child predicates.
- Date-effective surfaces: rate tables and threshold changes.

## Companion Tests

- Scenario families: single adult, sole parent, couple, youth, disability/work-capacity, income changes.
- Expected outputs: pending.
- Edge cases: threshold crossings, relationship status changes, dependent-child transitions.
- Historical/date-effective cases: pending.

## Oracle Comparison

- Oracle/reference: OpenFisca Aotearoa; nztaxmicrosim where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.

## Residual Risk

- Interpretation questions: relationship and work-capacity boundaries.
- Missing official evidence: source citation paths pending.
- Blockers: foundation gates #30, #31, #32.
