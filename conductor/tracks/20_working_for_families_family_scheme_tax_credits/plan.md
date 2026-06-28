## Phase 0: Dependency Gate

- [ ] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [ ] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [ ] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [ ] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Source Inventory

- [ ] Identify official Income Tax Act 2007 provisions and tax credit rate instruments.
- [ ] Locate official Inland Revenue and MSD guidance/rate tables.
- [ ] Confirm corpus citation paths or source manifests.

## Phase 2: RuleSpec Encoding

- [ ] Encode Family Tax Credit eligibility, amounts, and abatement.
- [ ] Encode In-Work Tax Credit eligibility and amount rules.
- [ ] Encode Minimum Family Tax Credit.
- [ ] Encode Best Start.
- [ ] Encode qualifying child, principal caregiver, and family income predicates.

## Phase 3: Tests and Oracle Comparison

- [ ] Add companion `.test.yaml` fixtures for representative family scenarios.
- [ ] Compare against pinned oracle fixtures as non-authoritative checks.
- [ ] Record divergences as interpretation questions or oracle defects.

## Phase 4: Upstream Packaging

- [ ] Prepare a legal-content PR slice linked to upstream issue `#33`.
- [ ] Include source provenance, validation commands, and residual risk in the PR body.
