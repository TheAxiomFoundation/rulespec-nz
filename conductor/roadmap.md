# Next Roadmap Proposal

This repo has no active conductor tracks left. The next work should be staged
as small, source-grounded families that reuse the existing income-interface and
tax-surface modules rather than re-encoding shared primitives.

## Recommended order

1. Student support and StudyLink surfaces.
2. Paid parental leave surfaces.
3. Child support surfaces.
4. Residual payroll, filing, and deduction integration gaps.

## Rationale

- Student support is the clearest open legal family in the current backlog and
  already has deferred module scaffolding in the tree.
- Paid parental leave and child support are separate legal families in the
  backlog and are both explicitly identified as oracle-backed gaps.
- Residual payroll and deduction integration should come after those families
  because they rely on the shared income and withholding primitives that are
  already in place.

## Dependency notes

- Student support should reuse [Track 23](./tracks/archive/23_income_interfaces/)
  and [Track 28](./tracks/archive/28_personal_income_tax_gap_fill/) as shared
  income inputs.
- Paid parental leave should reuse the income interface work and the existing
  payroll deduction surfaces where applicable.
- Child support should reuse the same income interfaces and the shared tax
  input plumbing, but keep the formula logic in its own source family.

## Suggested next conductor track

- Track 30: Student support and StudyLink surfaces.
