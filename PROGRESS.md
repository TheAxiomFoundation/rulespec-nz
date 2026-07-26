# Validation drift modules

## State

- Branch: `fix/nz-drift-modules-103`
- Base: local `origin/repin/nz-rulespec-2026-07-25` at `615f3900a2796a8a62b86740062701f29c3e011f`
- Goal: bring the four drifted-waiver modules to full validation passage, remove only waivers for modules that pass, and keep all generated provenance artifacts consistent.
- Network note: `git fetch origin main repin/nz-rulespec-2026-07-25` failed twice because this sandbox could not resolve `github.com`; `gh pr view 103` independently reported the same head SHA (`615f3900a2796a8a62b86740062701f29c3e011f`).
- Current baseline: residence grounding clean; student-loan repayments 4 grounding issues; child support 11 grounding issues; student allowances 25 grounding issues.

## Done

- Confirmed the source checkout is clean and on the requested repin branch.
- Created this dedicated worktree and branch without touching other agents' worktrees.
- Compared the locally tracked refs: the repin branch is three commits ahead of local `origin/main`.
- Read draft PR #91 and its 24 July hold comment. It replaces the same child-support module wholesale and is parked for a full re-encode; this branch will not copy or revive that implementation.
- Confirmed the residence and student-allowance companion tests pass before edits (3 and 8 cases respectively).
- Reproduced the residence CI-parity failure: the only validation error is missing positive companion coverage for `common_unlawfully_resident_or_present_in_new_zealand`; grounding, resolution, compile, and current companion execution are otherwise clean.

## Next

- Add a positive unlawful-presence companion case for residence, refresh artifacts, and validate the waiver deletion.
- Apply the statute-first repayment-period grounding map after the residence checkpoint.
- Finish source mapping for child support and student allowances before changing either module.
