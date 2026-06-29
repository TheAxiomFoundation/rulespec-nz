# Phase 0: Dependency Gate

- [x] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [x] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [x] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [x] Confirm the existing family-scheme modules are the correct canonical surface.
- [x] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

# Phase 1: Coverage Gap Inventory

- [x] Compare current Working for Families outputs against the `working-for-families` backlog.
- [x] Identify missing eligibility, credit, and abatement surfaces.
- [x] Create or link the upstream tracking issue.

# Phase 2: Source Inventory

- [x] Locate the Income Tax Act family-scheme provisions and current Inland Revenue guidance.
- [x] Record corpus citation paths or source manifests.

# Phase 3: RuleSpec Encoding

- [x] Fill family-scheme eligibility gaps.
- [x] Add tax credit and income-test coverage where missing.
- [x] Keep housing assistance separate from family-scheme logic.

# Phase 4: Tests and Upstream Packaging

- [x] Add companion `.test.yaml` fixtures.
- [x] Draft oracle comparison manifest skeleton for issue #32.
- [x] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [x] Prepare reviewable legal-content PR slices.
