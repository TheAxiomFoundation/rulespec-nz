# Track 6 Plan

## Phase 1: Source Manifest

- [x] Add a source-backed inventory manifest for existing New Zealand Superannuation RuleSpec modules. (`ab0154f`)

## Phase 2: Destination Reconciliation

- [x] Decide whether to keep the current split modules or add a compatibility wrapper at the source-map destination. (`3f4ef41`)
  Decision: keep the current split modules and do not add a compatibility wrapper until a downstream importer requires the source-map destination path.

## Phase 3: Oracle Fixtures

- [ ] Add bounded oracle comparison fixtures for the NZ Super eligibility and rate surface.

### Completed Implementation Commits

- `ab0154f` - Added the New Zealand Superannuation source inventory manifest, Track 6 conductor files, and manifest regression tests.
- `3f4ef41` - Recorded the New Zealand Superannuation destination reconciliation decision.
