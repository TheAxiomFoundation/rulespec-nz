## Phase 0: Dependency Gate

- [x] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [x] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [x] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [x] Confirm the existing personal-income-tax modules are the correct canonical surface.
- [x] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [x] Compare current personal income tax outputs against the `personal-income-tax` backlog.
- [x] Identify missing bracket, rebate, credit, withholding, and composition surfaces.
- [x] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [x] Locate the Income Tax Act and Tax Administration Act provisions plus annual amendments.
- [x] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [x] Fill personal income tax bracket and rate gaps.
- [x] Add rebate, credit, withholding, and PIE coverage where missing.
- [x] Keep family-scheme and housing-assistance logic separate.

## Phase 4: Tests and Upstream Packaging

- [x] Add companion `.test.yaml` fixtures.
- [x] Draft oracle comparison manifest skeleton for issue #32.
- [x] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [x] Prepare reviewable legal-content PR slices.

## Completion Note

- Track 28 was archived after clean review.
