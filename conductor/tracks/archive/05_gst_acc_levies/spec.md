# Track 5 Specification: GST and ACC Levies

## Goal

Establish the numbered Conductor track for official-source ingestion and verification of GST rate/conversion rules and ACC earners' levy schedules.

## Scope

- Tie the existing `nz/statutes/gst/rate.yaml` RuleSpec module to GST Act corpus citations and IRD GST calculation guidance.
- Tie the existing `nz/regulations/acc/earners_levy.yaml` RuleSpec module to the 2025 ACC earners' levy regulations and IRD ACC earners' levy rates.
- Preserve the comparison-oracle boundary: oracle repositories are fixtures and regression references, not legal authority.
- Record incomplete corpus traces explicitly when a cited provision is not present in the current normalized extracts.

## Out of Scope

- Re-downloading the full PCO corpus.
- Mechanically migrating PolicyEngine, OpenFisca, or nztaxmicrosim code.
- Encoding customs and excise interfaces beyond the current GST rate/conversion module.

## Acceptance

- A machine-readable GST and ACC source manifest exists under `data/corpus/inventory/nz/`.
- Tests prove the manifest agrees with the relevant source-map batches, existing RuleSpec module paths, companion tests, normalized provision JSONL files, and known incomplete corpus citations.
- Existing repository layout checks continue to pass.

## Archive Status

Archived on 2026-06-23 after review confirmed the official-source manifest, RuleSpec module provenance, provision traces, resolved GST section 10 trace, and comparison-only GST/ACC fixture tests pass.
