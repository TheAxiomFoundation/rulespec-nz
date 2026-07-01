# Track 8 Plan

## Phase 1: Builder Contract

- [x] Add a checked-in synthetic population builder manifest for local generator integrations. (`11b5f50`)

## Phase 2: Fixture Smoke Data

- [x] Add tiny JSONL or Arrow-compatible synthetic fixtures for schema-level validation. (`1d975f3`)

## Phase 3: Live Local Generator Validation

- [x] Validate against real local `open_social_data` and `fyi-cli` outputs when available. (`ba30658`)
  Recorded partial-blocked live validation: expected environment variables are unset and no compatible persons, households, and benefit_units generator output was found without running generators.

### Completed Implementation Commits

- `11b5f50` - Added the synthetic population builder manifest, Track 8 conductor files, and builder contract regression tests.
- `1d975f3` - Added tiny synthetic-only JSONL smoke fixtures for entity schema validation.
- `ba30658` - Recorded Track 8 partial-blocked live local generator validation state.

### Review and Archive Note

- 2026-06-23 Conductor review outcome: archived after confirming the stale `deferred_work` prose remediation in `data/microsimulation/synthetic-population-builder.json`.
- Passing gates rerun during review:
  - `python -m pytest tests\test_synthetic_population_builder_manifest.py -q -p no:cacheprovider`
  - `python -m ruff check tests\test_synthetic_population_builder_manifest.py`
  - `python -m basedpyright tests\test_synthetic_population_builder_manifest.py`
  - `python -m pytest tests\test_repository_layout.py -q -p no:cacheprovider`
- Residual blocker: live validation remains `partial_blocked` because required generator environment variables are unset and compatible persons, households, and benefit_units output was not found without running generators.
