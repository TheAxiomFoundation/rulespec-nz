# Next Roadmap Proposal

This repo has no active conductor tracks left. The next work should be staged
as small, source-grounded families that reuse the existing income-interface and
tax-surface modules rather than re-encoding shared primitives.

## Recommended order

1. Childcare, disability, and health-related assistance.
2. Paid parental leave, child support, and family-related payments.
3. Rates rebates and local-government-adjacent assistance.
4. Residency, citizenship, and immigration predicates.
5. Payroll deductions and savings interfaces.
6. GST and indirect-tax interfaces.

## Rationale

- Childcare, disability, and health-related assistance is the clearest remaining
  MSD family in the current backlog and reuses the existing social-security
  primitives.
- Paid parental leave and child support are separate legal families in the
  backlog and are both explicitly identified as oracle-backed gaps.
- Rates rebates, residency predicates, payroll deductions, and GST each sit in
  separate source families that should stay isolated from one another.

## Dependency notes

- Childcare/disability assistance should reuse [Track 25](./tracks/archive/25_social_security_main_benefits/)
  and [Track 23](./tracks/archive/23_income_interfaces/) as shared inputs.
- Paid parental leave and child support should reuse the income interface work
  and the existing payroll deduction surfaces where applicable.
- Rates rebates should reuse the personal-income-tax gap-fill work for income
  inputs.
- Residency predicates should stay as a shared predicate layer for benefits and
  tax programs.
- Payroll deductions should reuse the shared income interfaces and tax-surface
  plumbing.
- GST should remain isolated as an indirect-tax surface with minimal coupling.

## Suggested next conductor tracks

- Track 31: Childcare, disability, and health-related assistance.
- Track 32: Paid parental leave, child support, and family-related payments.
- Track 33: Rates rebates and local-government-adjacent assistance.
- Track 34: Residency, citizenship, and immigration predicates.
- Track 35: Payroll deductions and savings interfaces.
- Track 36: GST and indirect-tax interfaces.

## Additional small support tracks

Keep these narrow. They are not legislation conversion work; they harden the
research and provenance layer around the existing corpus.

1. Track 38: Corpus citation pinning and provenance QA.
2. Track 37: Oracle comparison and historical rule reconciliation.
3. Track 39: Dynamic simulation and research extensions.

## Additional dependency notes

- Track 38 should land before Track 37 so the comparison harness can rely on
  pinned corpus citations and provenance checks.
- Track 39 should remain last so research work does not block the core
  legislation backlog.
- The NLP pipeline remains useful for source extraction, but these support
  tracks should continue to assume official PCO/data.govt.nz citation paths are
  available even if NLP is still in progress.
