# Track 23: Personal Income Tax Gap-Fill

## Scope

Fill remaining personal income tax RuleSpec coverage beyond the initial Income Tax Act rate schedules.

## In Scope

- Historical resident individual tax brackets and rates.
- Non-resident sourced income treatment where needed for microsimulation.
- Taxable income composition predicates.
- Low-income rebates and Independent Earner Tax Credit.
- Donation tax credit.
- Resident withholding tax and PIE tax interfaces where needed for full-country coverage.

## Out of Scope

- Business income tax surfaces not needed for personal tax-benefit modelling.
- GST and indirect tax surfaces.
- Oracle code as legal authority.

## Acceptance Criteria

- Gap-fill modules cite official Income Tax Act, Tax Administration Act, amendment Act, or IRD source evidence.
- Historical rates are represented with date-effective parameters and tests.
- Companion `.test.yaml` fixtures cover thresholds, credits, and edge cases.
- An upstream issue is created and linked before opening the implementation PR.
