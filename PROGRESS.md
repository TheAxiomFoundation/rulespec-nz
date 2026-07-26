# Guidance block re-point progress

## State

- Branch: `codex/guidance-block-repoints`
- Base: `origin/main` at `9bcfa73e1df027ba074b0dc2b2f60d9f65e315e4`
- Worktree: `_axiom-worktrees/rulespec-nz-blocks/rulespec-nz`
- Phase: module edits and companion coverage

## Done

- Created the required isolated worktree from `origin/main`.
- Created this persistent progress log before module edits.
- Confirmed the pristine baseline suite: 279 passed, 1 skipped, 1 deselected.
- Inventoried the live blocker ledger and all affected proof atoms.
- Mapped the RWT, GST, payroll, StudyLink, and supported ACC atoms to
  text-bearing provisions with exact-substring excerpts.
- Confirmed that Schedule 1 Part B is absent and must remain untouched.
- Confirmed the specific container replacements:
  Income Tax Act 2007 s RD 10 and Accident Compensation Act 2001 Schedule 1
  clause 46.
- Found two live-count differences from the task table: the ACC module has
  eight weekly-compensation-root atoms and five LOPE atoms because the two
  minimum-wage versions have separate atoms.
- Confirmed that the historical ACC value `940` appears nowhere in the NZ
  corpus. Its two 2025 proof atoms cannot be honestly re-pointed.

## Next

- Re-point each supported atom and add missing zero-return companion cases.
- Verify module grounding and companion tests after each coherent module batch.
- Remove only waivers justified by full passage and repin the waiver fingerprint.
- Regenerate inventory, scorecard, provenance ledger, and migration constants after
  the final module edit, then run the prescribed full suite.
- Write the required external report in `ops/nz-lane/`.
