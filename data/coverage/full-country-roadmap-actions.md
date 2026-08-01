# Roadmap Action Plan (NZ Full-Country Coverage)

## Recommended execution sequence

1. Enable GitHub Issues on `edithatogo/rulespec-nz` (or use an Issue-enabled host).
2. Authenticate:
   - `gh auth login`, or
   - set `GH_TOKEN` with repo write scope.
3. Validate roadmap integrity before any remote mutations:
   - `python scripts/nz_full_country_roadmap_sync.py --check`
4. Generate a manual review artifact:
   - `python scripts/nz_full_country_roadmap_export.py --format gh > data/coverage/full-country-roadmap-issues.json`
5. Generate idempotent CLI commands (optional):
   - `python scripts/nz_full_country_roadmap_sync.py --emit-commands > /tmp/create_nz_roadmap_issues.sh`
6. Create issues from the payload:
   - `python scripts/nz_full_country_roadmap_sync.py --create-issues`
7. Create a repository Project and add all track issues.
8. Link each track to issue/PR IDs after creation (recommended as a follow-up pass in `track` documentation).

## Why this repo is already NZ-specific

- The roadmap file under `data/coverage/full-country-roadmap.json` is explicitly scoped to:
  - `jurisdiction: nz`
  - `scope: full_country`
- It mirrors `data/coverage/full-country-backlog.json` and maps every backlog track to concrete local coverage evidence.

## Additional improvements recommended

1. Add a lightweight CI check that fails if any file referenced in backlog tracks is added to backlog but absent from roadmap evidence.
2. Keep `full-country-roadmap.json` as the single source of truth and generate Markdown from it during release/checkpoint commits to avoid drift.
3. Add a second status tier (`blocked`, `in_review`) when a track remains partial but blocked on official-source parsing.
4. Add a per-track PR reference field once remote issues/PRs are created, for direct traceability:
   - `github_reference: { issue_url, pr_url, last_commit }`
5. Create a dedicated "Implementation History" view in the rules and a link in each track plan folder to its PR/issue IDs.
6. Add the new check as a CI target so roadmap and content evidence cannot drift silently.
