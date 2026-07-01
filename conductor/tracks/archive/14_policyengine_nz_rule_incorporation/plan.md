# Plan: PolicyEngine NZ Rule Incorporation

## Phase 1: Pin and Inventory Reconciliation

- [x] Task: Create `data/oracles/policyengine-nz-rule-inventory.json`.
- [x] Task: Add tests that validate the inventory and supporting-reference boundary.
- [x] Task: Decide whether to upgrade `data/oracles/oracle-index.json` to the observed upstream HEAD.
- [x] Task: If the pin is upgraded, update adapter tests and source-map references in the same PR slice.

## Phase 2: Existing Coverage Reconciliation

- [x] Task: Map PolicyEngine income-tax and Working for Families surfaces to current `nz/statutes/income_tax/` modules.
- [x] Task: Map ACC and GST surfaces to current RuleSpec roots.
- [x] Task: Mark already covered surfaces as `covered`, partial surfaces as `partial`, and new surfaces as `missing`.

## Phase 3: Fixture Extraction

- [x] Task: Extract representative PolicyEngine policy tests into supporting reference evidence manifests.
- [x] Task: Keep fixtures labelled `canonical_law: false` and `authority: supporting_reference`.
- [x] Task: Add fixture checks only where official-source RuleSpec implementations exist.
- [x] Task: Record unavailable fixtures as blocked supporting reference evidence rather than legal blockers.

## Phase 4: Canonical RuleSpec Implementation

- [x] Task: Implement missing KiwiSaver surfaces from official legislation and IRD guidance.
- [x] Task: Record remaining income tax and Working for Families partial gaps as supporting-reference reconciliation follow-ons before canonical encoding.

## Phase 5: Validation and Review

- [x] Task: Run unit, integration, and E2E tests for each implemented RuleSpec surface.
- [x] Task: Run full quality gates before review and archive.
