# Track 20: Working for Families and Family Scheme Tax Credits

## Scope

Encode the Working for Families and family scheme tax credit surface as NZ RuleSpec modules with official source provenance and companion tests.

## In Scope

- Family Tax Credit.
- In-Work Tax Credit.
- Minimum Family Tax Credit.
- Best Start.
- Principal caregiver, qualifying child, dependent child, and family income tests.
- Legacy parental tax credit and child tax credit handling where needed for historical coverage.

## Out of Scope

- Mechanical migration from OpenFisca, PolicyEngine, or nztaxmicrosim as legal authority.
- Raw official XML dumps.
- Unrelated payroll, student loan, or KiwiSaver surfaces except where required for income tests.

## Acceptance Criteria

- RuleSpec modules exist under the appropriate `nz/statutes/`, `nz/regulations/`, or `nz/policies/` roots.
- Each encoded rule cites official NZ source/corpus evidence.
- Companion `.test.yaml` fixtures cover eligibility, rates, abatement, and edge cases.
- Oracle comparisons are recorded as non-authoritative checks only.
- Upstream issue `#33` is referenced in the implementation PR.
