# Phase 0: Dependency Gate

- [x] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [x] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [x] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [x] Confirm the shared income-base surfaces needed by Track 24 are defined or can be factored from current rules.
- [x] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

# Phase 1: Coverage Gap Inventory

- [x] Compare current income-tax, benefit, and ACC surfaces for duplicated or missing income interfaces.
- [x] Identify the canonical period-conversion and annualisation gaps.
- [x] Create or link the upstream tracking issue.

# Phase 2: Source Inventory

- [x] Locate the official legislation and agency guidance for the shared income-base surfaces.
- [x] Record corpus citation paths or source manifests.

# Phase 3: RuleSpec Encoding

- [x] Encode the shared income-base definitions and bridge surfaces.
- [x] Add period conversion helpers where downstream tracks need them.
- [x] Add loss carry-over primitives where downstream tracks need them.
- [x] Add the shared activity-income bridge for business/self-employment inputs.
- [x] Add the shared employment-income bridge for salary and wage inputs.
- [x] Add the shared schedular-income bridge for withholding-style inputs.
- [x] Add a combined shared-income bridge total for downstream consumers.
- [x] Keep entitlement logic out of this track unless it is a shared primitive.

# Phase 4: Tests and Upstream Packaging

- [x] Add companion `.test.yaml` fixtures.
- [x] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [x] Prepare reviewable legal-content PR slices.
