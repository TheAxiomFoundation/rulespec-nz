# rulespec-nz

New Zealand RuleSpec encodings and source registry.

This repository is the full-country Aotearoa New Zealand RuleSpec workspace. It is intended to cover the complete tax, transfer, social insurance, student support, family assistance, housing support, and related eligibility surface, with official source provenance and comparison references from existing NZ models.

## Scope

- `nz/statutes/`: Acts encoded as RuleSpec.
- `nz/regulations/`: regulations, orders, determinations, and delegated instruments.
- `nz/policies/`: agency guidance, rate tables, calculator-facing policies, and executable policy surfaces when statute/regulation decomposition is not yet complete.
- `data/corpus/`: source inventory, provision slices, and coverage artifacts promoted from official NZ source ingestion.
- `data/oracles/`: reproducible references to comparison models and datasets used to cross-check Axiom outputs.
- `data/coverage/`: full-country coverage backlog and status.

The detailed tax-benefit intake map is `data/coverage/tax-benefit-source-map.json`. It links each priority track to official source families, pinned comparison files, and first RuleSpec encoding batches. The downstream GitHub Project and issue ledger are documented in `data/coverage/github-project-ledger.md`.

## Initial References

The first reference set is intentionally broad:

- PolicyEngine NZ only as a minimal PolicyEngine-style smoke/reference surface, not as an authoritative oracle.
- NZ Treasury IncomeExplorer as the executable stylized-family disposable-income and EMTR oracle; the public Python `emtr` prototype and AN25-01 repo are supporting references.
- Dylan Mordaunt's `nztaxmicrosim` for historical tax, WFF, benefits, levies, and synthetic-population-oriented logic.
- Dylan Mordaunt's `openfisca-aotearoa` for OpenFisca variables, parameters, tests, and ontology notes.
- Dylan Mordaunt's AU/NZ legislation, NLP, dynamic simulation, value-of-information, and policy-diffusion repositories as supporting source and research infrastructure.

Exact repository SHAs are pinned in `data/oracles/oracle-index.json`.

## Build Strategy

This is not a pilot repo. The target is full NZ coverage. The work should proceed as parallelizable tracks:

1. Official source spine: NZ Legislation, IRD, MSD/Work and Income, ACC, Studylink, Education, Local Government/rates, and Stats NZ definitions.
2. Corpus ingestion: source snapshots, normalized provisions, coverage reports, and inventory manifests for each source family.
3. Reference extraction: normalized scenarios and expected outputs from nztaxmicrosim, OpenFisca Aotearoa, and minimal smoke references from PolicyEngine NZ.
4. RuleSpec encoding: source-grounded modules under `nz/statutes`, `nz/regulations`, and `nz/policies`.
5. Parity: compare Axiom outputs against reference cases, then mark divergences as either Axiom bugs, reference bugs, or legally meaningful interpretation questions.

The first source-first ingestion lane is the NZ Legislation PCO XML adapter in `axiom-corpus`. With an official API key available in `NZ_LEGISLATION_API_KEY`, acquire XML sources first:

```bash
uv run axiom-corpus download-nz-legislation-api \
  --output-dir <path-to-pco-xml> \
  --manifest-path data/corpus/inventory/nz/api-downloads/<run-id>.json
```

Then normalize the local XML directory:

```bash
uv run axiom-corpus extract-nz-legislation \
  --base data/corpus \
  --version <run-id> \
  --source-dir <path-to-pco-xml> \
  --as-of <YYYY-MM-DD> \
  --expression-date <YYYY-MM-DD>
```

Use the official API or data.govt.nz bulk XML directory for Acts, regulations, Bills, and Supplementary Order Papers. Do not commit the full raw XML tree here; promote the versioned corpus artifacts and cite their `citation_path` values from RuleSpec modules.

## Conventions

Durable ids are `nz:<path>#<rule>`. Keep source law provenance in corpus artifacts and use `module.source_verification.corpus_citation_path` or `corpus_citation_paths` in encoded RuleSpec. Do not copy full external comparison repositories into this repo; pin their SHAs and extract only minimal comparison fixtures when needed.
