# Track 13: OpenFisca Aotearoa Rule Incorporation

## Goal

Incorporate every relevant rule, parameter, and situation-test surface from `edithatogo/openfisca-aotearoa` into this RuleSpec NZ library.

OpenFisca Aotearoa is a pinned comparison and structure oracle. It is not canonical law. RuleSpec modules produced by this track must be grounded in official New Zealand legislation, delegated instruments, or agency rate tables.

## Source Pins

- Repository: `https://github.com/edithatogo/openfisca-aotearoa`
- Current repo oracle-index pin: `c36c40bcf553dc95ddca473be12440d4be9d0560`
- Observed upstream HEAD on 2026-06-23: `76062ffc20e40373d9cb56c8910a224236aa1e72`
- Inventory manifest: `data/oracles/openfisca-aotearoa-rule-inventory.json`
- Source map: `data/coverage/openfisca-aotearoa-source-map.json`
- Reconciliation manifest: `data/coverage/openfisca-aotearoa-reconciliation.json`

## Scope

The observed upstream surface includes:

- 101 variable files;
- 84 parameter files;
- 72 YAML situation-test files;
- Act-backed surfaces for ACC, citizenship, housing restructuring, immigration, income tax, Pae Ora, parental leave, rates rebates, social security, superannuation, tax administration, veterans support, civil union, marriage, property relationships, and Oranga Tamariki interpretation;
- regulation-backed surfaces for social security regulation and student allowance;
- demographic predicate surfaces for age, dependants, education, health, housing, income, relationships, residence, and work;
- parameter surfaces for ACC, citizenship, disability allowance, family scheme, health, housing restructuring, income tax, minimum wage, rates rebates, social security, childcare assistance, and superannuation;
- situation-test surfaces for ACC, citizenship, demographics, housing, immigration, income tax, Pae Ora, parental leave, rates rebates, social security, student allowance, and tax administration.

## Boundaries

- Do not mechanically translate OpenFisca formulas into RuleSpec.
- Do not treat OpenFisca parameters, tests, or variables as canonical law.
- Do not overwrite existing RuleSpec modules without reconciling current official-source locators and companion tests.
- Do not silently update `data/oracles/oracle-index.json`; pin upgrades require a focused task because existing adapter tests currently assert the older pin.
- Every canonical RuleSpec rule must live under `nz/statutes/`, `nz/regulations/`, or `nz/policies/` with a companion `.test.yaml`.

## Implementation Summary

- Existing official-source RuleSpec coverage is reconciled for income tax, family scheme, main benefits, accommodation supplement, ACC earners levy, community services card, disability allowance, child disability allowance, winter energy payment, and NZ Super.
- Existing OpenFisca fixtures are approved only as comparison fixtures for current official-source RuleSpec surfaces.
- The oracle-index pin is retained for deterministic fixtures; live upstream HEAD reconciliation is deferred to `openfisca-aotearoa-pin-reconciliation`.
- Missing or partial canonical law surfaces are recorded as named official-source extraction tracks rather than encoded from OpenFisca code.

## Acceptance Criteria

- The inventory manifest records the current repo pin, observed upstream HEAD, and rule-surface counts.
- The implementation plan includes a pin-reconciliation phase before fixture extraction.
- Existing RuleSpec coverage is reconciled against OpenFisca surfaces before adding duplicates.
- Missing surfaces are either implemented from official sources or deferred to named official-source extraction follow-on tracks where source locators are not yet present.
- Full validation passes before review and archive.
