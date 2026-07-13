# rulespec-nz

New Zealand RuleSpec encodings and source registry.

This repository is the full-country Aotearoa New Zealand RuleSpec workspace. It is intended to cover the complete tax, transfer, social insurance, student support, family assistance, housing support, and related eligibility surface, with official source provenance and comparison references from existing NZ models.

## Scope

- `nz/{legislation,policies,regulations,statutes}/`: the four atomic RuleSpec
  roots for Acts, delegated instruments, and source-grounded policy modules.
- `nz/programs/`: declarative axiom-compose ProgramSpecs when a composed NZ
  program is added. Programs are not atomic `rulespec/v1` modules.
- `src/rulespec_nz/`: repository tooling such as comparison-oracle intake;
  executable Python never lives under `nz/programs/`.
- `data/corpus/`: source inventory, provision slices, and coverage artifacts promoted from official NZ source ingestion.
- `data/oracles/`: reproducible references to comparison models and datasets used to cross-check Axiom outputs.
- `data/coverage/`: full-country coverage backlog and status.

The detailed tax-benefit intake map is `data/coverage/tax-benefit-source-map.json`. It links each priority track to official source families, pinned comparison files, and first RuleSpec encoding batches. The downstream GitHub Project and issue ledger are documented in `data/coverage/github-project-ledger.md`.

The wider Axiom integration boundary for this NZ workspace is documented in `docs/axiom-ecosystem-integration.md`.

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
4. RuleSpec encoding: source-grounded modules under one of the four atomic
   `nz/` roots; declarative composition under `nz/programs/`.
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

Durable ids are `nz:<path>#<rule>`. Use exact `.yaml` files in direct
jurisdiction roots; repository-root content trees, `.yml` aliases, symlinks,
and Python program implementations are not supported. Keep source law
provenance in corpus artifacts and do not copy full comparison repositories.

Legacy applied manifests have been deleted. The manifest tree stays empty until
the named-release trusted signer regenerates `applied-rulespec/v5` attestations;
no workflow may accept an older schema as current attestation.

## Known gaps (ratcheted)

- `known-validation-gaps.yaml`: pre-existing content debt surfaced by repository-wide validation.
- `known-missing-money-atoms.yaml`: a zero-budget gate for policy-bearing monetary values without direct proof atoms. Release-missing sources are tracked separately in the canonical provenance blocker ledger.

These lists fail CI on new entries AND on listed entries that get fixed without being removed, so they only shrink.
