# Track 3 Specification: Income Tax Act Rate Schedules

## Goal

Establish the numbered Conductor track for official-source ingestion and verification of the Income Tax Act 2007 Schedule 1 individual income tax rate schedule.

## Scope

- Tie the existing `nz/statutes/income_tax/schedule_1/individual_income_tax.yaml` RuleSpec module to the official PCO corpus citation for Income Tax Act 2007 Schedule 1 and the IRD individual income tax rates reference.
- Preserve the comparison-oracle boundary: oracle repositories are fixtures and regression references, not legal authority.
- Keep Track 3 artifacts under `conductor/tracks/03_income_tax_rates/` while preserving the older `nz_ingest_tax_rate_20260619` track as historical context.

## Out of Scope

- Re-downloading the full PCO corpus.
- Mechanically migrating OpenFisca or PolicyEngine code.
- Creating duplicate rate RuleSpec modules while `schedule_1/individual_income_tax.yaml` is the active destination in the source map.

## Acceptance

- A machine-readable income tax rate source manifest exists under `data/corpus/inventory/nz/`.
- Tests prove the manifest agrees with the RuleSpec module's `source_verification` block and the `tax-personal-income` source-map batch.
- Existing repository layout checks continue to pass.
