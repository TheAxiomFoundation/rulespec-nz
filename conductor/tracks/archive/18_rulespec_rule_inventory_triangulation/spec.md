# Track 18: RuleSpec Rule Inventory and Triangulation

## Goal

Keep a machine-readable record of RuleSpec modules currently encoded in the repo, including source families, oracle overlaps, duplicate clusters, and reconciliation status.

## Scope

- Maintain `data/coverage/rulespec-rule-inventory.json`.
- Ensure every non-test RuleSpec YAML module under `nz/` appears in the inventory.
- Record duplicate or overlapping policy concepts before they are encoded twice.
- Triangulate conflicts using official source authority first, then pinned comparison oracles, then supporting fixtures.

## Acceptance Criteria

- The inventory covers every checked-in non-test RuleSpec module.
- Every inventory module declares source families, authority, and source route.
- Every duplicate cluster declares a canonical module, overlapping modules, source systems, triangulation method, and reconciliation status.
- Tests fail when a new RuleSpec module is added without inventory coverage.
