# Plan: nztaxmicrosim Rule Incorporation

## Phase 1: Pinned Oracle Inventory

- [x] Task: Verify live upstream HEAD and pinned oracle commit.
- [x] Task: Clone the pinned source into ignored `.tmp/` for inspection.
- [x] Task: Create `data/oracles/nztaxmicrosim-rule-inventory.json`.
- [x] Task: Add tests that validate the inventory, source pin, and non-authoritative boundary.

## Phase 2: Source Authority Mapping

- [x] Task: For each inventory surface, map the official Act, regulation, or agency table required for canonical RuleSpec.
- [x] Task: Extend source mapping with `data/coverage/nztaxmicrosim-source-map.json` where current source mapping lacked per-oracle surface detail.
- [x] Task: Identify placeholder/simplified oracle logic that can only be used as fixture smoke evidence.
- [x] Task: Create a per-surface implementation order that avoids duplicating existing RuleSpec modules.
- [x] Task: Add tests that validate source-authority mapping, existing companion tests, blockers, and implementation order.

## Phase 3: Existing Coverage Reconciliation

- [x] Task: Compare inventory surfaces to current files under `nz/`.
- [x] Task: Mark already-covered surfaces and record their current companion tests.
- [x] Task: Identify partial coverage gaps inside existing modules such as income tax credits, family scheme, main benefits, ACC, GST, and accommodation supplement.
- [x] Task: Add regression fixtures from `nztaxmicrosim` only where they test implemented official-source rules.

## Phase 4: RuleSpec Implementation Closeout

- [x] Task: Reconcile payroll deductions, paid parental leave, PIE/RWT, and child support to named official-source extraction follow-on tracks rather than oracle code copying.
- [x] Task: Reconcile donation credit, FamilyBoost, WFF, benefits, accommodation, ACC, and historical income-tax coverage against existing official-source modules and partial gaps.
- [x] Task: Record closeout status, approved comparison fixtures, and follow-on extraction units in `data/coverage/nztaxmicrosim-reconciliation.json`.

## Phase 5: Validation, Review Remediation, and Archive

- [x] Task: Run focused unit tests for source mapping, reconciliation, and oracle fixture boundaries.
- [x] Task: Run oracle fixture comparison tests against approved `nztaxmicrosim` snapshots.
- [x] Task: Run quality gates: `python -m ruff check`, `python -m ruff format --check`, `python -m pytest -q -p no:cacheprovider`, `python -m basedpyright`, and `cargo test --manifest-path rulespec-nz\Cargo.toml --no-default-features`.
- [x] Task: Remediate review finding by updating acceptance criteria to require implementation or named official-source follow-on extraction for missing canonical surfaces.
- [x] Task: Archive Track 12 after review remediation.

## Closeout Artifacts

- `data/oracles/nztaxmicrosim-rule-inventory.json`
- `data/coverage/nztaxmicrosim-source-map.json`
- `data/coverage/nztaxmicrosim-reconciliation.json`
- `tests/test_nztaxmicrosim_rule_inventory.py`
- `tests/test_nztaxmicrosim_source_map.py`
- `tests/test_nztaxmicrosim_reconciliation.py`
