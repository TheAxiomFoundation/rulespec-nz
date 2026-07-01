# Upstream PR Strategy

## Purpose

This workflow turns local RuleSpec NZ work into a small number of upstream pull requests. Each PR should be independently reviewable, legally traceable, and easy to revert without damaging unrelated work.

## PR Slicing Rules

Use the smallest slice that preserves a coherent contract:

1. **Legal content slice:** RuleSpec modules, companion `.test.yaml` files, and source/corpus metadata for one statute, regulation, or tightly coupled policy surface.
2. **Adapter slice:** Code, tests, and manifests for one ingestion, oracle-comparison, or data adapter boundary.
3. **Tooling slice:** Build, lint, typecheck, CI, packaging, or workflow changes that affect many tracks but do not change legal content.
4. **Documentation slice:** User-facing or maintainer-facing docs that explain an already-contained code or data change.
5. **Generated artifact slice:** Only when generated files are intentionally reviewable and reproducible from committed inputs.

Do not mix legal content and broad tooling changes unless one cannot be validated without the other. When they are coupled, put the tooling change first and make the legal-content PR depend on it.

## Required Evidence Per PR

Each PR package must include:

- Change inventory: files, purpose, and ownership boundary.
- Legal provenance: official source references for RuleSpec content.
- Oracle stance: comparison-only surfaces must be labelled non-authoritative.
- Validation transcript: exact local commands and results.
- Upstream target: repository, branch, dependency order, and expected reviewer.
- Residual risk: blocked live gates, missing external credentials, or known incomplete coverage.

## Parallelization Model

Parallelize only across independent questions:

- Inventory agent maps changed files and likely PR slices.
- Provenance/readiness agent checks legal source and validation evidence.
- Packaging agent prepares branch names, PR body, and dependency ordering.

The lead agent reconciles the outputs into the final PR plan. Subagents must not push, open PRs, or rewrite history unless the lead explicitly delegates that action after review.

## Stop Conditions

Stop before submission when:

- The branch contains unrelated user changes.
- Legal content lacks official-source citation paths.
- An oracle fixture is presented as canonical law.
- Tests fail or were not run.
- The upstream target cannot be confirmed.
- The PR depends on another unmerged change that is not stated in the PR body.
