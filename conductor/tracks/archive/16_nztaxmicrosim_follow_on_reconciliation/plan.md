## Phase 1: Deferred Surface Audit

- [x] Recheck nztaxmicrosim surfaces against `nztaxmicrosim-source-map.json`.
- [x] Split each deferred surface into official-source extraction units.

## Phase 2: Official-source Extraction

- [x] Extract KiwiSaver, student loan, and PAYE deduction source tables where not already covered.
- [x] Extract paid parental leave, PIE/RWT, and child-support formulas from official sources.

## Phase 3: Triangulation and Encoding

- [x] Compare nztaxmicrosim values against PolicyEngine NZ and OpenFisca where overlapping.
- [x] Encode only official-source-backed rules.
- [x] Record duplicate clusters and conflict dispositions in `rulespec-rule-inventory.json`.

## Phase 4: Validation

- [x] Run focused tests and update reconciliation manifests.
- [x] Archive only after review confirms no simplified oracle logic was promoted as law.
