# rulespec-nz

New Zealand RuleSpec encodings and source registry.

This repository is the full-country Aotearoa New Zealand RuleSpec workspace. It is intended to cover the complete tax, transfer, social insurance, student support, family assistance, housing support, and related eligibility surface, with official source provenance and oracle comparisons from existing NZ models.

## Scope

- `nz/statutes/`: Acts encoded as RuleSpec.
- `nz/regulations/`: regulations, orders, determinations, and delegated instruments.
- `nz/policies/`: agency guidance, rate tables, calculator-facing policies, and executable policy surfaces when statute/regulation decomposition is not yet complete.
- `data/corpus/`: source inventory, provision slices, and coverage artifacts promoted from official NZ source ingestion.
- `data/oracles/`: reproducible references to oracle models and datasets used to cross-check Axiom outputs.
- `data/coverage/`: full-country coverage backlog and status.

## Initial Oracles

The first oracle set is intentionally broad:

- PolicyEngine NZ for current PolicyEngine-style tests and parameters.
- Dylan Mordaunt's `nztaxmicrosim` for historical tax, WFF, benefits, levies, and synthetic-population-oriented logic.
- Dylan Mordaunt's `openfisca-aotearoa` for OpenFisca variables, parameters, tests, and ontology notes.
- Dylan Mordaunt's AU/NZ legislation, NLP, dynamic simulation, value-of-information, and policy-diffusion repositories as supporting source and research infrastructure.

Exact repository SHAs are pinned in `data/oracles/oracle-index.json`.

## Build Strategy

This is not a pilot repo. The target is full NZ coverage. The work should proceed as parallelizable tracks:

1. Official source spine: NZ Legislation, IRD, MSD/Work and Income, ACC, Studylink, Education, Local Government/rates, and Stats NZ definitions.
2. Corpus ingestion: source snapshots, normalized provisions, coverage reports, and inventory manifests for each source family.
3. Oracle extraction: normalized scenarios and expected outputs from PolicyEngine NZ, nztaxmicrosim, and OpenFisca Aotearoa.
4. RuleSpec encoding: source-grounded modules under `nz/statutes`, `nz/regulations`, and `nz/policies`.
5. Parity: compare Axiom outputs against oracle cases, then mark divergences as either Axiom bugs, oracle bugs, or legally meaningful interpretation questions.

The first source-first ingestion lane is the NZ Legislation PCO XML adapter in `axiom-corpus`:

```bash
uv run axiom-corpus extract-nz-legislation \
  --base data/corpus \
  --version <run-id> \
  --source-dir <path-to-pco-xml> \
  --as-of <YYYY-MM-DD> \
  --expression-date <YYYY-MM-DD>
```

Use the official data.govt.nz bulk XML directory for Acts, regulations, Bills, and Supplementary Order Papers. Do not commit the full raw XML tree here; promote the versioned corpus artifacts and cite their `citation_path` values from RuleSpec modules.

## Conventions

Durable ids are `nz:<path>#<rule>`. Keep source law provenance in corpus artifacts and use `module.source_verification.corpus_citation_path` or `corpus_citation_paths` in encoded RuleSpec. Do not copy full external oracle repositories into this repo; pin their SHAs and extract only minimal comparison fixtures when needed.
