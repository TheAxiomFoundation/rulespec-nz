## Phase 1: Local Manifest Audit

- [x] Read oracle, local corpus, and NLP pipeline metadata.
- [x] Separate verified local facts from live publication claims.

## Phase 2: Live Publication Verification

- [x] Check GitHub heads for `nlp-policy-nz`, `corpus-legislation-nz`, and `nz-legislation`.
- [x] Check Hugging Face datasets/models/spaces tied to the NZ legislation pipeline.
- [x] Check Zenodo records and DOI/version state.

## Phase 3: Source-precedence Decision

- [x] Decide when NLP extracts are preferred over `axiom-corpus extract-nz-legislation`.
- [x] Define fallback through NZ legislation CLI or direct PCO/data.govt.nz bulk XML extraction.

## Phase 4: Inventory Integration

- [x] Update `rulespec-rule-inventory.json` with NLP extract provenance fields.
- [x] Add tests for source-precedence and publication-state claims.
