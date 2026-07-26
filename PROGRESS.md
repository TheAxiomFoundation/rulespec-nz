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
- Re-pointed all eight GST guidance atoms to exact text in block 7 and block 1.
  GST remains grounding-clean and all six companion cases pass.
- Re-pointed both StudyLink guidance atoms to text-bearing blocks.
  Common residence remains grounding-clean and all four companion cases pass.
- Re-pointed all six RWT guidance atoms and added the negative-income zero case.
  All eight companion cases pass; grounding now reports only the five
  deliberately untouched Schedule 1 Part B atoms.
- Re-pointed both PAYE guidance roots, the student-loan guidance root, both
  subpart RD containers, and the absent KiwiSaver guidance atom to exact
  statutory/guidance text. Payroll is grounding-clean and both companion cases
  pass; its waiver is now eligible for deletion after the final module edit.
- Re-pointed eleven supported ACC/LOPE guidance atoms plus the Accident
  Compensation Act document root, and added three zero/floor companion cases.
  All eight companion cases pass. ACC now has only two local grounding issues:
  the deliberately unrepointed 2025 LOPE atom and the unsupported literal `940`.
- Deleted the now-clean payroll waiver, reducing active waivers from 14 to 13,
  and repinned the waiver-set SHA-256 to
  `0213c6a6f6feadf5a90ce37811b33a95dcea1129e0372aee995209b431c22be7`.
- Dropped and regenerated the five changed inventory entries, then normalized
  the inventory to indent 2 and the scorecard to indent 4, both newline-ended.
- Rebuilt the provenance ledger and updated its pinned migration test:
  50 blocked atoms / 14 paths became 16 blocked atoms / 4 paths, with 1,218 of
  1,234 proof atoms now resolved. The targeted migration tests pass.

## Next

- Run final grounding, companion, and prescribed full-suite verification.
- Write the required external report in `ops/nz-lane/`.
