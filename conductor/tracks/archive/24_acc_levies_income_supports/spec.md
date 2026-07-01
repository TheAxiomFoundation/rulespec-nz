# Track 24: ACC Levies and Income Support Surfaces

## Scope

Fill ACC levy and ACC-related income support coverage required for full-country NZ tax-benefit modelling.

## In Scope

- Earners' levy rate and liable income.
- Maximum liable earnings.
- Self-employed and low-income levy parameters where needed.
- Weekly compensation abatement.
- Loss of potential earnings.
- Minimum weekly earnings and related income support predicates.

## Out of Scope

- Clinical entitlement administration unrelated to fiscal modelling.
- Detailed employer/work-account pricing beyond individual tax-benefit interfaces.
- Oracle code as legal authority.

## Acceptance Criteria

- ACC levy and income-support modules cite official Act, regulation, rate notice, or IRD/ACC source evidence.
- Companion `.test.yaml` fixtures cover employed, self-employed, threshold, and compensation scenarios.
- Existing GST/ACC Track 5 coverage is reused rather than duplicated.
- An upstream issue is created and linked before opening the implementation PR.
