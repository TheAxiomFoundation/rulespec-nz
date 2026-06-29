# Track 25 Oracle Comparison Draft

## Purpose

This draft records the intended non-authoritative comparison surfaces for
Track 25 main-benefit work. It is not a legal source and does not replace the
pinned oracle manifests required by upstream issue #32.

## Intended Oracle Targets

- `nztaxmicrosim` at `9a9de211b40086a7a85a938ae26db4a533b27e99`
- `openfisca-aotearoa` at `c36c40bcf553dc95ddca473be12440d4be9d0560`

## Comparison Scope

- Jobseeker Support entitlement and rate branches
- Sole Parent Support entitlement and rate branches
- Supported Living Payment entitlement and rate branches
- Benefit income-test reductions
- Accommodation Supplement remains out of scope for this track

## Draft Comparison Cases

- `jobseeker_entitlement_standard_unemployed_adult`
- `jobseeker_full_time_student_without_discretionary_eligibility_is_ineligible`
- `jobseeker_single_standard_no_children_uses_income_test_3`
- `jobseeker_single_under_25_without_children_uses_income_test_3`
- `sole_parent_entitlement_single_parent`
- `supported_living_restricted_work_capacity_entitlement`
- `supported_living_caring_entitlement_and_temporary_continuation`
- `supported_living_single_under_18_without_children_uses_income_test_1`
- `supported_living_partnered_with_super_or_veterans_without_children_uses_income_test_2`

## Draft Outcome Fields

- entitlement holds / not_holds predicates
- gross weekly rates
- weekly income-test reductions
- net weekly payments
- blind subsidy amounts

## Status

Blocked until upstream issue #32 publishes pinned comparison manifests or a
repository-local equivalent is added.
