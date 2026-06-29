# Track 26 Specification: Working for Families and family scheme tax credits

## Objective

Encode the Working for Families family-scheme surfaces in RuleSpec NZ so the repo
has a legal-content track for family tax credit, in-work tax credit, parental tax
credit, minimum family tax credit, and Best Start-style entitlement and abatement
rules.

## Scope

- family scheme eligibility and continuing requirements
- principal caregiver, residence, and exclusion rules
- family tax credit calculations and abatements
- in-work tax credit and child tax credit boundaries
- parental tax credit and Best Start interactions where already supported by the corpus
- minimum family tax credit and net family scheme income surfaces
- companion tests for boundary, transition, and income cases

## Out of Scope

- housing assistance surfaces
- Social Security main-benefit entitlement rules beyond cross-module eligibility inputs
- unrelated income-tax surfaces outside the family-scheme family

## Acceptance Criteria

- The relevant family-scheme modules are represented in RuleSpec with source-linked tests.
- The track has local source evidence tied to official legislation and Inland Revenue guidance.
- Comparison references remain non-authoritative and are recorded separately from legal source text.
- The roadmap reflects the dependency order for the next legislation families.
