# Track 22: Social Security Act Main Benefits and Income Tests

## Scope

Encode core Social Security Act main benefit eligibility, rates, and income-test surfaces with official source provenance.

## In Scope

- Jobseeker Support.
- Sole Parent Support.
- Supported Living Payment.
- Emergency Benefit.
- Youth Payment and Young Parent Payment.
- Income, asset, residence, relationship, and dependent-child tests.
- Official benefit-rate table interfaces.

## Out of Scope

- Supplementary assistance handled by separate housing, disability, childcare, or emergency-assistance tracks.
- Oracle code as legal authority.
- Raw source payload dumps.

## Acceptance Criteria

- Encoded surfaces cite official Act, regulation, or MSD table evidence.
- Companion `.test.yaml` files cover representative eligibility and abatement cases.
- Definitions shared with other tracks are factored into common modules where appropriate.
- Upstream issue `#35` is referenced in the implementation PR.
