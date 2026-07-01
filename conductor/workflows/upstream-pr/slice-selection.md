# Workflow: Slice Selection

## Input

- Change inventory table.
- Track plan or implementation summary.

## Steps

1. Merge slices that cannot pass validation independently.
2. Split slices that cross ownership boundaries.
3. Order foundational tooling or schema changes before dependent legal content.
4. Keep Conductor bookkeeping out of upstream product PRs unless the upstream repo owns the Conductor artifacts.
5. Assign each slice a branch name:
   - `codex/upstream-<topic>`
   - `codex/upstream-<topic>-docs`
   - `codex/upstream-<topic>-validation`

## Output

Return the final PR sequence:

1. Branch name
2. Included paths
3. Excluded paths
4. Validation commands
5. PR dependency note

## Checks

- Each PR is reviewable in isolation.
- Each PR has a single primary reason to exist.
- The sequence can be stopped after any merged PR without leaving the upstream repository in a misleading state.
