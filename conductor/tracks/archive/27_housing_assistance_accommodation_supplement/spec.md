# Track 27 Specification: Housing assistance, especially Accommodation Supplement

## Objective

Encode the Accommodation Supplement and related housing-assistance surfaces in
RuleSpec NZ as a distinct track, keeping the entitlement, asset, base-rate, and
income-abatement logic separate from the main-benefits module.

## Scope

- Accommodation Supplement entitlement and exclusions
- assets requirement and cash-asset thresholds
- base-rate and area tables
- weekly accommodation-cost and income-abatement surfaces
- companion tests for beneficiary and non-beneficiary pathways

## Out of Scope

- Working for Families surfaces
- main-benefits entitlement logic except where it provides inputs
- unrelated housing policy not tied to the Accommodation Supplement surface

## Acceptance Criteria

- The Accommodation Supplement surface is represented in RuleSpec with source-linked tests.
- The track has local source evidence tied to official legislation and MSD guidance.
- Comparison references remain non-authoritative and are recorded separately from legal source text.
- The roadmap reflects the dependency order for the next legislation families.
