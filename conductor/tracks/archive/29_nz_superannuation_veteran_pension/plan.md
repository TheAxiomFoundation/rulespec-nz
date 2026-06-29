## Phase 0: Dependency Gate

- [x] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [x] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [x] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [x] Confirm the existing NZ Super modules are the correct canonical surface.
- [x] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [x] Compare current NZ Super outputs against the `superannuation` backlog.
- [x] Identify missing qualification, rate, and special-rate surfaces.
- [x] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [x] Locate the New Zealand Superannuation and Retirement Income Act and veteran pension sources.
- [x] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [x] Fill NZ Super qualification and rate gaps.
- [x] Add special-rate and hospital-rate coverage where missing.
- [x] Keep veteran pension and related cross-benefit logic separate where appropriate.

## Phase 4: Tests and Upstream Packaging

- [x] Add companion `.test.yaml` fixtures.
- [x] Draft oracle comparison manifest skeleton for issue #32.
- [x] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [x] Prepare reviewable legal-content PR slices.

## Completion Note

- Track 29 was archived after clean review.
