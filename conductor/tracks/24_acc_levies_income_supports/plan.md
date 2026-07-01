## Phase 0: Dependency Gate

- [ ] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [ ] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [ ] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [ ] Confirm Track 23 income interfaces cover the income bases needed by ACC levy calculations.
- [ ] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [ ] Compare current ACC/GST Track 5 outputs against the `levies-acc` backlog.
- [ ] Identify missing levy and income-support surfaces.
- [ ] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [ ] Locate Accident Compensation Act 2001 provisions.
- [ ] Locate ACC levy regulations, rate notices, and official ACC/IRD guidance.
- [ ] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [ ] Fill earners' levy and liable-income gaps.
- [ ] Add maximum liable earnings and self-employed parameters where missing.
- [ ] Encode weekly compensation and loss-of-potential-earnings interfaces needed for tax-benefit modelling.

## Phase 4: Tests and Upstream Packaging

- [ ] Add companion `.test.yaml` fixtures.
- [ ] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [ ] Prepare reviewable legal-content PR slices.
