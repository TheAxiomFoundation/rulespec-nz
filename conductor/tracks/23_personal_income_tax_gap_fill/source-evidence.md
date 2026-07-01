# Source Evidence: Personal Income Tax Gap-Fill

## Track

- Track id: `23_personal_income_tax_gap_fill`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/36
- Policy family: Personal income tax
- Implementation PR: pending

## Official Source Family

- Act, regulation, order, or official agency table: Income Tax Act 2007; Tax Administration Act 1994; annual tax amendment Acts; official Inland Revenue individual income tax guidance.
- Administering agency: Inland Revenue.
- Source status: pending foundation gate #31.
- Publication state checked: pending.

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: pending.

## RuleSpec Scope

- Rules: historical individual tax rates, low-income rebates, Independent Earner Tax Credit, donation tax credit, RWT/PIE interfaces where needed.
- Parameters: thresholds, rates, credit maxima, abatement thresholds.
- Definitions: taxable income, resident/non-resident income interfaces, qualifying income.
- Eligibility predicates: credit eligibility, residency, income source and thresholds.
- Date-effective surfaces: historical brackets, credit changes, annual amendments.

## Companion Tests

- Scenario families: resident individual, non-resident income, low-income credit, donation credit, threshold crossings.
- Expected outputs: pending.
- Edge cases: annual boundary dates, rounding, overlapping credits.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: pending.

## Residual Risk

- Interpretation questions: interfaces between family income tests and tax definitions.
- Missing official evidence: source citation paths pending.
- Blockers: foundation gates #30, #31, #32; Track 20 income-test assumptions.
