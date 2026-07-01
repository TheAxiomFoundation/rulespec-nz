# Source Evidence: Corpus citation pinning and provenance QA

## Track

- Track id: `38_corpus_citation_pinning_and_provenance_qa`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/63
- Policy family: Corpus citation pinning and provenance QA
- Implementation status: archived after clean review.

## Official Source Family

- Act, regulation, order, or official agency table: PCO/data.govt.nz corpus manifests; official corpus citation paths; source inventory records.
- Administering agency: not applicable for a non-legislation track.
- Source status: source inventory pinned for the implemented provenance slice.
- Publication state checked: yes.
- Core official references:
  - `data/corpus/inventory/nz/tax-benefit-pco-locators.json`
  - `data/coverage/corpus-citation-provenance-qa.json`

## Corpus Evidence

- Corpus source manifest: `data/corpus/inventory/nz/tax-benefit-pco-locators.json`
- Corpus citation path(s):
  - `nz/statute/act/public/1985/0141/section/8-DLM82299`
  - `nz/statute/act/public/1985/0141/section/10`
  - `nz/statute/act/public/1985/0141/section/12`
  - `nz/statute/act/public/2018/0004`
  - `nz/regulation/regulation/public/2025/0018/regulation/4`
  - `nz/regulation/regulation/public/2025/0018/regulation/5`
  - `nz/regulation/regulation/public/2025/0018/regulation/6`
  - `nz/regulation/regulation/public/2025/0018/regulation/7`
  - `nz/regulation/regulation/public/2025/0018/regulation/8`
  - `nz/regulation/regulation/public/2025/0018/regulation/9`
  - `nz/statute/act/public/2007/0097/section/MB-1`
  - `nz/statute/act/public/2007/0097/section/MB-2`
  - `nz/statute/act/public/2007/0097/section/MB-3`
  - `nz/statute/act/public/2007/0097/section/MB-4`
  - `nz/statute/act/public/2007/0097/section/MC-2`
  - `nz/statute/act/public/2007/0097/section/MC-3`
  - `nz/statute/act/public/2007/0097/section/MC-4`
  - `nz/statute/act/public/2007/0097/section/MC-5`
  - `nz/statute/act/public/2018/0032/section/16`
  - `nz/statute/act/public/2018/0032/section/18`
  - `nz/statute/act/public/2018/0032/section/19`
  - `nz/statute/act/public/2018/0032/section/20`
- Source ingestion command or run id: `2026-07-01`
- Known extraction gaps: intentionally narrow; this track is for infra/research, not legal content.

## RuleSpec Scope

- Rules: provenance manifest checks and corpus citation pinning.
- Parameters: only the minimum needed to support the narrow track slice.
- Definitions: shared validation or evidence primitives where needed.
- Eligibility predicates: not applicable unless the track reuses a legal surface.
- Date-effective surfaces: not applicable.
- Comparison oracles remain non-authoritative and must be recorded separately from legal source text.

## Current Implementation Slice

- `data/coverage/corpus-citation-provenance-qa.json`
- `tests/test_corpus_citation_provenance_qa.py`

## Companion Tests

- Scenario families: narrow manifest and provenance checks.
- Expected outputs: explicit pass/fail checks for pinned citation paths and module source verification.
- Edge cases: pinned source changes and version changes.
- Historical/date-effective cases: not applicable.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Interpretation questions: whether the provenance manifest should be split further by source family.
- Missing official evidence: none for the implemented provenance slice.
- Blockers: none for the narrow implemented slice; later corpus QA can expand pinned citation coverage.
