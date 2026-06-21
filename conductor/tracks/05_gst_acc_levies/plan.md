# Project Plan - Track 5 GST and ACC Levies

This plan is the active numbered Conductor surface for GST and ACC levy ingestion and verification.

---

## Phase 1: Source Manifest and Existing RuleSpec Alignment

- [x] Task: Add source manifest regression test
  Write a failing repository test that requires an official-source manifest for GST and ACC levy RuleSpec modules.
- [x] Task: Implement source manifest
  Add the manifest tying existing GST and ACC RuleSpec modules to normalized PCO provision JSONL files, source-map batches, agency references, and known corpus gaps.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Source Manifest and Existing RuleSpec Alignment' (7a9fe3d)
  Verified on 2026-06-22 with `python -m ruff check tests\test_gst_acc_levies_manifest.py`, `python -m basedpyright tests\test_gst_acc_levies_manifest.py`, `python -m pytest tests\test_gst_acc_levies_manifest.py -p no:cacheprovider`, and `python -m pytest tests -p no:cacheprovider`.

---

## Phase 2: Complete GST Corpus Trace

- [ ] Task: Locate GST section 10 provision extract
  Identify or generate the normalized PCO provision record for Goods and Services Tax Act 1985 section 10.
- [ ] Task: Add complete GST trace assertions
  Test that the GST module has available normalized provision records for sections 8, 10, and 12.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Complete GST Corpus Trace' (Protocol in workflow.md)

---

## Phase 3: Oracle Fixture Cross-Check

- [ ] Task: Add GST and ACC comparison fixtures
  Extract minimal pinned fixtures for GST calculations and ACC earners' levy scenarios from comparison or agency references.
- [ ] Task: Compare fixtures against RuleSpec values
  Add tests proving fixtures align with official-source-backed RuleSpec values without treating oracles as legal authority.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Oracle Fixture Cross-Check' (Protocol in workflow.md)

### Completed Implementation Commits

- 7a9fe3d conductor-track5-gst-acc-manifest

