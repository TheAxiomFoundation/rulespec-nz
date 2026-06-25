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

- [x] Task: Locate GST section 10 provision extract (91248fe)
  Identify or generate the normalized PCO provision record for Goods and Services Tax Act 1985 section 10.
- [x] Task: Add complete GST trace assertions (91248fe)
  Test that the GST module has available normalized provision records for sections 8, 10, and 12.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Complete GST Corpus Trace' (91248fe)
  Verified on 2026-06-22 with `python -m pytest tests\test_gst_acc_levies_manifest.py -p no:cacheprovider` red before implementation, then green with `python -m pytest tests\test_gst_acc_levies_manifest.py -p no:cacheprovider`, `python -m ruff check tests\test_gst_acc_levies_manifest.py`, `python -m basedpyright tests\test_gst_acc_levies_manifest.py`, and `python -m pytest tests -p no:cacheprovider`.

---

## Phase 3: Oracle Fixture Cross-Check

- [x] Task: Add GST and ACC comparison fixtures (d3ece10)
  Extract minimal pinned fixtures for GST calculations and ACC earners' levy scenarios from comparison or agency references.
- [x] Task: Compare fixtures against RuleSpec values (d3ece10)
  Add tests proving fixtures align with official-source-backed RuleSpec values without treating oracles as legal authority.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Oracle Fixture Cross-Check' (d3ece10)
  Verified on 2026-06-22 with `python -m pytest tests\test_gst_acc_levies_manifest.py -p no:cacheprovider` red before implementation, then green with `python -m pytest tests\test_gst_acc_levies_manifest.py -p no:cacheprovider`, `python -m ruff check tests\test_gst_acc_levies_manifest.py`, `python -m basedpyright tests\test_gst_acc_levies_manifest.py`, and `python -m pytest tests -p no:cacheprovider`.

### Completed Implementation Commits

- 7a9fe3d conductor-track5-gst-acc-manifest
- 91248fe Resolve_track5_gst_section10_trace
- d3ece10 Add_track5_gst_acc_oracle_fixtures

---

## Review and Archive Note

- 2026-06-23 Conductor review outcome: archived after clean review.
- Passing gates rerun during review:
  - `python -m pytest tests\test_gst_acc_levies_manifest.py -q -p no:cacheprovider`
  - `python -m ruff check tests\test_gst_acc_levies_manifest.py`
  - `python -m basedpyright tests\test_gst_acc_levies_manifest.py`
  - `python -m pytest tests\test_repository_layout.py -q -p no:cacheprovider`
- Residual risk: no live PCO re-download was performed; review is based on committed normalized provision extracts and manifest evidence.

