# Source Evidence: Income Interfaces

## Track

- Track id: `23_income_interfaces`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/48
- Policy family: shared income interfaces
- Implementation PR: https://github.com/TheAxiomFoundation/rulespec-nz/pull/50

## Official Source Family

- Act, regulation, order, or official agency table: Income Tax Act 2007; Social Security Act 2018; Accident Compensation Act 2001; official Inland Revenue and MSD guidance.
- Administering agency: Inland Revenue; MSD; ACC.
- Source status: pending foundation gate #31.
- Publication state checked: pending.

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: pending.

## RuleSpec Scope

- Rules: shared income bases, annualisation bridges, period conversion helpers, carry-over interfaces.
- Parameters: period and annualisation constants where shared across downstream tracks.
- Definitions: income-base primitives used by tax, welfare, and ACC tracks.
- Eligibility predicates: none unless they are shared primitives.
- Date-effective surfaces: shared income interfaces by tax year or benefit period.

## Current Implementation Slice

- `nz/statutes/income_tax/core/income_interfaces.yaml`
- `nz/statutes/income_tax/core/income_interfaces.test.yaml`
- `nz/statutes/income_tax/core/taxable_income.yaml`
- `nz/statutes/income_tax/core/taxable_income.test.yaml`

## Companion Tests

- Scenario families: wage, salary, self-employment, annualisation, bridge, and period-conversion cases.
- Expected outputs: annualisation conversions, weekly/fortnightly/monthly bridge conversions, shared taxable-income primitives, employment and business/self-employment bridges, and loss carry-over offsets.
- Edge cases: partial periods, negative adjustments, and date-boundary transitions.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.

## Residual Risk

- Interpretation questions: downstream dependency alignment for Track 24 and later benefit tracks.
- Missing official evidence: source citation paths pending.
- Blockers: foundation gates #30, #31, #32; Track 24 implementation sequence.
