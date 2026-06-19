# Project Plan - NZ Legislation Ingestion and Income Tax Rate Encodings

This plan tracks the step-by-step tasks required to implement the first track.

---

## Phase 1: Ingest and Normalize Legislation

- [ ] Task: Environment Setup and Tooling Validation
  Ensure Pixi environment is active, and verified to run python/ruff/basedpyright and toolchain binaries.
- [ ] Task: Write Tests for XML download integration
  Write integration tests ensuring PCO API key validation and API requests return expected shapes.
- [ ] Task: Ingest Income Tax Act 2007 XML
  Execute download-nz-legislation-api command to pull primary xml files.
- [ ] Task: Write Tests for Extraction normalization
  Write tests that assert legislation extraction parses sections, subsections, and dates correctly.
- [ ] Task: Extract and Normalize Provisions
  Run the normalization parser to output source manifests to `data/corpus/`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Ingest and Normalize Legislation' (Protocol in workflow.md)

---

## Phase 2: Establish Comparison References

- [ ] Task: Write Tests for Reference Extraction
  Write test expectations for expected tax rates and brackets scenarios generated from references.
- [ ] Task: Extract Scenarios from Comparison Oracles
  Extract comparative datasets from `nztaxmicrosim` or the Treasury prototype to cross-check outputs.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Establish Comparison References' (Protocol in workflow.md)

---

## Phase 3: Encode RuleSpec Modules

- [ ] Task: Write Failing Test Scenarios for Income Tax Rates
  Define rate schedules inputs and expected outcomes in `nz/statutes/income_tax/rate.test.yaml` (Red Phase).
- [ ] Task: Implement Income Tax Rate Rules
  Create rule declarations in `nz/statutes/income_tax/rate.yaml` to pass the tests (Green Phase).
- [ ] Task: Verify Quality Gates
  Verify >90% test coverage, run mutation testing, check with `basedpyright`, and lint with `ruff` (ALL checks).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Encode RuleSpec Modules' (Protocol in workflow.md)
