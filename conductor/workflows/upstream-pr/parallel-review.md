# Workflow: Parallel Review

## Input

- Final PR sequence.
- Changed file list.
- Validation transcript.

## Subagent Lanes

Run these lanes in parallel when the changed slices are independent:

1. **Inventory lane:** checks file grouping and unrelated dirtiness.
2. **Provenance/readiness lane:** checks legal-source claims, oracle boundaries, and validation evidence.
3. **Packaging lane:** checks branch names, PR body, dependency order, and reviewer-facing clarity.

## Reconciliation

The lead agent merges lane outputs into:

- required fixes before PR submission;
- optional improvements;
- final PR sequence;
- final validation status.

## Checks

- A subagent finding must cite a file path, command, or workflow rule.
- Conflicting subagent findings are resolved by the lead agent before any git action.
- Submission actions remain single-threaded.
