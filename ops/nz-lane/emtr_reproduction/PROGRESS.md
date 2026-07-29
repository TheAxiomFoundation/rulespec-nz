# NZ Treasury IncomeExplorer EMTR reproduction progress

## State

- Status: complete as of 2026-07-29. The expanded oracle, comparison artifacts,
  and living report are regenerated, byte-stable, checksummed, and ready for
  handoff. The diverse-family-grid extension began on 2026-07-29.
- The completed 2026-07-26 four-scenario audit is the continuity baseline; its
  pinned Treasury oracle now regenerates byte-for-byte before every expanded
  harness pass.
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
  `d59969b` compiles them together successfully into 176 total derived outputs
  (174 imported outputs plus 2 bridge rules).
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
  endpoints.
- Confirmed that the first residuals have the expected untuned shape: enacted
  benefit/WFF amounts differ from the BEFU25 forecast snapshot, while aligned
  Winter Energy Payment values agree to the snapshot's six-decimal precision.
- Independent source audits caught and corrected two host-encoding defects
  before reporting: (1) Treasury's lone-parent Accommodation Supplement cutout
  combines the lone-parent JSS rate with the JSS 70% abatement schedule, not
  the staged SPS/JSS-with-children income test; and (2) RuleSpec's statutory AS
  primary must use the reg 17 eldest-FTC `/52` input and the exact reg 18 JSS
  cutout, leaving Treasury's `/365*7` and annual-ceiling conventions as labeled
  diagnostics only. No class-(a) residual remains in the final 640 cells.
- Built the complete 4 × 8 × 20 primary matrix with exact signed, absolute, and
  relative deltas. Of 640 cells, 298 are numerically exact, 100 more are inside
  the six-decimal oracle envelope, 174 differences outside that envelope are
  class (b), 68 are class (c), and none remain class (a) or (d).
- Decomposed all 32 EMTR residuals into annual-cent ACC rounding, seven
  complete-dollar WFF interactions, and two sub-envelope JSON display residues.
- Added deterministic CSV, JSON, AS-rounding/decomposition, secondary-rate,
  checksum, and Markdown report generation.
- Wrote the canonical artifacts after two independent fresh compilation and
  evaluation passes (377 engine calls each) produced byte-identical files.
  Validated 640 primary rows, 64 secondary-rate rows, 32 AS diagnostics, JSON
  structure, component recomposition, and every `SHA256SUMS` entry.
- Preserved the original audit's stronger continuity result: 434 of 608
  dollar/control cells agree to the cent and all 174 cent-level exceptions are
  named forecast-vintage differences, with zero unexplained.
- Read the completed `PROGRESS.md` and `REPORT.md`, confirmed the external
  artifact layout, and confirmed local audit branch
  `audit/treasury-emtr-reproduction` points to checkpoint `aa8832f`.
- Passed the honesty-critical oracle gate. The unchanged historical R generator
  recovered from RuleSpec commit `943b27a` was run twice with
  `/usr/local/bin/Rscript` against Treasury commit `741a6ca` and parameter SHA
  `de89898c...`; both fresh raw outputs were byte-identical. The only raw-file
  differences from the pinned snapshot were today's `generated_at` and the
  historical `generator.script` key later migrated to `generator.adapter`.
  Restoring those two metadata values yielded an exact 25,888-byte match and
  canonical SHA-256 `3f4ea311825b316d63910ce37c18e5980ef256df89d1eb5ec8442b4d1351c3c5`.
- Confirmed all required pinned R packages are installed (`data.table`,
  `dplyr`, `jsonlite`, `openxlsx`, `yaml`, and `zoo`).
- Completed the pinned-source branch audit. `R/emtr.R` selects the lone-parent
  JSS rate with the SPS abatement scale when the youngest child is 14+, abates
  TY27 Best Start once over the aggregate eligible-child amount, computes
  partner tax/ACC separately while using joint income for benefits/WFF, and
  supports Area 4 and AS caps. Raw `emtr()` and the UI expose only rent versus
  mortgage; neither has a boarder input.
- Fixed the expanded design at seven new profiles: 14+ lone parent; two
  Best Start-aged children crossing $79,000; a separate dual-full-time couple;
  focused childless IETC; Area 4 high-rent cap; a clearly labeled
  cost-normalised boarder proxy; and four children spanning age bands.
- Kept the common eight display wages and selected extra integer points only
  around source-derived transitions: Best Start at 775/776 plus the
  per-child/aggregate extinction diagnostics at 1125/1126 and 1476/1477;
  joint WFF at 121/122; and IETC benefit-release/abatement/extinction at
  688/689, 1265/1266, and 1342/1343.
- Defined the boarder comparison honestly: RuleSpec receives $400 weekly board
  with its statutory 62% qualifying-cost rule; Treasury is actually run with
  the rent-like $248 qualifying-cost equivalent. This exercises the RuleSpec
  boarder composition but cannot independently validate the 62% rule because
  Treasury has no native boarder branch.
