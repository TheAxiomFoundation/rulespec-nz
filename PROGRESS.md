# Validation drift modules

## State

- Branch: `fix/nz-drift-modules-103`
- Base: local `origin/repin/nz-rulespec-2026-07-25` at `615f3900a2796a8a62b86740062701f29c3e011f`
- Goal: bring the four drifted-waiver modules to full validation passage, remove only waivers for modules that pass, and keep all generated provenance artifacts consistent.
- Network note: `git fetch origin main repin/nz-rulespec-2026-07-25` failed twice because this sandbox could not resolve `github.com`; `gh pr view 103` independently reported the same head SHA (`615f3900a2796a8a62b86740062701f29c3e011f`).
- Current baseline: residence grounding clean; student-loan repayments 4 grounding issues; child support 11 grounding issues; student allowances 25 grounding issues.
- Passage count: 3 of 4 (`nz/statutes/common/residence.yaml`, `nz/statutes/student_loan/repayments.yaml`, and `nz/regulations/student_allowances/core.yaml`).
- Final verification: all three repaired modules are grounding-clean; their 4, 9, and 11 engine companion cases pass; child support retains its expected 11 grounding issues while all 11 existing companions pass; the repository suite reports 279 passed, 1 skipped, and 1 deselected.

## Done

- Confirmed the source checkout is clean and on the requested repin branch.
- Created this dedicated worktree and branch without touching other agents' worktrees.
- Compared the locally tracked refs: the repin branch is three commits ahead of local `origin/main`.
- Read draft PR #91 and its 24 July hold comment. It replaces the same child-support module wholesale and is parked for a full re-encode; this branch will not copy or revive that implementation.
- Confirmed the residence and student-allowance companion tests pass before edits (3 and 8 cases respectively).
- Reproduced the residence CI-parity failure: the only validation error is missing positive companion coverage for `common_unlawfully_resident_or_present_in_new_zealand`; grounding, resolution, compile, and current companion execution are otherwise clean.
- Added the missing positive unlawful-presence companion case. The signed-release waiver pipeline now reports `passed: true`; compile, grounding, all 4 companion cases, and 18 focused repository tests pass.
- Deleted only the now-passing residence waiver and repinned the exact waiver-set SHA to `17ba2df4d37ba8ea5c1409e793751207eb2bd2f43dfba8e051b4fe1e5a27d99a`.
- Corrected the student-loan module's governing anchor from s 22 (borrower residence) to s 37 (deduction rate and pay-period thresholds). The 12% rate now quotes s 37 verbatim.
- Replaced generated annual-threshold divisions by 52, 26, and 12 with IRD's operative published weekly, fortnightly, and monthly amounts ($464, $928, and $2,010.66), each quoted verbatim from `student-loan-repayment-deductions/block-3`.
- Student-loan grounding is CLEAN; engine compile and all 9 companion cases pass; both zero-branch and derived-output coverage guards return no issues. The protected full validator cannot run on this host without its signing broker, as expected in the task context.
- Refreshed the student-loan inventory entry and provenance ledger. The ledger moved from 109 to 99 blocked atoms and from 19 to 17 blockers, retiring the module's broad-act and empty-Schedule-1 debt.
- Deleted only the now-clean student-loan waiver and repinned the exact waiver-set SHA to `6158036d6c911b45a30ffeb88e85f001bd30054b6c1be710688f046952891fe3`.
- Corrected the annual-threshold rule's remaining free-text source label from the unrelated Schedule 1 to s 4, matching its proof atom; regenerated artifacts remained byte-identical, grounding stayed CLEAN, all 9 engine cases passed, and 26 focused repository tests passed.
- Completed the child-support source audit without editing the module. Only the `35` care threshold has a current source (s 31); the 18.45% living allowance, flat 18%/26%/33% rates, fixed maximums, and six annual dollar amounts have no honest support in the bound corpus and implement the repealed pre-2015 model.
- Confirmed that current ss 30–36 instead require the income-shares, care-cost, child-expenditure, fixed living-allowance, and nil-case machinery. PR #91 is parked because its attempted replacement also omits critical Schedule 3, rounding, derivation, nil-condition, and eligibility logic.
- Left `nz/statutes/child_support/core_formula.yaml` and its immutable waiver byte-for-byte unchanged. Fixing only `35` would drift the waiver while the other ten failures remain; a full re-encode belongs in the parked child-support work.
- Re-grounded all 25 reported student-allowance issues statute-first: regulations 2, 4, and 43 state the relevant income concepts and parental-assessment scope, while Schedule 2 clauses 1–4 state the weekly rates, income thresholds, parental-income bands, and abatement percentages. StudyLink guidance is retained only for the operative annual parental-income cutoffs.
- Replaced the unsupported annual band breakpoints with the statutory weekly widths ($71.41 and $259.51), promoted the exact parental-income 52-week conversion and long abatement decimals to parameters, and removed the unused tax-rate parameters and unsupported `weekly allowance * 52` annual output.
- A final source audit caught that reg 43 permits a chief-executive-selected averaging period of up to 52 weeks but does not establish unconditional annual personal-income division by 52. The module now accepts student and partner personal income for the week directly; only parental income uses reg 2's explicit division by 52.
- Corrected the recognised-partner age condition, per-parent negative-income floors, and Schedule 2's $1,185.75 combined-income cutoff. The final payment now starts from the selected statutory gross rate and applies parental abatement only to the single, under-24, childless, non-independent surface required by reg 4.
- Companion coverage now proves final payments for couples, students with children, independent students, and students aged 24 or older, plus the high-parental-income and partnered-income zero branches and every derived output.
- Student-allowance grounding is CLEAN; all 11 engine companion cases pass; nonnegative-reduction, zero-branch, derived-output, scalar-table, and interval guards all report no issues; 27 focused repository tests pass.
- Refreshed the inventory and provenance ledger. The ledger has 1,221 atoms (1,163 resolved and 58 blocked) across 40 modules and 17 blockers; the student-allowance module now contributes 45 inventoried rules and no blocked proof atoms.
- Deleted only the now-clean student-allowance waiver and repinned the exact waiver-set SHA to `c8b551976764ea05d8950041aebce28ca884f1a06b590929c573ccb173723909`.
- Wrote the per-module final report to `/Users/maxghenis/TheAxiomFoundation/ops/nz-lane/drift-modules-report.md`.

## Next

- CI remains the final signed-waiver adjudicator. The only unfinished module is child support, whose current-law re-encode must be coordinated with parked PR #91 rather than attempted as a waiver-fingerprint refresh.
