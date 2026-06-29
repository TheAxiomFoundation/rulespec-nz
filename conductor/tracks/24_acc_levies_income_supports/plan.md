## Phase 0: Dependency Gate

- [x] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [x] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [x] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [x] Confirm Track 23 income interfaces cover the income bases needed by ACC levy calculations.
- [x] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [x] Compare current ACC/GST Track 5 outputs against the `levies-acc` backlog.
- [x] Identify missing levy and income-support surfaces.
- [x] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [x] Locate Accident Compensation Act 2001 provisions.
- [x] Locate ACC levy regulations, rate notices, and official ACC/IRD guidance.
- [x] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [x] Fill earners' levy and liable-income gaps.
- [x] Add maximum liable earnings and self-employed parameters where missing.
- [x] Encode weekly compensation and loss-of-potential-earnings interfaces needed for tax-benefit modelling.

## Phase 4: Tests and Upstream Packaging

- [x] Add companion `.test.yaml` fixtures.
- [x] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [x] Prepare reviewable legal-content PR slices.
