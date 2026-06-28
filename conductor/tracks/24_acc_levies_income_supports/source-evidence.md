# Source Evidence: ACC Levies and Income Support Surfaces

## Track

- Track id: `24_acc_levies_income_supports`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/37
- Policy family: ACC levies and income supports
- Implementation PR: pending

## Official Source Family

- Act, regulation, order, or official agency table: Accident Compensation Act 2001; ACC levy regulations and rate notices; official ACC/IRD PAYE guidance.
- Administering agency: ACC; Inland Revenue.
- Source status: pending foundation gate #31.
- Publication state checked: pending.

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: pending.

## RuleSpec Scope

- Rules: earners' levy, liable earnings, weekly compensation abatement, loss of potential earnings, minimum weekly earnings.
- Parameters: levy rates, maximum liable earnings, self-employed and low-income levy settings.
- Definitions: liable income, earner status, weekly earnings, compensation interfaces.
- Eligibility predicates: income support entitlement interfaces needed for fiscal modelling.
- Date-effective surfaces: levy years and rate notices.

## Companion Tests

- Scenario families: employee, self-employed, low-income, maximum-liable-earnings, weekly compensation.
- Expected outputs: pending.
- Edge cases: threshold crossings, GST-inclusive/exclusive rates, levy year transitions.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.

## Residual Risk

- Interpretation questions: income interface with Track 23 tax definitions.
- Missing official evidence: source citation paths pending.
- Blockers: foundation gates #30, #31, #32; Track 23 income interfaces.
