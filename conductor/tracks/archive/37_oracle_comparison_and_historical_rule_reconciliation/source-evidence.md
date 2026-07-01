# Source Evidence: Oracle comparison and historical rule reconciliation

## Track

- Track id: `37_oracle_comparison_and_historical_rule_reconciliation`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/62
- Policy family: Oracle comparison and historical rule reconciliation
- Implementation status: archived after clean review.

## Official Source Family

- Act, regulation, order, or official agency table: nztaxmicrosim; OpenFisca Aotearoa; PolicyEngine NZ; pinned comparison manifests.
- Administering agency: not applicable for a non-legislation track.
- Source status: source inventory pinned for the implemented reconciliation slice.
- Publication state checked: yes.
- Core official references:
  - `data/oracles/oracle-index.json`
  - `data/coverage/nztaxmicrosim-reconciliation.json`
  - `data/coverage/openfisca-aotearoa-reconciliation.json`
  - `data/coverage/policyengine-nz-reconciliation.json`

## Corpus Evidence

- Corpus source manifest: `data/oracles/oracle-index.json`
- Corpus citation path(s):
  - `data/coverage/nztaxmicrosim-reconciliation.json`
  - `data/coverage/openfisca-aotearoa-reconciliation.json`
  - `data/coverage/policyengine-nz-reconciliation.json`
- Source ingestion command or run id: `scripts/phase3_reconciliation_workflow.py`
- Known extraction gaps: intentionally narrow; this track is for infra/research, not legal content.

## RuleSpec Scope

- Rules: comparison manifests, provenance checks, and historical-rule reconciliation outputs.
- Parameters: only the minimum needed to support the narrow track slice.
- Definitions: shared validation or evidence primitives where needed.
- Eligibility predicates: not applicable unless the track reuses a legal surface.
- Date-effective surfaces: only when the track explicitly compares historical outputs.
- Comparison oracles remain non-authoritative and must be recorded separately from legal source text.

## Current Implementation Slice

- `scripts/phase3_reconciliation_workflow.py`
- `data/coverage/nztaxmicrosim-reconciliation.json`
- `data/coverage/openfisca-aotearoa-reconciliation.json`
- `data/coverage/policyengine-nz-reconciliation.json`

## Companion Tests

- Scenario families: narrow manifest, provenance, and reconciliation checks.
- Expected outputs: explicit pass/fail or comparison outputs for the track slice.
- Edge cases: pinned source changes and version changes.
- Historical/date-effective cases: only where the track needs them.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa; PolicyEngine NZ where pinned.
- Pinned SHA or version: `data/oracles/oracle-index.json` records the comparison pins.
- Comparison role: non-authoritative only.
- Known divergences: pending follow-on reconciliation.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Interpretation questions: whether the narrow track should be split further.
- Missing official evidence: none for the implemented reconciliation slice.
- Blockers: none for the narrow implemented slice; later corpus QA can harden citation pinning further.
