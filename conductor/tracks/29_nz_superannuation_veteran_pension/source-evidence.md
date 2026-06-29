# Source Evidence: NZ Superannuation and veteran pension surfaces

## Track

- Track id: `29_nz_superannuation_veteran_pension`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/52
- Policy family: NZ Superannuation and veteran pension

## Official Source Family

- Act, regulation, order, or official agency table: New Zealand Superannuation and Retirement Income Act 2001; Veterans' Support Act 2014; official MSD rate tables.
- Administering agency: MSD.
- Source status: source inventory recorded for the NZ Super surface.
- Publication state checked: yes.
- Core official references:
  - data/corpus/provisions/nz/statute/2026-06-17-new-zealand-superannuation-core.jsonl
  - data/corpus/provisions/nz/statute/2026-06-17-new-zealand-superannuation-special-rates.jsonl

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: pending.

## RuleSpec Scope

- Rules: age qualification, residence qualification, ordinary rates, special rates, and hospital reductions.
- Parameters: age thresholds, residence-year tests, weekly rates, and reduction periods.
- Definitions: entitlement and rate primitives for NZ Superannuation and veteran pension interactions.
- Eligibility predicates: entitlement and exclusion conditions.
- Date-effective surfaces: rate and special-rate changes by effective date.
- Cross-benefit logic remains separate from the income-tax and family-scheme tracks.

## Current Implementation Slice

- `nz/statutes/new_zealand_superannuation/core.yaml`
- `nz/statutes/new_zealand_superannuation/special_rates.yaml`
- companion tests already in the module tree

## Companion Tests

- Scenario families: entitlement, ordinary rate, special rate, hospital rate, and long-term residential care cases.
- Expected outputs: entitlement holds / not_holds predicates, weekly rates, reductions, and net weekly amounts.
- Edge cases: age and residence thresholds, hospital periods, and partner- or veteran-linked rate interactions.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Interpretation questions: how much of the existing surface already covers the target backlog.
- Missing official evidence: source citation paths pending.
- Blockers: foundation gates #30, #31, #32; oracle comparison remains blocked until pinned manifests are published.
