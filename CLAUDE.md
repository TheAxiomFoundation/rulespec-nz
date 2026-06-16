# rulespec-nz Agent Notes

This repo stores New Zealand RuleSpec source registry materials, oracle references, and encoded policy rules.

## Do

- Treat the scope as full-country coverage, not a demo slice.
- Prefer official New Zealand government sources for legal provenance.
- Use oracle repositories as comparison engines or fixtures, not as legal authority.
- Keep exact oracle commit SHAs in `data/oracles/oracle-index.json`.
- Start official Acts, regulations, Bills, and SOP ingestion with `axiom-corpus extract-nz-legislation` against the PCO/data.govt.nz bulk XML directory.
- Add RuleSpec under `nz/statutes/`, `nz/regulations/`, or `nz/policies/` with companion `.test.yaml` files.
- Keep large source payloads outside Git unless they are small, necessary official extracts.
- Sync `axiom-encode` and `.axiom/toolchain.toml` before substantial encoding runs, because concurrent encoder work may change the supported schema.

## Do Not

- Migrate OpenFisca or PolicyEngine code mechanically as RuleSpec.
- Treat secondary summaries, commercial tax guides, or oracle model code as canonical law.
- Add generated source payload dumps, formula artifacts, `parameters.yaml`, or standalone YAML fixtures outside allowed RuleSpec roots.
- Hand-copy statute text into RuleSpec without a corpus `citation_path`.
- Edit a dirty `axiom-encode` checkout owned by another agent.
