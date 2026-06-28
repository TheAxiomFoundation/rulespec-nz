## Phase 0: Dependency Gate

- [ ] Confirm upstream issue #30 repo quality and CI scaffold is merged or locally reproducible.
- [ ] Confirm upstream issue #31 source-readiness manifests are available for this source family.
- [ ] Confirm upstream issue #32 oracle manifests are available for non-authoritative comparison.
- [ ] Confirm Track 20 family income-test assumptions do not conflict with income-tax definitions.
- [ ] Incorporate NLP pipeline extracts if available; otherwise proceed from official PCO/data.govt.nz citation paths.

## Phase 1: Gap Inventory

- [ ] Compare current income-tax RuleSpec coverage against `tax-personal-income` backlog components.
- [ ] Identify missing rate, credit, withholding, and historical-parameter surfaces.
- [ ] Create or link the upstream tracking issue.

## Phase 2: Source Inventory

- [ ] Locate official Income Tax Act 2007 and Tax Administration Act 1994 provisions.
- [ ] Locate IRD rate/credit guidance and historical rate tables.
- [ ] Record corpus citation paths or source manifests.

## Phase 3: RuleSpec Encoding

- [ ] Add date-effective historical rate parameters.
- [ ] Encode low-income and Independent Earner Tax Credit surfaces.
- [ ] Encode donation tax credit.
- [ ] Add RWT/PIE interfaces where required for full-country modelling.

## Phase 4: Tests and Upstream Packaging

- [ ] Add companion `.test.yaml` fixtures.
- [ ] Compare against pinned oracle/reference outputs as non-authoritative checks.
- [ ] Prepare reviewable legal-content PR slices.
