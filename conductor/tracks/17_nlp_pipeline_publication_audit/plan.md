## Phase 1: Local Manifest Audit

- [ ] Read oracle, local corpus, and NLP pipeline metadata.
- [ ] Separate verified local facts from live publication claims.

## Phase 2: Live Publication Verification

- [ ] Check GitHub heads for `nlp-policy-nz`, `corpus-legislation-nz`, and `nz-legislation`.
- [ ] Check Hugging Face datasets/models/spaces tied to the NZ legislation pipeline.
- [ ] Check Zenodo records and DOI/version state.

## Phase 3: Source-precedence Decision

- [ ] Decide when NLP extracts are preferred over `axiom-corpus extract-nz-legislation`.
- [ ] Define fallback through NZ legislation CLI or direct PCO/data.govt.nz bulk XML extraction.

## Phase 4: Inventory Integration

- [ ] Update `rulespec-rule-inventory.json` with NLP extract provenance fields.
- [ ] Add tests for source-precedence and publication-state claims.
