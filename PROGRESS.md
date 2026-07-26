# Validation drift modules

## State

- Branch: `fix/nz-drift-modules-103`
- Base: local `origin/repin/nz-rulespec-2026-07-25` at `615f3900a2796a8a62b86740062701f29c3e011f`
- Goal: bring the four drifted-waiver modules to full validation passage, remove only waivers for modules that pass, and keep all generated provenance artifacts consistent.
- Network note: an initial `git fetch origin main repin/nz-rulespec-2026-07-25` failed because this sandbox could not resolve `github.com`.

## Done

- Confirmed the source checkout is clean and on the requested repin branch.
- Created this dedicated worktree and branch without touching other agents' worktrees.
- Compared the locally tracked refs: the repin branch is three commits ahead of local `origin/main`.

## Next

- Inspect PR #91 before changing child-support files.
- Capture current grounding, engine-test, and repository-test failures for all four modules.
- Fix and validate each module independently, regenerating artifacts and committing every coherent step.
