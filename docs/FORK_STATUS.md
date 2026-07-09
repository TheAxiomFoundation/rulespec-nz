# rulespec-nz fork status (edithatogo)

**Fork:** https://github.com/edithatogo/rulespec-nz  
**Local source of truth for compile:** branch `fix/kiwisaver-elective-rates-map`  
**Upstream PR:** https://github.com/TheAxiomFoundation/rulespec-nz/pull/80 (open; blocked on signing key)

## Why this fork exists as compile SoT

Upstream `main` still carries KiwiSaver elective rates as `kind: parameter_set` with a YAML **sequence** of rates. The pinned Axiom engine rejects that shape:

```text
yaml parse error: rules[1].versions[0].values: invalid type: sequence, expected a map
```

This fork’s `fix/kiwisaver-elective-rates-map` rewrites elective rates to:

- `kind: parameter`
- `indexed_by: elective_rate_option`
- integer-keyed `values` map (`1`…`5` → 3.5% … 10%)

Verified: `axiom-rules-engine compile` succeeds on `nz/statutes/kiwisaver/contributions.yaml` (artifact format v1, 3 derived outputs).

Also on this branch: `.axiom/repository-structure.yaml` allows root `LICENSE-CODE` and `NOTICE` (required after dual-license #77).

## Upstream PR #80 — needs signing key

PR #80 from this fork has the compile + allowlist fixes, but upstream CI fails on:

```text
axiom-encode guard-generated: Manual RuleSpec changes are not allowed
- nz/statutes/kiwisaver/contributions.yaml changed without a matching
  .axiom/encoding-manifests manifest
```

Producing a valid encoding manifest requires `AXIOM_ENCODE_APPLY_SIGNING_KEY` / `axiom-encode sign-applied-files` (or re-apply via `axiom-encode encode --apply`). Contributors without that org key cannot clear the gate.

**Until a maintainer re-signs the path and merges #80, treat this fork branch as the local source of truth for compiling KiwiSaver contributions** (and for any harness that needs that module).

## Recommended local pin

| Item | Value |
|---|---|
| Repo | `edithatogo/rulespec-nz` |
| Branch | `fix/kiwisaver-elective-rates-map` |
| Engine pin used for verify | `TheAxiomFoundation/axiom-rules-engine` @ `732ad89` |
| Engine binary (local) | `.external-repos/axiom-rules-engine/target/debug/axiom-rules-engine` |

Do **not** force-push `origin/main` of `TheAxiomFoundation/rulespec-nz`. Push only to `edithatogo/rulespec-nz`.
