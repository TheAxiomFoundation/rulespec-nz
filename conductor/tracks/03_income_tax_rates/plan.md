# Project Plan - Track 3 Income Tax Rate Schedules

This plan is the active numbered Conductor surface for the income tax rate ingestion work. The older `conductor/tracks/nz_ingest_tax_rate_20260619/` record is retained as historical context.

---

## Phase 1: Source Manifest and RuleSpec Alignment

- [x] Task: Add source manifest regression test
  Write a failing repository test that requires an official-source manifest for the Income Tax Act Schedule 1 individual rate scale and checks it against the existing RuleSpec module and source map.
- [x] Task: Implement source manifest
  Add the manifest tying the RuleSpec destination to the PCO corpus citation, IRD reference URL, and comparison-oracle check.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Source Manifest and RuleSpec Alignment' (Protocol in workflow.md)

---

## Phase 2: Corpus Provision Trace

- [ ] Task: Locate Schedule 1 provision extract
  Identify the normalized PCO provision record for the Schedule 1 rate table and record the corpus locator/provision path.
- [ ] Task: Add provision trace assertions
  Test that the manifest points to an available normalized provision or records an explicit blocker.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Corpus Provision Trace' (Protocol in workflow.md)

---

## Phase 3: Oracle Fixture Cross-Check

- [ ] Task: Add nztaxmicrosim bracket fixture
  Extract a minimal pinned fixture for bracket thresholds and rates from the pinned `nztaxmicrosim` reference.
- [ ] Task: Compare fixture against RuleSpec values
  Add tests proving the fixture aligns with the official-source-backed RuleSpec values without treating the oracle as legal authority.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Oracle Fixture Cross-Check' (Protocol in workflow.md)

### Completed Implementation Commits

- `11e073a` conductor-track3-income-tax-rate-manifest


