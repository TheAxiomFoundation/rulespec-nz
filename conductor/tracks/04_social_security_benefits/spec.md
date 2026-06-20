# Track 4 Specification: Social Security Main Benefits

## Goal

Establish the numbered Conductor track for official-source ingestion and verification of Social Security Act 2018 main-benefit entitlement and rate schedules.

## Scope

- Tie the existing `nz/statutes/social_security/main_benefits/entitlement.yaml` and `nz/statutes/social_security/main_benefits/rates.yaml` RuleSpec modules to normalized PCO corpus extracts.
- Cover Jobseeker Support, Sole Parent Support, and Supported Living Payment as the first main-benefits batch.
- Preserve the comparison-oracle boundary: oracle repositories are fixtures and regression references, not legal authority.

## Out of Scope

- Re-downloading the full PCO corpus.
- Mechanically migrating OpenFisca, PolicyEngine, or nztaxmicrosim code.
- Encoding Emergency Benefit, Youth Payment, Young Parent Payment, Orphan's Benefit, or Unsupported Child's Benefit in this first Track 4 task.

## Acceptance

- A machine-readable Social Security main-benefits source manifest exists under `data/corpus/inventory/nz/`.
- Tests prove the manifest agrees with the `social-security-main-benefits` source-map batches, existing RuleSpec module paths, companion tests, and normalized provision JSONL files.
- Existing repository layout checks continue to pass.
