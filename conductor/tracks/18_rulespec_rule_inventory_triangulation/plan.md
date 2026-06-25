## Phase 1: Initial Inventory

- [x] Create `data/coverage/rulespec-rule-inventory.json`.
- [x] Add test coverage requiring every RuleSpec module to be inventoried.
- [x] Add duplicate clusters for current high-overlap tax-benefit surfaces.

## Phase 2: Rule-level Extraction

- [ ] Add generated rule-name extraction from each RuleSpec YAML file.
- [ ] Extend tests so every declared `rules[].name` is represented in the inventory.
- [ ] Add stable identifiers for rule-level provenance and duplicate detection.

## Phase 3: Reconciliation Workflow

- [ ] Link duplicate clusters to OpenFisca, PolicyEngine, and nztaxmicrosim reconciliation surfaces.
- [ ] Add conflict status fields for value, scope, and stale-oracle mismatches.
- [ ] Require a recorded official-source decision before resolving a conflict.

## Phase 4: Reporting

- [ ] Generate a compact completion scorecard from the inventory.
- [ ] Add a status view for encoded, extracted-not-encoded, deferred, and blocked surfaces.
