# Track 17: NLP Pipeline and Publication Audit

## Goal

Determine where the NZ NLP legislation pipeline is up to, whether its Hugging Face, GitHub, and Zenodo artifacts are current, and when it should be preferred over fallback NZ legislation CLI extraction.

## Scope

- Audit `nlp-policy-nz`, `corpus-legislation-nz`, and `nz-legislation` entries in `data/oracles/oracle-index.json`.
- Verify publication surfaces before relying on external dataset claims.
- Map NLP-extracted provisions to the RuleSpec inventory and reconciliation clusters.
- Define source precedence: official PCO/data.govt.nz extract, NLP normalized extract with retained citation path, local Parquet layer, then NZ legislation CLI fallback.

## Acceptance Criteria

- A publication audit manifest records GitHub commit, Hugging Face identifiers, Zenodo DOI/version, and local extract availability.
- Each source is classified as authoritative source, normalized official-source mirror, supporting source tool, or stale/unverified.
- RuleSpec modules using NLP extracts cite stable provision identifiers and fallback extraction route.
- The rule inventory records which modules are backed by NLP/corpus extracts versus CLI fallback.
