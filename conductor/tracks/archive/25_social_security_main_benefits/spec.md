# Track 25: Social Security Act main benefits and income tests

## Scope

Fill the Social Security Act 2018 main-benefit entitlement and income-test
surface needed for full-country NZ benefit modelling.

## In Scope

- Main-benefit entitlement predicates.
- Weekly rate schedules for Jobseeker Support, Sole Parent Support, and
  Supported Living Payment.
- Income-test reductions and abatement surfaces.
- Companion RuleSpec tests for eligibility, rates, and income-test cases.

## Out of Scope

- Medical or administrative determinations outside the fiscal model.
- Oracle code as legal authority.
- Accommodation Supplement, which is tracked separately.

## Acceptance Criteria

- Main-benefit modules cite official Act, order, or MSD source evidence.
- Companion `.test.yaml` fixtures cover entitlement, rate, and income-test cases.
- Existing working social-security surfaces are reused rather than duplicated.
- An upstream issue is created and linked before opening the implementation PR.
