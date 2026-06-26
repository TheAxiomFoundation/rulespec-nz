## Phase 1: Pin and Source Audit

- [x] Compare `oracle-index.json` OpenFisca pin with observed upstream head. [ba020ac]
- [x] Identify official Acts, regulations, agency tables, and corpus citation paths for each deferred surface. [tbd_commit]

## Phase 2: Official-source Extraction

- [ ] Prefer existing NLP/corpus extracts when they retain official citation paths.
- [ ] Fall back to `axiom-corpus extract-nz-legislation` or NZ legislation CLI when needed.

## Phase 3: RuleSpec and Reconciliation

- [ ] Add or extend RuleSpec modules and companion `.test.yaml` files.
- [ ] Update `rulespec-rule-inventory.json` with source families, oracle links, and duplicate clusters.

## Phase 4: Validation

- [ ] Run focused reconciliation and inventory tests.
- [ ] Archive only after review confirms no OpenFisca code is treated as law.




