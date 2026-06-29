## Phase 0: Dependency Gate

- [x] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [x] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [x] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [x] Confirm the existing main-benefits entitlement and rate modules are the correct canonical surface.
- [x] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [x] Compare current Social Security outputs against the `social-security-main-benefits` backlog.
- [x] Identify missing entitlement, rate, and income-test surfaces.
- [x] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [x] Locate the Social Security Act provisions and any 2026 rate orders or MSD guidance.
- [x] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [x] Fill main-benefit entitlement gaps.
- [x] Add rate and income-test coverage where missing.
- [x] Keep accommodation support separate from main-benefit logic.

## Phase 4: Tests and Upstream Packaging

- [x] Add companion `.test.yaml` fixtures.
- [x] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [x] Prepare reviewable legal-content PR slices.

## Completion Note

- Track 25 is packaged locally and ready for review.
