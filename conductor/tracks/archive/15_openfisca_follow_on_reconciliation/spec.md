# Track 15: OpenFisca Follow-on Reconciliation

## Goal

Complete OpenFisca Aotearoa follow-on surfaces by converting every deferred surface into official-source extraction, RuleSpec encoding, or a comparison-only fixture.

## Scope

- Reconcile the pinned OpenFisca commit before live-head fixture refresh.
- Use OpenFisca variables, parameters, tests, entities, and ontology files as discovery and comparison material only.
- Source canonical RuleSpec from official New Zealand legislation, regulations, or agency rate tables.
- Update `data/coverage/rulespec-rule-inventory.json` as modules are added or extended.
- Record duplicate or overlapping surfaces before claiming completion.

## Acceptance Criteria

- Every deferred surface has an encoded artifact, extraction artifact, or exact source blocker.
- Duplicate or overlapping RuleSpec modules are recorded with triangulation method and reconciliation status.
- Comparison fixtures remain non-authoritative and pinned to an oracle commit.
- Focused OpenFisca reconciliation and rule inventory tests pass.
