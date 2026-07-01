# Plan: Upstream PR Workflow System

## Phase 1: Strategy and Boundaries

- [x] Task: Define upstream PR slicing strategy.
- [x] Task: Define legal provenance and oracle-boundary guardrails.
- [x] Task: Define when longer workflows compose smaller workflows.

## Phase 2: Workflow Modules

- [x] Task: Create change inventory workflow.
- [x] Task: Create discrete PR slicing workflow.
- [x] Task: Create upstream readiness workflow.
- [x] Task: Create branch and PR preparation workflow.
- [x] Task: Create parallel review workflow.

## Phase 3: Agents and Skill Entry Point

- [x] Task: Create subagent role specs for inventory, provenance/readiness, and PR packaging.
- [x] Task: Create repo-local Codex skill entrypoint.
- [x] Task: Add validation tests for workflow artifacts.

## Phase 4: Automation and Blocker Closeout

- [x] Task: Add `workflow.json` as the machine-readable dependency graph.
- [x] Task: Declare blocker handling, dependency order, and automated completion gates.
- [x] Task: Declare parallel lanes with allowed and forbidden actions.
- [x] Task: Update the skill entrypoint to run from the executable workflow graph.
- [x] Task: Extend tests so the workflow remains granular, dependency-aware, parallelizable, and safe for unattended preparation.
- [x] Task: Confirm no implementation blockers remain in Track 11 metadata.

## Verification

- [x] `python -m pytest tests/test_upstream_pr_workflow_artifacts.py -q -p no:cacheprovider`
- [x] `python -m ruff check tests/test_upstream_pr_workflow_artifacts.py`
- [x] `python -m ruff format --check tests/test_upstream_pr_workflow_artifacts.py`

## Closeout

- [x] Review findings remediated.
- [x] Track archived after review remediation.
