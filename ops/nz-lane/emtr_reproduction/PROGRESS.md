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
- Completed the host-level scenario mapping for all four snapshot profiles.
  The mapping evaluates separate person/family/child entities, supplies the
  full family-scheme-income and IWTC eligibility closure, and uses enacted
  RuleSpec outputs as delegated Accommodation Supplement inputs.
- Implemented the period alignment explicitly: 365/7 for tax, ACC, FTC, Best
  Start, IETC, and the snapshot's annual-average Winter Energy Payment; 52 for
  IWTC and MFTC; benefit rates remain weekly.
- Implemented Treasury's raw `emtr()` convention exactly: weekly $1 forward
  differences at every sampled wage and the carried $1,499-to-$1,500 interval
  at the final endpoint.
- Ran an end-to-end probe over all 32 displayed points and all hidden forward
  endpoints. The composition evaluated successfully in 315 engine calls.
- Confirmed that the first residuals have the expected untuned shape: enacted
  benefit/WFF amounts differ from the BEFU25 forecast snapshot, while aligned
  Winter Energy Payment values agree to the snapshot's six-decimal precision.
- An independent source audit caught and corrected one host-encoding defect
  before reporting: Treasury's lone-parent Accommodation Supplement cutout
  combines the lone-parent JSS rate with the JSS 70% abatement schedule, not
  the staged SPS/JSS-with-children income test. The full sweep was rerun after
  the correction; no class-(a) mapping residual remains in the 640 primary
  comparison cells.
- Built the complete 4 × 8 × 20 primary matrix with exact signed, absolute, and
  relative deltas. Of 640 cells, 298 are numerically exact, 100 more are inside
  the six-decimal oracle envelope, 174 material differences are class (b), 68
  are class (c), and none remain class (a) or (d).
- Decomposed all 32 EMTR residuals into annual-cent ACC rounding, seven
  complete-dollar WFF interactions, and two sub-envelope JSON display residues.
- Added deterministic CSV, JSON, AS-rounding, secondary-rate, checksum, and
  Markdown report generation. A temporary end-to-end run completed two fresh
  compile/evaluate passes with byte-identical artifacts; the generated files
  passed row-count, JSON parse, and SHA-256 validation.

## Next

- Complete the final adversarial review, write the canonical artifacts, and
  checkpoint the finished audit.
