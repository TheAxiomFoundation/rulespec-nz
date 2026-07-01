# Track 11: Upstream PR Workflow System

## Goal

Create a reusable workflow system for turning repository work into a discrete number of upstream pull requests. The system must support small, reviewable change slices, preserve legal provenance boundaries, allow parallel subagent work where the work can be safely separated, and complete routine workflow preparation without human decision points.

## Scope

- Define a strategy for grouping repository changes into upstream PR slices.
- Add composable workflow modules that can be chained into longer upstream-submission workflows.
- Add a machine-readable workflow graph for dependency order, blockers, parallel lanes, and automated completion gates.
- Add subagent role specifications for inventory, provenance/readiness, and PR packaging.
- Add a repo-local skill entrypoint so future agents can invoke the workflow consistently.
- Add validation tests that ensure the workflow artifacts remain present, connected, and automation-ready.

## Non-Goals

- Do not open live upstream PRs in this track.
- Do not infer that oracle code is legal authority.
- Do not bundle unrelated RuleSpec, workflow, and tooling changes into one upstream PR unless the workflow explicitly classifies it as an atomic dependency.
- Do not require human input for routine blocker classification, dependency ordering, or local validation recording.

## Acceptance Criteria

- A Conductor track exists for the workflow work.
- `conductor/workflows/upstream-pr/` contains a strategy plus composable workflow modules.
- `conductor/workflows/upstream-pr/workflow.json` declares the executable graph, dependency order, blockers, parallel lanes, and automated completion gates.
- `.agents/upstream-pr/` contains subagent role specs.
- `.codex/skills/upstream-pr-workflow/SKILL.md` exists as the workflow entrypoint and requires `workflow.json`.
- Tests verify the artifact graph, required sections, and automation contract.
- Track metadata records implementation and review completion with no remaining blockers.
