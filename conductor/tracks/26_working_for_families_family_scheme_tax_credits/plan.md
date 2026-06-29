## Phase 0: Dependency Gate

- [ ] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [ ] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [ ] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [ ] Confirm the existing family-scheme modules are the correct canonical surface.
- [ ] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [ ] Compare current Working for Families outputs against the `working-for-families` backlog.
- [ ] Identify missing eligibility, credit, and abatement surfaces.
- [ ] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [ ] Locate the Income Tax Act family-scheme provisions and current Inland Revenue guidance.
- [ ] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [ ] Fill family-scheme eligibility gaps.
- [ ] Add tax credit and income-test coverage where missing.
- [ ] Keep housing assistance separate from family-scheme logic.

## Phase 4: Tests and Upstream Packaging

- [ ] Add companion `.test.yaml` fixtures.
- [ ] Draft oracle comparison manifest skeleton for issue #32.
- [ ] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [ ] Prepare reviewable legal-content PR slices.
