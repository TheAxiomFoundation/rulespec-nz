# Source Evidence: Rates rebates and local-government-adjacent assistance

## Track

- Track id: $(System.Collections.Hashtable.id)
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/58
- Policy family: Rates rebates and local-government-adjacent assistance

## Official Source Family

- Act, regulation, order, or official agency table: Rates Rebate Act 1973; Rates Rebate Regulations; DIA rates rebate guidance.
- Administering agency: Relevant administering agency.
- Source status: source inventory not yet pinned for this planned track.
- Publication state checked: yes.
- Core official references: pending corpus citation paths.

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: planned track only; official source extraction still needs to be pinned.

## RuleSpec Scope

- Rules: rates rebate maximum allowable; income threshold; initial contribution; additional dependant amount; local authority interaction.
- Parameters: thresholds, rate tables, and entitlement limits where applicable.
- Definitions: legal predicates and income-interface primitives where needed.
- Eligibility predicates: entitlement and exclusion conditions.
- Date-effective surfaces: rate and threshold changes by effective date.
- Comparison oracles remain non-authoritative and must be recorded separately from legal source text.

## Current Implementation Slice

- none yet

## Companion Tests

- Scenario families: boundary, threshold, and date-effective cases.
- Expected outputs: entitlement holds / not_holds predicates, weekly or annual amounts, and reduced or zero-payment outcomes.
- Edge cases: threshold crossings, term transitions, and dependent-status changes.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Interpretation questions: how much of the planned family already exists in the current corpus inventory.
- Missing official evidence: source citation paths pending.
- Blockers: foundation gates #30, #31, #32; oracle comparison remains blocked until pinned manifests are published.

