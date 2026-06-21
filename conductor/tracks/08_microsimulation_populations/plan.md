# Track 8 Plan

## Phase 1: Builder Contract

- [x] Add a checked-in synthetic population builder manifest for local generator integrations. (`11b5f50`)

## Phase 2: Fixture Smoke Data

- [x] Add tiny JSONL or Arrow-compatible synthetic fixtures for schema-level validation. (`1d975f3`)

## Phase 3: Live Local Generator Validation

- [ ] Validate against real local `open_social_data` and `fyi-cli` outputs when available.

### Completed Implementation Commits

- `11b5f50` - Added the synthetic population builder manifest, Track 8 conductor files, and builder contract regression tests.
- `1d975f3` - Added tiny synthetic-only JSONL smoke fixtures for entity schema validation.