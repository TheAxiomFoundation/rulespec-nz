# Axiom Ecosystem Integration

This repository is the New Zealand jurisdiction workspace for RuleSpec source
coverage, executable rules, and companion tests. It should stay focused on NZ
legal and policy surfaces while integrating with the wider Axiom Foundation
toolchain through explicit boundaries.

## Repository Role

`rulespec-nz` owns:

- NZ RuleSpec modules under `nz/statutes/`, `nz/regulations/`, and
  `nz/policies/`.
- NZ coverage, source-readiness, and oracle-reference manifests under
  `data/coverage/`, `data/corpus/`, and `data/oracles/`.
- Companion `.test.yaml` fixtures that validate encoded NZ rules.
- NZ-specific implementation notes and review evidence that are necessary to
  reproduce or audit the RuleSpec content.

`rulespec-nz` should not own:

- general-purpose source ingestion code;
- shared RuleSpec compiler/runtime code;
- cross-jurisdiction oracle adapter logic;
- website or application presentation code;
- project-management state that cannot be represented as repo-owned files.

## Integration Map

| Surface | Axiom repository or product | `rulespec-nz` responsibility |
| --- | --- | --- |
| Official NZ source ingestion | `axiom-corpus` | Reference corpus artifacts and citation paths; do not vendor raw official XML dumps. |
| AI-assisted encoding workflow | `axiom-encode` | Keep NZ RuleSpec modules compatible with the current encoder schema and toolchain pins. |
| Rule execution and validation | `axiom-rules-engine` | Provide executable NZ RuleSpec and focused expected-output fixtures. |
| Oracle comparison | `axiom-oracles` | Pin comparison models and record parity findings as non-authoritative checks. |
| Public docs and app surfaces | `axiom-foundation.org` and `app.axiom-foundation.org` | Provide stable NZ artifacts and coverage status that can be surfaced by the docs/app layer. |
| Jurisdiction sibling patterns | `rulespec-us`, `rulespec-uk`, `rulespec-ca` | Match jurisdiction-repo conventions where possible while preserving NZ legal provenance. |

## Source Authority

Official New Zealand sources remain the legal authority. Oracle repositories such
as OpenFisca Aotearoa, nztaxmicrosim, and PolicyEngine-style references are
comparison fixtures only. A RuleSpec module should cite official corpus evidence
before relying on oracle parity.

## PR Boundaries

Upstream pull requests should be reviewable as one of these slices:

- one statute, regulation, or tightly coupled policy surface with companion
  tests and official source provenance;
- one source-ingestion or oracle-comparison boundary;
- one repository-quality or CI change;
- one documentation change that explains committed repo-owned artifacts.

Avoid mixing legal content, broad tooling, generated manifests, and local agent
workflow files unless the coupling is required for validation.

## GitHub Coordination

The downstream fork currently tracks full-country NZ coverage through a GitHub
Project and issue ledger. Because GitHub Projects are account metadata, they are
documented in repository files rather than represented directly in code.

The repository source of truth remains the committed coverage manifests and
RuleSpec modules. GitHub issues and projects are coordination views over those
artifacts, not replacements for them.
