# NZ Treasury IncomeExplorer EMTR reproduction progress

## State

- Audit started 2026-07-26.
- Audit resumed 2026-07-26 from the prior worker's intact groundwork.
- Validation artifact lives outside `rulespec-nz`, under this directory.
- Isolated rulespec worktree: `/Users/maxghenis/TheAxiomFoundation/_axiom-worktrees/rulespec-nz-emtr/rulespec-nz`.
- Rulespec base: local `origin/main` at `89a7d25dc03a4d045348620283332de10b1047da`.
- Disconnect-safe snapshots are committed on the isolated repository's local-only
  `audit/treasury-emtr-reproduction` branch using a separate index; the branch
  records this external artifact without checking it into either RuleSpec
  working tree.
- `git fetch origin` was attempted but could not resolve `github.com` in the sandbox.
- Treasury checkout is pinned at `741a6ca4f5d27b1dc00b43dc395e39ffc4040a4b`.

## Done

- Confirmed the primary `rulespec-nz` checkout is on another branch and left it untouched.
- Created an isolated detached worktree from the locally available `origin/main`.
- Confirmed the engine requires the RuleSpec root basename to be exactly
  `rulespec-nz`; nested the isolated checkout accordingly rather than bypassing
  the guard.
- Added an audit-only composition importing all ten mapped modules; engine
  `d59969b` compiles them together successfully into 174 derived outputs.
- Verified TY27 selects the period starting `2026-04-01` and the matching
  rulespec versions; documented the engine's lack of automatic period
  conversion.
- Recovered and checked the historical snapshot generator. It uses a weekly
  $1 forward difference (with a $1,499-to-$1,500 endpoint carry) and calls raw
  `emtr()`, bypassing the app's `WFF_or_Benefit: Max` wrapper.
- Wired the family-scheme-income output to the WFF and Best Start amount inputs
  inside the external composition without adding policy parameters.
- Ran all ten mapped modules' companion suites against engine `d59969b`: 87
  cases passed.
- Started source-level investigations of Treasury's R method, rulespec module coverage, and the engine evaluation interface.
- Resumed from and reviewed the original brief, existing progress, 563-line
  harness infrastructure, and audit-only composition.

## Next

- Finish scenario-to-engine mappings and the exact weekly $1 forward-difference
  sweep.
- Generate all requested matrices and classify every discrepancy.
- Verify a clean rerun and finish `REPORT.md`.
