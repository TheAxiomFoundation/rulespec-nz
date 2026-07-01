## Phase 1: Pin and Source Audit

- [x] Compare `oracle-index.json` OpenFisca pin with observed upstream head. [ba020ac]
- [x] Identify official Acts, regulations, agency tables, and corpus citation paths for each deferred surface. [f972932]

## Phase 2: Official-source Extraction

- [x] Prefer existing NLP/corpus extracts when they retain official citation paths. [tbd_commit]
- [x] Fall back to `axiom-corpus extract-nz-legislation` or NZ legislation CLI when needed. [tbd_commit]

## Phase 3: RuleSpec and Reconciliation

- [x] Add or extend RuleSpec modules and companion `.test.yaml` files.
- [x] Update `rulespec-rule-inventory.json` with source families, oracle links, and duplicate clusters.

## Phase 4: Validation

- [x] Run focused reconciliation and inventory tests.
- [x] Archive only after review confirms no OpenFisca code is treated as law.



