# Plan: OpenFisca Aotearoa Rule Incorporation

## Phase 1: Pin and Inventory Reconciliation

- [x] Task: Verify live upstream HEAD for `edithatogo/openfisca-aotearoa`.
- [x] Task: Inspect live variable, parameter, and situation-test counts in ignored `.tmp/`.
- [x] Task: Create `data/oracles/openfisca-aotearoa-rule-inventory.json`.
- [x] Task: Add tests that validate the inventory and comparison-only boundary.
- [x] Task: Decide whether to upgrade `data/oracles/oracle-index.json` from `c36c40bcf553dc95ddca473be12440d4be9d0560` to `76062ffc20e40373d9cb56c8910a224236aa1e72`.
- [x] Task: Retain the current oracle-index pin for deterministic fixtures and record live-head reconciliation as `openfisca-aotearoa-pin-reconciliation`.

## Phase 2: Existing Coverage Reconciliation

- [x] Task: Map OpenFisca income-tax and family-scheme surfaces to current `nz/statutes/income_tax/` modules.
- [x] Task: Map OpenFisca social-security and accommodation surfaces to current `nz/statutes/social_security/` modules.
- [x] Task: Map OpenFisca ACC, superannuation, childcare, disability, community-services-card, GST-adjacent, and rates-rebate surfaces to current RuleSpec roots.
- [x] Task: Mark already covered surfaces as implemented existing coverage, partial surfaces as partial official-source reconciliation, and new surfaces as official-source extraction follow-ons.
- [x] Task: Create `data/coverage/openfisca-aotearoa-source-map.json`.

## Phase 3: Fixture Extraction

- [x] Task: Approve existing representative OpenFisca fixture manifests for surfaces with current official-source RuleSpec coverage.
- [x] Task: Keep fixtures labelled `canonical_law: false` and `authority: comparison_oracle` through manifest tests.
- [x] Task: Add fixture checks only where official-source RuleSpec implementations exist.
- [x] Task: Record unavailable, live-head, or not-yet-official-source fixtures as follow-on comparison evidence rather than legal blockers.

## Phase 4: Canonical RuleSpec Implementation

- [x] Task: Reconcile currently implemented official-source RuleSpec modules for income tax, family scheme, main benefits, accommodation supplement, ACC earners levy, community services card, disability allowance, child disability allowance, winter energy payment, and NZ Super.
- [x] Task: Defer missing citizenship, immigration, student allowance, parental leave, rates rebates, housing restructuring, relationship, demographic, ACC weekly-compensation, and Pae Ora surfaces to named official-source extraction tracks.
- [x] Task: Record the official sources and planned RuleSpec destinations for every deferred surface.
- [x] Task: Create `data/coverage/openfisca-aotearoa-reconciliation.json`.

## Phase 5: Validation and Review

- [x] Task: Add unit tests for inventory, source-map, reconciliation, fixture boundaries, and Conductor bookkeeping.
- [x] Task: Run focused OpenFisca Aotearoa implementation tests.
- [x] Task: Run JSON validation, `python -m ruff check programs tests test_bindings.py`, `python -m ruff format --check programs tests test_bindings.py`, `basedpyright`, `python -m pytest -q -p no:cacheprovider`, and `cargo test --manifest-path rulespec-nz\Cargo.toml --no-default-features`.
- [x] Task: Conduct Conductor review and remediate findings before archive.
  - Review completed 2026-06-26: All 16 Track 13 tests pass, lint clean, format clean, 125/125 full suite tests pass.
  - No remediation findings: every deferred surface is already recorded as a named official-source extraction follow-on.
  - Residual risk: no live PCO re-download was performed; review is based on committed normalized provision extracts and manifest evidence.
