# Source Evidence: ACC Levies and Income Support Surfaces

## Track

- Track id: `24_acc_levies_income_supports`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/37
- Policy family: ACC levies and income supports
- Implementation PR: pending

## Official Source Family

- Act, regulation, order, or official agency table: Accident Compensation Act 2001; ACC levy regulations and rate notices; official ACC/IRD PAYE guidance.
- Administering agency: ACC; Inland Revenue.
- Source status: official-source slice recorded for levy and weekly-compensation surfaces.
- Publication state checked: yes for levy and weekly-compensation guidance pages.

## Corpus Evidence

- Corpus source manifest: official provisions and guidance recorded in the repo corpus inventory.
- Corpus citation path(s):
  - nz/regulation/regulation/public/2025/0018/regulation/4
  - nz/regulation/regulation/public/2025/0018/regulation/5
  - nz/regulation/regulation/public/2025/0018/regulation/6
  - nz/regulation/regulation/public/2025/0018/regulation/7
  - nz/regulation/regulation/public/2025/0018/regulation/8
  - nz/regulation/regulation/public/2025/0018/regulation/9
  - nz/agency/ird/acc-earners-levy-rates
- Weekly-compensation source citations remain represented through official ACC guidance URLs until a dedicated local corpus slice is extracted.
- Source ingestion command or run id: pending for the weekly-compensation corpus slice.
- Known extraction gaps: detailed weekly-compensation corpus extraction still pending.

## RuleSpec Scope

- Rules: earners' levy, liable earnings, weekly compensation abatement, loss of potential earnings, minimum weekly earnings.
- Parameters: levy rates, maximum liable earnings, self-employed and low-income levy settings.
- Definitions: liable income, earner status, weekly earnings, compensation interfaces.
- Eligibility predicates: income support entitlement interfaces needed for fiscal modelling.
- Date-effective surfaces: levy years and rate notices.

## Companion Tests

- Scenario families: employee, self-employed, low-income, maximum-liable-earnings, weekly compensation.
- Expected outputs: levy rates, levy cap behavior, 80 percent weekly compensation rates, minimum weekly compensation floor, and loss-of-potential-earnings surfaces.
- Edge cases: threshold crossings, GST-inclusive/exclusive rates, levy year transitions.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: pending foundation gate #32.
- Comparison role: non-authoritative only.
- Known divergences: weekly compensation remains a primary-source modeled interface rather than a direct oracle transplant.

## Residual Risk

- Interpretation questions: some weekly-compensation and loss-of-potential-earnings entitlement details are modeled as interface predicates rather than as full claims administration.
- Missing official evidence: a dedicated corpus extract for weekly compensation should still be added later.
- Blockers: foundation gates #30, #31, #32.
