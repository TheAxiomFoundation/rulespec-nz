# Track 30 Specification: Student support and StudyLink surfaces

## Objective

Encode the Student Support / StudyLink allowance surfaces in RuleSpec NZ so
the repo covers the deferred student-allowance family with official-source
eligibility, means-testing, and rate logic.

## Scope

- student allowance eligibility and exclusion rules
- parental and partner income tests
- independent circumstances and age-based eligibility
- allowance rate and payment-period surfaces where officially sourced
- reuse of existing student-loan repayment and income-interface primitives
- companion tests for boundary, transition, and income cases

## Out of Scope

- paid parental leave surfaces
- child support surfaces
- unrelated tax or benefit families outside student support

## Acceptance Criteria

- The relevant student-support modules are represented in RuleSpec with
  source-linked tests.
- The track has local source evidence tied to official legislation and
  StudyLink / TEC guidance.
- Comparison references remain non-authoritative and are recorded separately
  from legal source text.
- The roadmap reflects the dependency order for the next legislation families.
