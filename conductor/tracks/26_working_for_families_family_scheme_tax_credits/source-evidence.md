# Source Evidence: Working for Families and family scheme tax credits

## Track

- Track id: `26_working_for_families_family_scheme_tax_credits`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/33
- Policy family: Working for Families and family scheme tax credits

## Official Source Family

- Act, regulation, order, or official agency table: Income Tax Act 2007 family scheme provisions; Inland Revenue Working for Families guidance.
- Administering agency: Inland Revenue.
- Source status: source inventory recorded for the family-scheme surface.
- Publication state checked: yes.
- Core official references:
  - data/corpus/provisions/nz/statute/2026-06-17-wff-eligibility.jsonl
  - data/corpus/provisions/nz/statute/2026-06-17-wff-tax-credits.jsonl
  - data/corpus/provisions/nz/agency/2026-06-17-ird-working-for-families-rates.jsonl

## Corpus Evidence

- Corpus source manifest: pending.
- Corpus citation path(s): pending.
- Source ingestion command or run id: pending.
- Known extraction gaps: pending.

## RuleSpec Scope

- Rules: family scheme eligibility, principal caregiver tests, tax credits, and abatements.
- Parameters: child counts, income thresholds, weekly conversion surfaces, and rate tables.
- Definitions: family-scheme income, principal caregiver, and dependent-child primitives.
- Eligibility predicates: family-scheme entitlement and credit conditions.
- Date-effective surfaces: tax-credit and abatement changes by effective date.
- Housing assistance remains in its separate module.

## Current Implementation Slice

- `nz/statutes/income_tax/family_scheme/eligibility.yaml`
- `nz/statutes/income_tax/family_scheme/tax_credits.yaml`
- `nz/statutes/income_tax/family_scheme/eligibility.test.yaml`
- `nz/statutes/income_tax/family_scheme/tax_credits.test.yaml`

## Companion Tests

- Scenario families: eligibility, family tax credit, in-work tax credit, parental tax credit, minimum family tax credit, and Best Start cases.
- Expected outputs: entitlement holds / not_holds predicates, weekly or annual credit values, abatement reductions, and net family-scheme amounts.
- Edge cases: threshold crossings, relationship-period changes, child-caregiver changes, and protected family tax credit months.
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
