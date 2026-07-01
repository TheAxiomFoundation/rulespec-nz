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
  - official StudyLink calculator assets:
    - https://www.studylink.govt.nz/products/rates/calculators/parental-income-calculator.html
    - https://www.studylink.govt.nz/products/rates/calculators/student-allowance-rate-calculator.html
    - https://www.studylink.govt.nz/webadmin/scripts/parental-income-calculator.js?v=2018
    - https://www.studylink.govt.nz/webadmin/scripts/student-abated-net-allowance-calculator.js?v=2018

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): the citation paths listed above plus the existing student-loan repayment module for shared-income inputs.
- Source ingestion command or run id: official StudyLink calculator asset extraction completed in this session.
- Known extraction gaps: corpus citation paths and oracle manifests still need final pinning for upstream packaging.

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

- Interpretation questions: whether to split the encoded surface further into dedicated basic-grant and parental-income submodules.
- Missing official evidence: final corpus citation paths for the allowance rates and means tests still need to be pinned to the corpus extract.
- Blockers: foundation gates #30, #31, #32; oracle comparison remains blocked until pinned manifests are published.
