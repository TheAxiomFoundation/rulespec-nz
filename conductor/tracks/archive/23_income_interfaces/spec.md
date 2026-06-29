# Track 23: Income Interfaces

## Scope

Define the shared income interfaces needed by downstream tax, welfare, and ACC
tracks so they can consume the same canonical income-base surfaces.

## In Scope

- Employment, salary, and wage income interfaces.
- Business, self-employment, and taxable-income bridge surfaces.
- Annualisation, period alignment, and loss/gain carry-over interfaces.
- Shared income bases used by Working for Families, Social Security, and ACC.
- Official-source manifests and companion RuleSpec tests for the shared layer.

## Out of Scope

- Product-specific entitlement logic for any single benefit or levy.
- Oracle code as legal authority.
- Re-encoding downstream rules that already belong in a dedicated track.

## Acceptance Criteria

- Shared income-interface rules exist under the appropriate `nz/` surface.
- Companion `.test.yaml` fixtures cover period alignment and bridge cases.
- Source manifests cite official Acts, regulations, or agency guidance.
- Track 24 can reference the income interfaces without duplicating them.
- An upstream issue is created and linked before opening the implementation PR.
