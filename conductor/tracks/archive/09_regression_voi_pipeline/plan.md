# Track 9 Plan

## Phase 1: Pipeline Contract

- [x] Add a checked-in regression and VOI pipeline manifest for external analysis handoffs. (`92a3dfc`)

## Phase 2: Fixture Outputs

- [x] Add tiny regression and VOI fixture outputs for schema-level validation. (`77a384e`)

## Phase 3: Live Local Analysis Validation

- [x] Validate against real local `mars` and `voiage` workflows when available. (`34e232c`)

### Completed Implementation Commits

- `92a3dfc` - Added the regression/VOI pipeline manifest, Track 9 conductor files, and pipeline contract regression tests.
- `77a384e` - Added synthetic regression/VOI fixture outputs, summary report, and schema validation tests.
- `34e232c` - Recorded blocked live validation state for missing local mars/voiage workflows.

### Review and Archive Note

- 2026-06-23 Conductor review outcome: archived after adding a regression assertion that completed fixture-output and live-validation phases do not reappear in `deferred_work`.
- Passing gates rerun during review:
  - `python -m pytest tests\test_regression_voi_pipeline_manifest.py -q -p no:cacheprovider`
  - `python -m ruff check tests\test_regression_voi_pipeline_manifest.py`
  - `python -m basedpyright tests\test_regression_voi_pipeline_manifest.py`
  - `python -m pytest tests\test_repository_layout.py -q -p no:cacheprovider`
- Residual blocker: live validation remains `blocked_missing_local_workflows` because `RULESPEC_NZ_MARS_DIR` and `RULESPEC_NZ_VOIAGE_DIR` are unset and no adjacent local checkouts were found.
