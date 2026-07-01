# Track Specification: OpenFisca Parsing & Transpilation Adapter

## 1. Description and Goal
Create a guarded adapter layer for OpenFisca Aotearoa references. The adapter may parse OpenFisca metadata, parameter files, tests, and variable references for comparison and fixture generation, but it must not mechanically migrate OpenFisca code into RuleSpec or treat OpenFisca as legal authority.

## 2. Guardrails
- Official NZ legislation, regulations, and agency sources remain canonical.
- OpenFisca Aotearoa is an oracle/comparison surface only.
- Every extracted reference must retain the pinned oracle commit from `data/oracles/oracle-index.json`.
- Generated manifests must mark `canonical_law: false`.
- Adapter outputs must point to future RuleSpec destinations without creating standalone YAML fixtures outside allowed roots.

## 3. Initial Scope
- Parse repo-local intake metadata for OpenFisca oracle surfaces.
- Normalize track/file references into a stable manifest for later fixture extraction.
- Validate the manifest shape with unit tests.

## 4. Archive Status

Archived on 2026-06-23 after review confirmed that the guarded adapter preserves pinned OpenFisca commits, marks outputs as `canonical_law: false`, and keeps fixture extraction in-memory/comparison-only.
