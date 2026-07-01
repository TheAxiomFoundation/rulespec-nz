# Track 40 Specification: Repository quality, CI, and automation hardening

## Objective

Turn the repo-level recommendations into a small support track that improves quality gates, CI signal, and GitHub project hygiene without touching legislation encoding.

## Scope

- Split the fast quality gate from slower or environment-specific checks.
- Add drift detection for generated coverage artifacts.
- Audit GitHub Project field consistency, missing status values, and source/oracle status values.
- Tighten roadmap issue #46 so it points more explicitly at project-ledger conventions.
- Add or refresh lightweight PR and issue templates, plus CODEOWNERS where they help review routing.
- Document how conductor tracks, issues, pull requests, and the GitHub Project relate.

## Out of Scope

- New legislation encoding.
- Large refactors of policy surfaces.
- Moving to a different GitHub project or org setup.
- Broad repo renames or unrelated cleanup.

## Acceptance Criteria

- CI has a clear fast gate and a separate slower lane for environment-specific work.
- Generated coverage artifacts are checked for drift in a reproducible way.
- GitHub Project items have consistent field values and track linkage.
- Roadmap issue #46 explicitly references project-ledger conventions.
- Repo documentation explains the relationship between conductor, issues, PRs, and the project board.
