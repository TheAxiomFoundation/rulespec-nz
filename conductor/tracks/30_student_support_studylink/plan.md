## Phase 0: Dependency Gate

- [ ] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [ ] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [ ] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [ ] Confirm the existing student-support modules are the correct canonical surface.
- [ ] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [ ] Compare current student support outputs against the `student-support` backlog.
- [ ] Identify missing eligibility, means-test, allowance-rate, and payment-period surfaces.
- [ ] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [ ] Locate the Student Allowances Regulations 1998, Education and Training Act 2020, and StudyLink/TEC guidance.
- [ ] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [ ] Fill student allowance eligibility gaps.
- [ ] Add parental-income, partner-income, and independent-circumstances coverage where missing.
- [ ] Keep paid parental leave and child support logic separate.

## Phase 4: Tests and Upstream Packaging

- [ ] Add companion `.test.yaml` fixtures.
- [ ] Draft oracle comparison manifest skeleton for issue #32.
- [ ] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [ ] Prepare reviewable legal-content PR slices.

