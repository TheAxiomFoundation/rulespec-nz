## Phase 0: Dependency Gate

- [ ] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [ ] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [ ] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [ ] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Source Inventory

- [ ] Identify official Social Security Act 2018 provisions for each main benefit.
- [ ] Identify Social Security Regulations 2018 provisions for tests and rates.
- [ ] Locate official MSD/Work and Income rate tables and source manifests.

## Phase 2: RuleSpec Encoding

- [ ] Encode shared residence, relationship, dependent-child, income, and asset predicates.
- [ ] Encode Jobseeker Support.
- [ ] Encode Sole Parent Support.
- [ ] Encode Supported Living Payment.
- [ ] Encode Emergency Benefit.
- [ ] Encode Youth Payment and Young Parent Payment.

## Phase 3: Tests and Oracle Comparison

- [ ] Add companion tests for representative household and income scenarios.
- [ ] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [ ] Record divergences and unresolved interpretation questions.

## Phase 4: Upstream Packaging

- [ ] Prepare one or more legal-content PR slices linked to upstream issue `#35`.
- [ ] Split further if the benefit family is too large for one reviewable PR.
