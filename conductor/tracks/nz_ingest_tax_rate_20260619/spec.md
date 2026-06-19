# Track Specification: NZ Legislation Ingestion and Income Tax Rate Encodings

## 1. Description and Goal
Ingest official NZ legislation XML sources using the `axiom-corpus` API adapter and establish the first verified RuleSpec modules for Income Tax Act rate schedules. The goal is to set up the end-to-end flow from PCO API ingestion, normalization to corpus, reference comparisons, and finally verified RuleSpec encoding.

## 2. Technical Stack Context
- **Tooling:** `axiom-corpus` download and extract subcommands.
- **Runtimes:** Python via `pixi`.
- **Output Artifacts:**
  - Ingested PCO XML manifests in `data/corpus/`
  - RuleSpec modules: `nz/statutes/income_tax/rate.yaml`
  - RuleSpec test suites: `nz/statutes/income_tax/rate.test.yaml`

## 3. Requirements and Scope
- **Legislation Ingestion:** Ingest the Income Tax Act 2007 from the Parliamentary Counsel Office (PCO) XML API.
- **RuleSpec Encoding:** Map the primary income tax rate schedules (personal income tax brackets and rates) into declarative RuleSpec format.
- **Verification:** Compare Axiom outputs against reference cases extracted from the comparison oracles (`nztaxmicrosim` or Treasury `EMTR` prototypes).
- **Quality Gates:** 
  - Ensure 100% of defined rate schedule rules are tested via companion `.test.yaml`.
  - Maintain >90% code coverage.
  - No type checks, formatting, or linting errors (`basedpyright` and `ruff --select ALL` must pass cleanly).
