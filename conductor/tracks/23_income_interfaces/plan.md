# Phase 0: Dependency Gate

- [x] [2153670] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [x] [2153670] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [x] [2153670] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [x] [2153670] Confirm the shared income-base surfaces needed by Track 24 are defined or can be factored from current rules.
- [x] [2153670] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

# Phase 1: Coverage Gap Inventory

- [x] [2153670] Compare current income-tax, benefit, and ACC surfaces for duplicated or missing income interfaces.
- [x] [2153670] Identify the canonical period-conversion and annualisation gaps.
- [x] [2153670] Create or link the upstream tracking issue.

# Phase 2: Source Inventory

- [x] [2153670] Locate the official legislation and agency guidance for the shared income-base surfaces.
- [x] [2153670] Record corpus citation paths or source manifests.

# Phase 3: RuleSpec Encoding

- [x] [2153670] Encode the shared income-base definitions and bridge surfaces.
- [x] [2153670] Add period conversion helpers where downstream tracks need them.
- [x] [2153670] Add loss carry-over primitives where downstream tracks need them.
- [x] [2153670] Add the shared activity-income bridge for business/self-employment inputs.
- [x] [2153670] Add the shared employment-income bridge for salary and wage inputs.
- [x] [2153670] Add the shared schedular-income bridge for withholding-style inputs.
- [x] [2153670] Add a combined shared-income bridge total for downstream consumers.
- [x] [2153670] Keep entitlement logic out of this track unless it is a shared primitive.

# Phase 4: Tests and Upstream Packaging

- [x] [2153670] Add companion `.test.yaml` fixtures.
- [x] [2153670] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [x] [2153670] Prepare reviewable legal-content PR slices.

