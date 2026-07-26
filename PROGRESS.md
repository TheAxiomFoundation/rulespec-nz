# Validation drift modules

## State

- Branch: `fix/nz-drift-modules-103`
- Base: local `origin/repin/nz-rulespec-2026-07-25` at `615f3900a2796a8a62b86740062701f29c3e011f`
- Goal: bring the four drifted-waiver modules to full validation passage, remove only waivers for modules that pass, and keep all generated provenance artifacts consistent.
- Network note: `git fetch origin main repin/nz-rulespec-2026-07-25` failed twice because this sandbox could not resolve `github.com`; `gh pr view 103` independently reported the same head SHA (`615f3900a2796a8a62b86740062701f29c3e011f`).
- Current baseline: residence grounding clean; student-loan repayments 4 grounding issues; child support 11 grounding issues; student allowances 25 grounding issues.
- Passage count: 2 of 4 (`nz/statutes/common/residence.yaml` and `nz/statutes/student_loan/repayments.yaml`).

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

## Next

- Apply the statute-first/guidance-rate grounding map for student allowances, then regenerate artifacts and remove its waiver only if all local passage checks are clean.
