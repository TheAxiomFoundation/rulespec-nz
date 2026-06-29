## Phase 0: Dependency Gate

- [ ] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [ ] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [ ] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [ ] Confirm the existing NZ Super modules are the correct canonical surface.
- [ ] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [ ] Compare current NZ Super outputs against the `superannuation` backlog.
- [ ] Identify missing qualification, rate, and special-rate surfaces.
- [ ] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [ ] Locate the New Zealand Superannuation and Retirement Income Act and veteran pension sources.
- [ ] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [ ] Fill NZ Super qualification and rate gaps.
- [ ] Add special-rate and hospital-rate coverage where missing.
- [ ] Keep veteran pension and related cross-benefit logic separate where appropriate.

## Phase 4: Tests and Upstream Packaging

- [ ] Add companion `.test.yaml` fixtures.
- [ ] Draft oracle comparison manifest skeleton for issue #32.
- [ ] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [ ] Prepare reviewable legal-content PR slices.
