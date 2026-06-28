## Phase 0: Dependency Gate

- [ ] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [ ] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [ ] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [ ] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Source Inventory

- [ ] Identify Social Security Act 2018 and Regulations provisions.
- [ ] Locate official Accommodation Supplement area/rate schedules.
- [ ] Record source manifests or corpus citation paths.

## Phase 2: RuleSpec Encoding

- [ ] Encode applicant and accommodation eligibility predicates.
- [ ] Encode area lookup and rate selection.
- [ ] Encode income and asset tests.
- [ ] Encode accommodation cost, boarder/lodger, and household predicates.

## Phase 3: Tests and Oracle Comparison

- [ ] Add companion `.test.yaml` scenarios across areas, family types, and income levels.
- [ ] Compare to pinned oracle/reference outputs as non-authoritative checks.
- [ ] Record any policy interpretation questions.

## Phase 4: Upstream Packaging

- [ ] Prepare a legal-content PR slice linked to upstream issue `#34`.
- [ ] Include official-source provenance and validation transcript.
