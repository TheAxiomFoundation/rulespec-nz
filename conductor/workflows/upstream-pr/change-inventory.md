# Workflow: Change Inventory

## Input

- Current working tree.
- Optional target base branch or upstream repository.

## Steps

1. Run `git status --short` and identify unrelated dirty files.
2. Run `git diff --name-status` for modified tracked files.
3. Run `git ls-files --others --exclude-standard` for untracked files.
4. Classify each changed path as `legal-content`, `adapter`, `tooling`, `docs`, `conductor`, `generated`, or `unknown`.
5. Identify files that must move together, such as a RuleSpec file and its companion `.test.yaml`.
6. Produce a slice table with proposed PR IDs, file lists, rationale, and dependency order.

## Output

Return a markdown table:

| PR ID | Class | Files | Rationale | Depends On | Risk |
| --- | --- | --- | --- | --- | --- |

## Checks

- Every changed file appears in exactly one proposed slice or is explicitly marked `exclude`.
- No legal-content slice lacks its companion test file.
- No generated artifact is included without a reproducibility note.
