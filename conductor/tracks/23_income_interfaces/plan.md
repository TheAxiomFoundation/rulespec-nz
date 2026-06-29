## Phase 0: Dependency Gate

- [ ] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [ ] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [ ] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [ ] Confirm the shared income-base surfaces needed by Track 24 are defined or can be factored from current rules.
- [ ] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [ ] Compare current income-tax, WFF, benefit, and ACC surfaces for duplicated or missing income interfaces.
- [ ] Identify the canonical period-conversion and annualisation gaps.
- [ ] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [ ] Locate the official legislation and agency guidance for the shared income-base surfaces.
- [ ] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [x] Encode the shared income-base definitions and bridge surfaces.
- [x] Add period conversion helpers where downstream tracks need them.
- [x] Add loss carry-over primitives where downstream tracks need them.
- [ ] Keep entitlement logic out of this track unless it is a shared primitive.

## Phase 4: Tests and Upstream Packaging

- [x] Add companion `.test.yaml` fixtures.
- [ ] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [ ] Prepare reviewable legal-content PR slices.
