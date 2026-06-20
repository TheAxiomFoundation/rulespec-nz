# Track 7: Ingestion Adapter for Local Parquet Layers

## Goal

Define the repository-side adapter contract for local Parquet data layers produced by `corpus-legislation-nz` and `corpus-nz-hansard` without committing raw Parquet payloads.

## Scope

- Record the expected local sources, path environment variables, and Parquet table contracts.
- Preserve New Zealand Legislation as the official legal authority for RuleSpec provenance.
- Treat Hansard as parliamentary context, not direct legal authority for executable rules.
- Define normalized JSON/JSONL outputs that can be deliberately promoted into `data/corpus/`.
- Keep large local Parquet datasets outside Git.

## Out of Scope

- Downloading, copying, or committing local Parquet files.
- Running a live `corpus-legislation-nz` or `corpus-nz-hansard` export.
- Replacing the existing `axiom-corpus` PCO XML extraction lane.
- Using Hansard as canonical law for RuleSpec modules.

## Acceptance Criteria

- A local Parquet adapter manifest exists under `data/corpus/ingestion/`.
- The manifest covers both `corpus-legislation-nz` and `corpus-nz-hansard`.
- The manifest records required columns, join keys, normalized output paths, and repository boundaries.
- Tests verify the adapter contract and source-authority boundary.
