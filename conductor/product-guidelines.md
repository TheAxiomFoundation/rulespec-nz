# Product Guidelines - NZ RuleSpec Encodings

This document outlines the conventions, design principles, and guidelines for encoding New Zealand legislation and policies into RuleSpec.

## Module Structure and Naming
- **Source-Based Directory Mapping**: RuleSpec directories must match the official names of Acts, regulations, or policies in `snake_case` (e.g., `nz/statutes/income_tax/`).
- **Durable IDs**: Every rule and variable must be assigned a unique, durable ID using the format `nz:<path>#<rule>`.
- **Functional Tagging**: When organizing or linking rules across domains, tag them clearly by policy function (e.g., `tax`, `benefit`, `housing`, `education`) to enable functional grouping.

## Testing Guidelines
- **Companion Test Files**: Every RuleSpec YAML module must have a corresponding `.test.yaml` file in the same directory (e.g., `rate.test.yaml` next to `rate.yaml`).
- **Scenario Verification**: Tests must cover standard cases, edge cases, and comparisons against reference models (oracles).

## Legal Provenance
- **Corpus Citation**: Every rule or group of rules must cite its source law provenance. Use `module.source_verification.corpus_citation_path` or `corpus_citation_paths` referencing normalized corpus files in `data/corpus/`.
- **No Mechanical Migration**: Do not mechanically translate other codebases (like OpenFisca or PolicyEngine) into RuleSpec. Encode from the source law first, then compare.
