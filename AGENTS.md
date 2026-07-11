# rulespec-nz Agent Notes

> ⚠️ **Single source of truth for agent instructions.**
> `CLAUDE.md` and `GEMINI.md` both reference this file. Edit here, not in copies.

This repo stores New Zealand RuleSpec source registry materials, oracle references, and encoded policy rules.

## Do

- Treat the scope as full-country coverage, not a demo slice.
- Prefer official New Zealand government sources for legal provenance.
- Use oracle repositories as comparison engines or fixtures, not as legal authority.
- Keep exact oracle commit SHAs in `data/oracles/oracle-index.json`.
- Start official Acts, regulations, Bills, and SOP ingestion with `axiom-corpus extract-nz-legislation` against the PCO/data.govt.nz bulk XML directory.
- Add atomic RuleSpec under `nz/legislation/`, `nz/policies/`,
  `nz/regulations/`, or `nz/statutes/` with companion `.test.yaml` files.
- Add only declarative `.yaml` ProgramSpecs under `nz/programs/`; keep Python
  tooling under `src/rulespec_nz/`.
- Keep large source payloads outside Git unless they are small, necessary official extracts.
- Sync `axiom-encode` and `.axiom/toolchain.toml` before substantial encoding runs, because concurrent encoder work may change the supported schema.

## Do Not

- Migrate OpenFisca or PolicyEngine code mechanically as RuleSpec.
- Treat secondary summaries, commercial tax guides, or oracle model code as canonical law.
- Add repository-root content trees, `.yml` aliases, symlinks, Python program
  implementations, generated formula artifacts, or standalone YAML fixtures.
- Hand-copy statute text into RuleSpec without a corpus `citation_path`.
- Edit a dirty `axiom-encode` checkout owned by another agent.
