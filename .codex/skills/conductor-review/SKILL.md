---
id: conductor-review
name: conductor-review
description: Review Conductor tracks against their plan, repo guidelines, tests, and archive readiness.
triggers: ["$conductor-review", "/conductor:review", "conductor review", "review conductor track"]
version: 0.4.1-rulespec-nz.1
source: "https://github.com/gemini-cli-extensions/conductor"
source_ref: "c9a6a1873ee22fbebfc2e2274ef2e015a8cbdbc0"
---

# conductor-review

Use this skill when the user asks to run `$conductor-review`, `/conductor:review`, review a Conductor track, apply review fixes, or archive reviewed tracks.

This is the repo-local Codex wrapper for the upstream Gemini Conductor review command. The upstream source is vendored at `references/upstream-review.toml`; read it before performing a review when precise upstream behavior matters.

## Required Inputs

- Scope from the user, if provided, such as a track number, track id, track title, or `current`.
- If no scope is provided, inspect `conductor/tracks.md` and select tracks that are active, in progress, recently implemented, or inconsistent with their on-disk archive state.

## Setup Checks

Before reviewing, resolve and verify:

1. `conductor/tracks.md`
2. `conductor/product.md`, if present
3. `conductor/tech-stack.md`, if present
4. `conductor/workflow.md`, if present
5. `conductor/product-guidelines.md`, if present
6. The target track folder, `metadata.json`, `plan.md`, and `spec.md` if the scope is a track

This repo predates strict upstream Conductor setup, so missing optional project context files are warnings unless the target track explicitly depends on them. Missing track files are review blockers.

## Review Protocol

For each target track:

1. Read `metadata.json`, `plan.md`, and `spec.md`.
2. Confirm the track id, status, registry entry, and folder location agree.
3. Check every checked plan item has concrete evidence in code, data, tests, manifests, or recorded blocker text.
4. Confirm official NZ sources remain canonical and oracle repositories are comparison-only.
5. Inspect related test files and manifests for stale narrative fields, missing source paths, and inconsistent status fields.
6. Run the narrowest meaningful validation available in the repo. Prefer existing focused tests. If pytest or project tooling is unavailable, run a deterministic local equivalent and report the tooling blocker.
7. Report findings first, ordered by severity, with file references.
8. Apply fixes when the user has asked to proceed or apply all fixes.
9. Re-run the focused validation or equivalent check after fixes.
10. Archive only after review findings are resolved or explicitly recorded as external blockers.

## Archive Protocol

When a reviewed track is complete:

1. Set `metadata.json` status to `archived_after_clean_review` or the closest existing repo convention.
2. Add `archived_at` and `archive_reason` when the track metadata style supports those fields.
3. Move the track folder to `conductor/tracks/archive/<track_id>/` unless this repo intentionally keeps that track outside archive; if not moving, record the reason.
4. Update `conductor/tracks.md` so archived tracks are under `Archived Tracks` and active tracks contain only actual active work.
5. Remove scratch files created during review.
6. Preserve unrelated dirty files.

## Output

Return:

- review scope
- findings and fixes applied
- validation commands and results
- archive actions taken
- residual blockers, if any

## Guardrails

- Do not treat OpenFisca, PolicyEngine, nztaxmicrosim, or other oracle code as legal authority.
- Prefer official NZ government source evidence and repo-local manifests.
- Do not run broad destructive cleanup.
- Do not commit unless the user explicitly asks for a commit.
- If a command-line Conductor executable is unavailable, this skill is the authoritative repo-local review implementation.
