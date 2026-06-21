# Project Plan - Track 4 Social Security Main Benefits

This plan is the active numbered Conductor surface for Social Security Act 2018 main-benefits ingestion and verification.

---

## Phase 1: Source Manifest and Existing RuleSpec Alignment

- [x] Task: Add source manifest regression test
  Write a failing repository test that requires an official-source manifest for Social Security Act 2018 main-benefit entitlement and rate schedules.
- [x] Task: Implement source manifest
  Add the manifest tying existing main-benefit RuleSpec modules to normalized PCO provision JSONL files, source-map batches, and comparison-oracle checks.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Source Manifest and Existing RuleSpec Alignment' (7427380)
  Verified on 2026-06-22 with `python -m ruff check tests\test_social_security_main_benefits_manifest.py`, `python -m basedpyright tests\test_social_security_main_benefits_manifest.py`, `python -m pytest tests\test_social_security_main_benefits_manifest.py -p no:cacheprovider`, and `python -m pytest tests -p no:cacheprovider`.

---

## Phase 2: Remaining Main-Benefit Coverage Trace

- [x] Task: Inventory remaining main-benefit surfaces (fa4fea4)
  Identify Emergency Benefit, Youth Payment, Young Parent Payment, Orphan's Benefit, Unsupported Child's Benefit, asset tests, and stand-down provisions still outside the first modules.
- [x] Task: Add coverage-gap assertions (fa4fea4)
  Test that the Track 4 manifest records implemented and deferred main-benefit surfaces explicitly.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Remaining Main-Benefit Coverage Trace' (Protocol in workflow.md)

---

## Phase 3: Oracle Fixture Cross-Check

- [ ] Task: Add main-benefit oracle fixtures
  Extract minimal pinned fixtures for Jobseeker, Sole Parent Support, and Supported Living Payment from comparison oracles.
- [ ] Task: Compare fixtures against RuleSpec values
  Add tests proving oracle fixtures align with official-source-backed RuleSpec values without treating oracles as legal authority.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Oracle Fixture Cross-Check' (Protocol in workflow.md)

### Completed Implementation Commits

- 7427380 conductor-track4-social-security-manifest

