## Phase 0: Baseline Audit

- [x] Confirm the current CI workflow layout and strict-quality settings.
- [x] Audit GitHub Project item fields for missing or inconsistent `Status`, `Source status`, and `Oracle status` values.
- [x] Review roadmap issue #46 for project-ledger wording gaps.
- [x] Inspect current PR and issue templates for missing repo hygiene conventions.
- [x] Task: Conductor - User Manual Verification 'Baseline Audit' (Protocol in workflow.md)

## Phase 1: CI and Quality Gate Hardening

- [x] Add failing tests or checks for generated coverage drift.
- [x] Split fast required checks from slower environment-specific checks.
- [x] Keep warning-free strictness as a CI goal for lint, type, and format gates.
- [x] Ensure the quality gate remains reproducible on the current Windows workspace.
- [x] Task: Conductor - User Manual Verification 'CI and Quality Gate Hardening' (Protocol in workflow.md)

## Phase 2: GitHub Project and Repo Automation

- [x] Normalize GitHub Project field usage for track items and linked issues.
- [x] Add or refresh issue and PR templates so required metadata is captured consistently.
- [x] Add `CODEOWNERS` rules for high-impact config and generated-artifact paths if missing.
- [x] Tighten roadmap issue #46 to reference project-ledger conventions directly.
- [x] Task: Conductor - User Manual Verification 'GitHub Project and Repo Automation' (Protocol in workflow.md)

## Phase 3: Documentation and Traceability

- [x] Document how conductor tracks, issues, pull requests, and the GitHub Project fit together.
- [x] Add a short repository operations note for generated artifacts and drift checks.
- [x] Add a changelog or worklog convention for substantive repo-management changes.
- [x] Verify the resulting documentation is narrow and does not expand into legislation work.
- [x] Task: Conductor - User Manual Verification 'Documentation and Traceability' (Protocol in workflow.md)

## Completion

- [x] Implementation commit: 3bc16f7
