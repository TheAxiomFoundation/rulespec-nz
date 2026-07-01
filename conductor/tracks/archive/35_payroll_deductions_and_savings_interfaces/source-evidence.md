# Source Evidence: Payroll deductions and savings interfaces

## Track

- Track id: 35_payroll_deductions_and_savings_interfaces
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/60
- Policy family: Payroll deductions and savings interfaces

## Official Source Family

- Act, regulation, order, or official agency table: KiwiSaver Act 2006; Student Loan Scheme Act 2011; Income Tax Act 2007 PAYE provisions; IRD contribution and deduction guidance.
- Administering agency: Inland Revenue.
- Source status: source inventory pinned for this track.
- Publication state checked: yes.
- Core official references:
  - KiwiSaver Act 2006: `nz/statute/act/public/2006/0040`
  - Student Loan Scheme Act 2011: `nz/statute/act/public/2011/0062`
  - Income Tax Act 2007: `nz/statute/act/public/2007/0097`

## Corpus Evidence

- Corpus source manifest: `data/corpus/inventory/nz/tax-benefit-pco-locators.json`
- Corpus citation path(s):
  - `nz/statute/act/public/2006/0040`
  - `nz/statute/act/public/2011/0062`
  - `nz/statute/act/public/2007/0097`
- Source ingestion command or run id: `2026-06-16-pco-latest`
- Known extraction gaps: no section-level evidence gaps for the implemented payroll interfaces.

## RuleSpec Scope

- Rules: KiwiSaver employee contribution rates; KiwiSaver employer contribution interfaces; student loan deductions; PAYE periodization.
- Parameters: thresholds, rate tables, and entitlement limits where applicable.
- Definitions: legal predicates and income-interface primitives where needed.
- Eligibility predicates: entitlement and exclusion conditions.
- Date-effective surfaces: rate and threshold changes by effective date.
- Comparison oracles remain non-authoritative and must be recorded separately from legal source text.

## Current Implementation Slice

- `nz/statutes/kiwisaver/contributions.yaml`
- `nz/statutes/student_loan/repayments.yaml`
- `nz/statutes/payroll/deductions.yaml`

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

- Interpretation questions: how much further payroll-specific periodization should be split out from the shared PAYE aggregation helper.
- Missing official evidence: none for the implemented slice.
- Blockers: foundation gates #30, #31, #32 remain relevant for comparison-only reconciliation, but not for the official-source implementation slice.
