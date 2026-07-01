# Track 6 Plan

## Phase 1: Source Manifest

- [x] Add a source-backed inventory manifest for existing New Zealand Superannuation RuleSpec modules. (`ab0154f`)

## Phase 2: Destination Reconciliation

- [x] Decide whether to keep the current split modules or add a compatibility wrapper at the source-map destination. (`3f4ef41`)
  Decision: keep the current split modules and do not add a compatibility wrapper until a downstream importer requires the source-map destination path.

## Phase 3: Oracle Fixtures

- [x] Add bounded oracle comparison fixtures for the NZ Super eligibility and rate surface. (`c2839d4`)
  Added a bounded OpenFisca eligibility fixture and recorded that the pinned oracle has no matching 2026 NZ Super rate parameters.

### Completed Implementation Commits

- `ab0154f` - Added the New Zealand Superannuation source inventory manifest, Track 6 conductor files, and manifest regression tests.
- `3f4ef41` - Recorded the New Zealand Superannuation destination reconciliation decision.
- `c2839d4` - Added the New Zealand Superannuation OpenFisca eligibility fixture.

---

## Review and Archive Note

- 2026-06-23 Conductor review outcome: archived after remediating a stale `basedpyright` suppression in `tests/test_nz_superannuation_manifest.py`.
- Passing gates rerun during review:
  - `python -m pytest tests\test_nz_superannuation_manifest.py -q -p no:cacheprovider`
  - `python -m ruff check tests\test_nz_superannuation_manifest.py`
  - `python -m basedpyright tests\test_nz_superannuation_manifest.py`
  - `python -m pytest tests\test_repository_layout.py -q -p no:cacheprovider`
- Residual risk: no live PCO re-download was performed; review is based on committed normalized provision extracts and manifest evidence.
- Oracle limitation: the pinned OpenFisca fixture covers eligibility and explicitly records that matching 2026 NZ Super rate parameters are not available in the pinned oracle.
