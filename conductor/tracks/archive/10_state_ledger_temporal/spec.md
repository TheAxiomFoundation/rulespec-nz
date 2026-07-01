# Track 10: State Ledger and Temporal Policy Ledger Integrations

## Scope

Track 10 records the repository-side contract for temporal policy state ledger handoffs that reference kairos and TheAxiomFoundation axiom-corpus without vendoring external tools or generated state payloads.

## Contract Goals

- Keep kairos tied to the pinned research-oracle registry entry.
- Keep TheAxiomFoundation axiom-corpus tied to the existing NZ legislation ingestion adapter and minimum ref.
- Define the stable event envelope for temporal policy lifecycle records.
- Link existing ingestion corpus microsimulation and analysis manifests as upstream contract inputs.
- Declare repository boundaries for promoted ledger metadata versus local and raw event payloads.

## Non-Goals

- No live external ledger execution is performed in this track.
- No generated Parquet Arrow or raw ledger payloads are committed.
- No legal authority is inferred from research or implementation repositories.

## Archive Status

Archived on 2026-06-23 after review confirmed the temporal state ledger contract, fixture outputs, registry boundaries, and blocked live-validation record pass focused tests.
