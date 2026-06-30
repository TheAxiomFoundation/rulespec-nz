# Source Evidence: Student support and StudyLink surfaces

## Track

- Track id: `30_student_support_studylink`
- Upstream issue: pending
- Policy family: Student support and StudyLink

## Official Source Family

- Act, regulation, order, or official agency table: Student Allowances Regulations 1998; Education and Training Act 2020; Student Loan Scheme Act 2011; official StudyLink and TEC guidance.
- Administering agency: Studylink; Ministry of Social Development; Inland Revenue.
- Source status: source inventory recorded for the student-support surface.
- Publication state checked: yes.
- Core official references:
  - nz/regulation/1998/0277
  - nz/statute/act/public/2011/0067
  - nz/agency/tec/student-allowances

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): the citation paths listed above plus the existing student-loan repayment module for shared-income inputs.
- Source ingestion command or run id: pending.
- Known extraction gaps: student allowance rates and means tests remain deferred in the current module.

## RuleSpec Scope

- Rules: allowance eligibility, parental and partner means tests, independent circumstances, and payment surfaces.
- Parameters: age thresholds, income thresholds, and allowance rates.
- Definitions: student-support income, dependency, and residency primitives.
- Eligibility predicates: allowance entitlement and exclusion conditions.
- Date-effective surfaces: allowance and threshold changes by effective date.
- Student loan repayment logic is already encoded elsewhere and should be reused as an input surface.

## Current Implementation Slice

- `nz/regulations/student_allowances/core.yaml`
- `nz/regulations/student_allowances/core.test.yaml`
- `nz/statutes/student_loan/repayments.yaml`
- `nz/statutes/student_loan/repayments.test.yaml`

## Companion Tests

- Scenario families: eligibility, parental income, partner income, independence, allowance rate, and threshold cases.
- Expected outputs: entitlement holds / not_holds predicates, weekly payment amounts, and reduced or zero-payment outcomes.
- Edge cases: threshold crossings, term transitions, and dependent-status changes.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Interpretation questions: how much of the existing deferred module is already covered by the current source inventory.
- Missing official evidence: source citation paths for the allowance rates and means tests still need to be pinned to the final corpus extract.
- Blockers: foundation gates #30, #31, #32; oracle comparison remains blocked until pinned manifests are published.

