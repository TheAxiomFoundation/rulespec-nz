# Track 14: PolicyEngine NZ Rule Incorporation

## Goal

Incorporate every relevant rule, parameter, and policy-test surface from `PolicyEngine/policyengine-nz` into this RuleSpec NZ library using official New Zealand sources as canonical authority.

PolicyEngine NZ is a supporting reference and comparison source. It is not canonical law. RuleSpec modules produced by this track must be grounded in official New Zealand legislation, delegated instruments, or agency rate tables.

## Source Pins

- Repository: `https://github.com/PolicyEngine/policyengine-nz`
- Inventory manifest: `data/oracles/policyengine-nz-rule-inventory.json`

## Boundaries

- Do not mechanically translate PolicyEngine formulas into RuleSpec.
- Do not treat PolicyEngine parameters, tests, or variables as canonical law.
- Do not silently update `data/oracles/oracle-index.json`; pin upgrades require a focused task because existing adapter tests assert pinned references.
- Every canonical RuleSpec rule must live under `nz/statutes/`, `nz/regulations/`, or `nz/policies/` with a companion `.test.yaml`.

## Acceptance Criteria

- The inventory manifest records the current repo pin, observed upstream HEAD, and rule-surface counts.
- The implementation plan includes pin reconciliation before fixture extraction.
- Existing RuleSpec coverage is reconciled against PolicyEngine NZ surfaces before adding duplicates.
- Missing surfaces are implemented from official sources and checked against supporting reference evidence where available.
