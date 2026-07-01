# Workflow: Branch and PR Preparation

## Input

- One ready PR slice.
- Upstream target repository and base branch.

## Steps

1. Confirm current branch and dirty state.
2. Create or switch to the slice branch.
3. Stage only files in the approved slice.
4. Commit with a concise conventional message.
5. Prepare the PR body with:
   - purpose;
   - included paths;
   - legal provenance statement;
   - validation transcript;
   - dependency order;
   - residual risk.
6. Push only after the staged diff is reviewed.
7. Open a PR only when the user asks for submission or the current workflow explicitly includes live submission.

## Output

Return:

- branch name;
- commit SHA;
- staged file list;
- PR title;
- PR body draft;
- push/PR status.

## Checks

- Never stage unrelated dirty files.
- Never use destructive git commands to clean user changes.
- Do not open a PR from a branch that includes multiple unapproved slices.
