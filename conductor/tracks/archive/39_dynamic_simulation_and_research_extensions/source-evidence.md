# Source Evidence: Dynamic simulation and research extensions

## Track

- Track id: `39_dynamic_simulation_and_research_extensions`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/64
- Policy family: Dynamic simulation and research extensions
- Implementation status: implemented pending review.

## Official Source Family

- Act, regulation, order, or official agency table: Axiom research stack; Kairos; voiage; lifecourse; innovate.
- Administering agency: not applicable for a non-legislation track.
- Source status: source inventory pinned for the implemented research slice.
- Publication state checked: yes.
- Core official references:
  - `data/oracles/oracle-index.json`
  - `data/analysis/regression-voi-pipeline.json`
  - `data/ledger/state-ledger-temporal-policy.json`
  - `data/coverage/full-country-backlog.json`

## Corpus Evidence

- Corpus source manifest: `data/oracles/oracle-index.json`
- Corpus citation path(s):
  - `data/analysis/regression-voi-pipeline.json`
  - `data/ledger/state-ledger-temporal-policy.json`
  - `data/coverage/full-country-backlog.json`
- Source ingestion command or run id: `2026-07-01`
- Known extraction gaps: intentionally narrow; this track is for infra/research, not legal content.

## RuleSpec Scope

- Rules: research contracts, boundary checks, and provenance checks.
- Parameters: only the minimum needed to support the narrow track slice.
- Definitions: shared validation or evidence primitives where needed.
- Eligibility predicates: not applicable unless the track reuses a legal surface.
- Date-effective surfaces: only where the research contract references temporal policy state.
- Comparison oracles remain non-authoritative and must be recorded separately from legal source text.

## Current Implementation Slice

- `data/analysis/dynamic-research-extensions.json`
- `tests/test_dynamic_research_extensions.py`

## Companion Tests

- Scenario families: narrow manifest, research-oracle, and boundary checks.
- Expected outputs: explicit pass/fail checks for pinned research oracles and non-legal boundaries.
- Edge cases: pinned source changes and version changes.
- Historical/date-effective cases: only where the track needs them.

## Oracle Comparison

- Oracle/reference: kairos; voiage; lifecourse; innovate.
- Pinned SHA or version: `data/oracles/oracle-index.json` records the research pins.
- Comparison role: non-authoritative only.
- Known divergences: pending.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Interpretation questions: whether the research bucket should split into separate simulation and value-of-information tracks.
- Missing official evidence: none for the implemented research slice.
- Blockers: none for the narrow implemented slice; later research can build on the existing contracts without changing legal encodings.
