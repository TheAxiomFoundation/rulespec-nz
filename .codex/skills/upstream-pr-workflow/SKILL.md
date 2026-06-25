---
id: upstream-pr-workflow
name: upstream-pr-workflow
description: Package local RuleSpec NZ changes into discrete upstream pull requests.
triggers: ["$upstream-pr-workflow", "/upstream-pr-workflow", "prepare upstream PRs", "package upstream PRs"]
version: 0.2.0
---

# upstream-pr-workflow

Use this skill when asked to prepare, review, or submit upstream PRs from local RuleSpec NZ changes.

## Required Workflow

1. Read `conductor/workflows/upstream-pr/workflow.json` as the executable dependency graph.
2. Read `conductor/workflows/upstream-pr/strategy.md` for slicing rules and legal/oracle boundaries.
3. Run `conductor/workflows/upstream-pr/change-inventory.md`.
4. Run `conductor/workflows/upstream-pr/slice-selection.md`.
5. For each selected PR slice, run `conductor/workflows/upstream-pr/upstream-readiness.md`.
6. If independent slices or review questions exist, use the role specs in `.agents/upstream-pr/` to parallelize inventory, provenance/readiness, and packaging review according to the `parallel_lanes` in `workflow.json`.
7. Run `conductor/workflows/upstream-pr/branch-pr-prep.md` only after readiness and parallel-review blockers are resolved.
8. Do not push or open a PR unless the user explicitly asks for live submission.

## Required Output

Return:

- proposed PR sequence;
- included and excluded paths for each PR;
- dependency order and blockers for each PR;
- validation commands and results;
- provenance and oracle-boundary notes;
- residual risks;
- next action required from the user, if any.

## Guardrails

- Preserve unrelated working-tree changes.
- Keep legal content, adapter code, tooling, docs, and generated artifacts in separate slices unless validation requires coupling.
- Use official NZ government sources for legal provenance.
- Treat oracle repositories as comparison fixtures only.
- Do not claim remote CI or upstream acceptance without live evidence.
- Default to automated completion: record blockers with reproduction steps and continue with independent slices unless live submission or external credentials are explicitly required.
