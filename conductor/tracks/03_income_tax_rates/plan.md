# Project Plan - Track 3 Income Tax Rate Schedules

This plan is the active numbered Conductor surface for the income tax rate ingestion work. The older `conductor/tracks/nz_ingest_tax_rate_20260619/` record is retained as historical context.

---

## Phase 1: Source Manifest and RuleSpec Alignment

- [x] Task: Add source manifest regression test
  Write a failing repository test that requires an official-source manifest for the Income Tax Act Schedule 1 individual rate scale and checks it against the existing RuleSpec module and source map.
- [x] Task: Implement source manifest
  Add the manifest tying the RuleSpec destination to the PCO corpus citation, IRD reference URL, and comparison-oracle check.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Source Manifest and RuleSpec Alignment' (eb5735d)
  Verified on 2026-06-22 with `python -m ruff check tests\test_income_tax_rate_source_manifest.py`, `python -m basedpyright tests\test_income_tax_rate_source_manifest.py`, `python -m pytest tests\test_income_tax_rate_source_manifest.py -p no:cacheprovider`, and `python -m pytest tests -p no:cacheprovider`.

---

## Phase 2: Corpus Provision Trace

- [x] Task: Locate Schedule 1 provision extract (f265c33)
  Identify the normalized PCO provision record for the Schedule 1 rate table and record the corpus locator/provision path.
- [x] Task: Add provision trace assertions (f265c33)
  Test that the manifest points to an available normalized provision or records an explicit blocker.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Corpus Provision Trace' (f265c33)
  Verified on 2026-06-22 with `python -m ruff check tests\test_income_tax_rate_source_manifest.py`, `python -m basedpyright tests\test_income_tax_rate_source_manifest.py`, `python -m pytest tests\test_income_tax_rate_source_manifest.py -p no:cacheprovider`, and `python -m pytest tests -p no:cacheprovider`.

---

## Phase 3: Oracle Fixture Cross-Check

- [x] Task: Add nztaxmicrosim bracket fixture (bf0def7)
  Extract a minimal pinned fixture for bracket thresholds and rates from the pinned `nztaxmicrosim` reference.
- [x] Task: Compare fixture against RuleSpec values (bf0def7)
  Add tests proving the fixture aligns with the official-source-backed RuleSpec values without treating the oracle as legal authority.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Oracle Fixture Cross-Check' (bf0def7)
  Verified on 2026-06-22 with `python -m ruff check tests\test_income_tax_rate_source_manifest.py`, `python -m basedpyright tests\test_income_tax_rate_source_manifest.py`, `python -m pytest tests\test_income_tax_rate_source_manifest.py -p no:cacheprovider`, and `python -m pytest tests -p no:cacheprovider`.

### Completed Implementation Commits

- `11e073a` conductor-track3-income-tax-rate-manifest
- `eb5735d` Harden Track 3 manifest test typing and verification gates
- `f265c33` Add Track 3 Schedule 1 provision trace
- `bf0def7` Add Track 3 nztaxmicrosim bracket fixture


