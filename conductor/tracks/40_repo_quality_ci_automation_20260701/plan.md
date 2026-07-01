## Phase 0: Baseline Audit

- [ ] Confirm the current CI workflow layout and strict-quality settings.
- [ ] Audit GitHub Project item fields for missing or inconsistent `Status`, `Source status`, and `Oracle status` values.
- [ ] Review roadmap issue #46 for project-ledger wording gaps.
- [ ] Inspect current PR and issue templates for missing repo hygiene conventions.
- [ ] Task: Conductor - User Manual Verification 'Baseline Audit' (Protocol in workflow.md)

## Phase 1: CI and Quality Gate Hardening

- [ ] Add failing tests or checks for generated coverage drift.
- [ ] Split fast required checks from slower environment-specific checks.
- [ ] Keep warning-free strictness as a CI goal for lint, type, and format gates.
- [ ] Ensure the quality gate remains reproducible on the current Windows workspace.
- [ ] Task: Conductor - User Manual Verification 'CI and Quality Gate Hardening' (Protocol in workflow.md)

## Phase 2: GitHub Project and Repo Automation

- [ ] Normalize GitHub Project field usage for track items and linked issues.
- [ ] Add or refresh issue and PR templates so required metadata is captured consistently.
- [ ] Add `CODEOWNERS` rules for high-impact config and generated-artifact paths if missing.
- [ ] Tighten roadmap issue #46 to reference project-ledger conventions directly.
- [ ] Task: Conductor - User Manual Verification 'GitHub Project and Repo Automation' (Protocol in workflow.md)

## Phase 3: Documentation and Traceability

- [ ] Document how conductor tracks, issues, pull requests, and the GitHub Project fit together.
- [ ] Add a short repository operations note for generated artifacts and drift checks.
- [ ] Add a changelog or worklog convention for substantive repo-management changes.
- [ ] Verify the resulting documentation is narrow and does not expand into legislation work.
- [ ] Task: Conductor - User Manual Verification 'Documentation and Traceability' (Protocol in workflow.md)
