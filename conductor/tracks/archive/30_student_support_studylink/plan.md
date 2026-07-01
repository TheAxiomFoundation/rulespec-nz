## Phase 0: Dependency Gate

- [x] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [x] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [x] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [x] Confirm the existing student-support modules are the correct canonical surface.
- [x] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Coverage Gap Inventory

- [x] Compare current student support outputs against the `student-support` backlog.
- [x] Identify missing eligibility, means-test, allowance-rate, and payment-period surfaces.
- [x] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [x] Locate the Student Allowances Regulations 1998, Education and Training Act 2020, and StudyLink/TEC guidance.
- [x] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [x] Fill student allowance eligibility gaps.
- [x] Add parental-income, partner-income, and independent-circumstances coverage where missing.
- [x] Keep paid parental leave and child support logic separate.

## Phase 4: Tests and Upstream Packaging

- [x] Add companion `.test.yaml` fixtures.
- [x] Draft oracle comparison manifest skeleton for issue #32.
- [x] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [x] Prepare reviewable legal-content PR slices.

## Completion Note

- Track 30 was archived after clean review.
