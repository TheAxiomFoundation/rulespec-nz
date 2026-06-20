# Track Plan: OpenFisca Parsing & Transpilation Adapter

This plan implements Track 2 to build a guarded OpenFisca reference parser and future transpilation adapter.

---

## Phase 1: Guarded Oracle Reference Intake

- [~] Task: Scaffold OpenFisca oracle reference parser
  Parse `data/oracles/oracle-index.json` and `data/coverage/tax-benefit-source-map.json` to produce comparison-only OpenFisca reference manifests with pinned commits and `canonical_law: false` guardrails.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Guarded Oracle Reference Intake' (Protocol in workflow.md)

---

## Phase 2: Fixture Extraction Contracts

- [ ] Task: Define OpenFisca fixture extraction schema
  Specify how OpenFisca tests and parameters become comparison fixtures without becoming canonical law.
- [ ] Task: Implement fixture extraction dry-run
  Read selected OpenFisca-style test/parameter snippets and emit normalized in-memory fixture candidates.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Fixture Extraction Contracts' (Protocol in workflow.md)