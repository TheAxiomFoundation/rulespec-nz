## Phase 0: Dependency Gate

- [x] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [x] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [x] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [x] Confirm the existing accommodation-supplement module is the correct canonical surface.
- [x] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [x] Compare current Accommodation Supplement outputs against the `housing-assistance` backlog.
- [x] Identify missing entitlement, assets, base-rate, and income-abatement surfaces.
- [x] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [x] Locate the Social Security Act and Social Security Regulations Accommodation Supplement provisions.
- [x] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [x] Fill Accommodation Supplement entitlement gaps.
- [x] Add assets, base-rate, and income-abatement coverage where missing.
- [x] Keep main-benefit logic separate from housing-assistance logic.

## Phase 4: Tests and Upstream Packaging

- [x] Add companion `.test.yaml` fixtures.
- [x] Draft oracle comparison manifest skeleton for issue #32.
- [x] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [x] Prepare reviewable legal-content PR slices.

## Completion Note

- Track 27 was archived after clean review.
