# Source Evidence: Oracle comparison and historical rule reconciliation

## Track

- Track id: $(System.Collections.Hashtable.id)
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/62
- Policy family: Oracle comparison and historical rule reconciliation

## Official Source Family

- Act, regulation, order, or official agency table: nztaxmicrosim; OpenFisca Aotearoa; pinned comparison manifests.
- Administering agency: not applicable for a non-legislation track.
- Source status: track scoped as infrastructure / research rather than direct legal encoding.
- Publication state checked: yes.
- Core official references: pending corpus citation paths where applicable.

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: intentionally narrow; this track is for infra/research, not legal content.

## RuleSpec Scope

- Rules: comparison manifests, provenance checks, or research outputs as applicable.
- Parameters: only the minimum needed to support the narrow track slice.
- Definitions: shared validation or evidence primitives where needed.
- Eligibility predicates: not applicable unless the track reuses a legal surface.
- Date-effective surfaces: only when the track explicitly compares historical outputs.
- Comparison oracles remain non-authoritative and must be recorded separately from legal source text.

## Current Implementation Slice

- none yet

## Companion Tests

- Scenario families: narrow manifest, provenance, or research checks.
- Expected outputs: explicit pass/fail or comparison outputs for the track slice.
- Edge cases: pinned source changes and version changes.
- Historical/date-effective cases: only where the track needs them.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Interpretation questions: whether the narrow track should be split further.
- Missing official evidence: source citation paths pending where applicable.
- Blockers: foundation gates #30, #31, #32; oracle comparison remains blocked until pinned manifests are published.
