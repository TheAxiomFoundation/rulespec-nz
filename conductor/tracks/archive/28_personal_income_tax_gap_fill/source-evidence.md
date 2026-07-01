# Source Evidence: Personal income tax gap-fill surfaces

## Track

- Track id: `28_personal_income_tax_gap_fill`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/36
- Policy family: Personal income tax gap-fill
- Implementation PR: archived after clean review.

## Official Source Family

- Act, regulation, order, or official agency table: Income Tax Act 2007; Tax Administration Act 1994; annual amendment Acts; official Inland Revenue guidance.
- Administering agency: Inland Revenue.
- Source status: source inventory recorded for the personal-income-tax surface.
- Publication state checked: yes.
- Core official references: pending corpus citation paths.

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: pending.

## RuleSpec Scope

- Rules: resident brackets and rates, rebates, credits, withholding, and composition surfaces.
- Parameters: thresholds, rate tables, and credit limits.
- Definitions: taxable income and source-composition primitives where needed.
- Eligibility predicates: tax credit and withholding conditions.
- Date-effective surfaces: bracket and rate changes by effective date.
- Family-scheme and housing-assistance logic remain separate.

## Current Implementation Slice

- `nz/statutes/income_tax/core/income_interfaces.yaml`
- `nz/statutes/income_tax/investment/pie.yaml`
- `nz/statutes/income_tax/withholding/resident_withholding_tax.yaml`

## Companion Tests

- Scenario families: bracket, rebate, credit, withholding, and PIE interface cases.
- Expected outputs: tax amounts, reductions, withholding amounts, and net liabilities.
- Edge cases: threshold crossings, year-to-year changes, and source-composition boundaries.
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
