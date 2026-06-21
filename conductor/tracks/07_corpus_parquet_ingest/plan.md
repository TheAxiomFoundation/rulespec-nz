# Track 7 Plan

## Phase 1: Adapter Contract

- [x] Add a checked-in adapter manifest for local Parquet corpus layers. (`5fc1e00`)

## Phase 2: Reader Smoke Fixtures

- [x] Add tiny synthetic Parquet or Arrow fixtures for schema-level reader validation. (`dfdcefe`)

## Phase 3: Live Local Validation

- [x] Validate against real local `corpus-legislation-nz` and `corpus-nz-hansard` exports when available. (`437ccf3`)
  Recorded partial-blocked live validation: expected environment variables are unset; a Hansard candidate export exists; adjacent legislation Parquet is from `corpus-law-nz`, not the manifest source id.

### Completed Implementation Commits

- `5fc1e00` - Added the local Parquet adapter manifest, Track 7 conductor files, and adapter contract regression tests.
- `dfdcefe` - Added local Parquet reader smoke fixtures for schema-level validation.
- `437ccf3` - Recorded Track 7 partial-blocked live local validation state.