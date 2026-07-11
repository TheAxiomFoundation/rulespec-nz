# Contributing to rulespec-nz

Thank you for your interest in contributing to the New Zealand RuleSpec source registry!

## Getting Started

1. **Read the context files** — `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` contain important project conventions.
2. **Review the Conductor setup** — The `conductor/` directory contains the project's product guide, tech stack, workflow, and active tracks.
3. **Install dependencies** — Use Pixi to set up the environment:
   ```bash
   pixi install
   ```

## Development Workflow

This project follows the Conductor context-driven development lifecycle:

1. **Spec & Plan** — Work is organized as _tracks_. Each track has a `spec.md` and `plan.md` in `conductor/tracks/`.
2. **TDD** — Write tests first (Red phase), implement to pass (Green phase), then refactor.
3. **Quality gates** — All code must pass linting (`ruff`), type checking (`basedpyright`), tests (`pytest`), and meet >90% coverage before merging.
4. **Scorecard updates** — After adding new modules, regenerate the coverage scorecard:
   ```bash
   python scripts/phase4_scorecard.py
   ```

### Quick commands

| Command | Purpose |
|---------|---------|
| `pixi run test` | Run all tests |
| `pixi run lint` | Run ruff linter |
| `pixi run typecheck` | Run basedpyright |
| `pixi run quality` | Run lint + format-check + typecheck + test |
| `make scorecard` | Regenerate coverage scorecard |

## Code Conventions

- Atomic RuleSpec YAML: `nz/legislation/`, `nz/policies/`, `nz/regulations/`,
  or `nz/statutes/`, with companion `.test.yaml` files.
- Declarative composition: exact `.yaml` ProgramSpecs under `nz/programs/`;
  never Python implementations.
- Every rule must cite source law via `corpus_citation_path`.
- Oracle models (`nztaxmicrosim`, `openfisca-aotearoa`) are comparison fixtures, not legal authority.
- No mechanical migration from OpenFisca or PolicyEngine — encode from source law first.

## Pull Request Process

1. Create a branch from `main` with a descriptive name.
2. Ensure the CI workflow (`repository-checks.yml`) passes.
3. Update `conductor/tracks.md` if your work corresponds to a track.
4. Regenerate the scorecard if modules or rules changed.
5. Submit a PR with a clear description of what changed and why.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
