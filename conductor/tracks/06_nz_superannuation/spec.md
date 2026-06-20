# Track 6: Legislation Ingestion - New Zealand Superannuation Act

## Goal

Record the source-backed ingestion status for the New Zealand Superannuation and Retirement Income Act 2001, tying existing RuleSpec modules to official corpus provisions and the tax-benefit source map.

## Scope

- Reconcile the source-map first batch `nz-superannuation` with existing RuleSpec modules under `nz/statutes/new_zealand_superannuation/`.
- Inventory official corpus provision extracts for age qualification, residence qualification, ordinary rates, hospital/special-rate surfaces, and saved non-qualifying-spouse rates.
- Preserve the boundary between official sources and oracle repositories.
- Explicitly record the path divergence between the source-map destination and the already implemented module split.

## Out of Scope

- Re-downloading or re-extracting PCO bulk legislation.
- Mechanical migration from OpenFisca, PolicyEngine, or nztaxmicrosim.
- Encoding overseas pension deduction interfaces or veteran pension surfaces in this track.
- Moving existing RuleSpec modules without a separate compatibility plan.

## Acceptance Criteria

- A manifest exists under `data/corpus/inventory/nz/` for New Zealand Superannuation.
- The manifest matches the source-map `superannuation` first batch.
- The manifest points to existing RuleSpec modules, companion tests, and corpus provision JSONL files.
- The manifest records the canonical source-map destination and current implemented module paths as a known divergence.
- Targeted and repository tests pass.