- Added `generate_treasury_emtr_snapshot_expanded.R`. In baseline mode it
  reproduces the canonical 25,888-byte pinned oracle exactly; in expanded mode
  it actually runs pinned raw `emtr()` for all 11 profiles and 104 sampled
  wage points, rounds Treasury numeric outputs to six decimals, preserves the
  original four scenario objects unchanged in value and schema, and emits
  explicit per-scenario provenance.
- Added source-produced Treasury marginal diagnostics for all eight raw
  `emtr()` net-income components to the expanded provenance. The generator,
  rather than the Python comparison, computes every Treasury-side component
  value and forward difference.
- Ran two independent expanded generator passes after adding the diagnostics
  and the exact IETC transition points. They were byte-identical with SHA-256
  `6bed8c0a91e4ba6416238ef1cf381bc8033f3122f3eeb5766074d763929293fd`.
- Extended the Python harness to regenerate and byte-check the baseline before
  it accepts the expanded oracle; verify the R version, generator, Treasury
  checkout, and parameter file; load per-scenario dense wage points; map the
  14+ lone-parent JSS branch; exercise partner tax/ACC and boarder inputs; and
  emit the generated expanded oracle as a checksummed artifact.
- Enforced a clean tracked Treasury checkout before R execution, in addition
  to the existing exact HEAD and parameter-hash checks. The final machine and
  Markdown provenance record clean tracked Treasury, RuleSpec, and engine
  trees.
- Corrected the host aggregation for multiple Best Start children: RuleSpec's
  child-level pre-abatement amounts are summed and the single family-income
  abatement is applied once. The former per-child result is retained as a
  diagnostic so the before/after effect can be reported.
- Extended the report renderer from four scenarios and 32 points to all 11
  scenarios and 104 points. It includes the continuity gate, scenario coverage,
  class evidence, the Best Start before/after diagnostic, component-level EMTR
  decomposition, full per-scenario tables, provenance, reproducibility
  instructions, and explicit remaining coverage gaps.
- Completed the 2,080-cell expanded classification. Of 1,976 amount/control
  cells, 1,454 agree to the cent; the 522 cent-level exceptions are 520 named
  forecast-vintage cells and two documented convention cells. Across all
  primary cells there are zero remaining class-(a) encoding bugs and zero
  unexplained class-(d) cells.
- Classified the 104 EMTR cells from exact component recomposition rather than
  closeness: eight are forecast-vintage effects and 96 are source-backed
  conventions (annual-cent ACC rounding, complete-dollar WFF abatement, Best
  Start family abatement, and IETC whole-dollar income rules). The validator
  aborts on a component remainder over `0.000004` or any unexplained row.
- Preserved the original four-scenario result exactly at 434 of 608
  amount/control cells agreeing to the cent, with all 174 exceptions classified
  as forecast vintage.
- Confirmed the expanded headline is dollar exactness: 1,454 of 1,976
  amount/control cells agree to the cent; every exception is named, with zero
  remaining encoding bugs and zero unexplained.
- Ran the final canonical command in two separate invocations. Each invocation
  independently regenerated the baseline and expanded Treasury oracles and ran
  two fresh RuleSpec compile/evaluate passes (883 engine evaluations per pass).
  All seven generated artifacts and the command's JSON result were
  byte-identical between invocations.
- Ran the documented `python3 ops/nz-lane/emtr_reproduction/run.py` command as
  a further clean invocation; all artifacts and stdout were byte-identical to
  the preserved first final run.
- Validated 2,080 comparison rows, 208 secondary-rate rows, 104 Accommodation
  Supplement diagnostics, 11 scenario records, 104 sampled oracle rows, 104
  Treasury component-diagnostic rows, all dense wage coordinates, zero class
  (a)/(d) rows, and every `SHA256SUMS` entry.
- Final canonical SHA-256 values:
  - `REPORT.md`: `90242a19139f32293892a5fb6ae5e0990f55673670f06eb370ebc90dfd47ff23`
  - `comparison.json`: `b2970a2c11f7e5cd88c1068c237ee5ee0035d923064ee915e112c1d010087f73`
  - `comparison.csv`: `ccaa4dcb61b112587b47afb0e1892f670df354670fcd35f4d801edc621dd4bf2`
  - expanded Treasury snapshot:
    `6bed8c0a91e4ba6416238ef1cf381bc8033f3122f3eeb5766074d763929293fd`
- Confirmed the pinned baseline snapshot remains unmodified at SHA-256
  `3f4ea311825b316d63910ce37c18e5980ef256df89d1eb5ec8442b4d1351c3c5`,
  and the Treasury parameter file remains
  `de89898c78989e057bde7d006b725fed4615ff32731ad008b96148c5a74b683c`.
- Confirmed the isolated RuleSpec worktree, pinned Treasury checkout, and
  pinned engine checkout all have clean tracked trees after the final runs.

## Next

- No work remains for the requested scope. `REPORT.md` lists the residual
  coverage gaps for any future extension, including Treasury's lack of a
  native boarder branch and the omitted entitlement/program families.
