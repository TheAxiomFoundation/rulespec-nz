# Track 12: nztaxmicrosim Rule Incorporation

## Goal

Incorporate every relevant rule surface from `edithatogo/nztaxmicrosim` into this RuleSpec NZ library's planning, coverage, and comparison-oracle surfaces without treating oracle code as canonical law.

The source library is a pinned comparison oracle, not canonical law. RuleSpec modules produced from this work must be grounded in official New Zealand legislation, delegated instruments, or agency rate tables, with `nztaxmicrosim` used for rule discovery, fixture extraction, historical-parameter comparison, and regression parity checks.

## Source Pin

- Repository: `https://github.com/edithatogo/nztaxmicrosim`
- Pinned commit: `9a9de211b40086a7a85a938ae26db4a533b27e99`
- Existing oracle index entry: `data/oracles/oracle-index.json`
- Inventory manifest: `data/oracles/nztaxmicrosim-rule-inventory.json`
- Source-authority map: `data/coverage/nztaxmicrosim-source-map.json`
- Reconciliation closeout: `data/coverage/nztaxmicrosim-reconciliation.json`

## Scope

Rule surfaces identified from the pinned library:

- personal income tax and historical bracket/rate parameters;
- Independent Earner Tax Credit;
- donation tax credit;
- FamilyBoost childcare tax credit;
- Working for Families: FTC, IWTC, MFTC, BSTC, abatement, and shared-care/calibration surfaces;
- ACC earners levy;
- Jobseeker Support, Sole Parent Support, Supported Living Payment;
- Accommodation Supplement;
- Winter Energy Payment;
- Disability Allowance;
- NZ Super interaction flags;
- KiwiSaver employee contributions;
- student loan repayments;
- Portfolio Investment Entity tax;
- Resident Withholding Tax;
- paid parental leave;
- child support;
- historical tax-search and parameter coverage fixtures.

## Boundaries

- Do not copy `nztaxmicrosim` Python functions mechanically into RuleSpec.
- Do not treat placeholder or simplified oracle logic as law. The pinned source has explicit placeholder/simplification surfaces, including WFF placeholder rules, child support simplification, PIE simplification, and EMTR simplification.
- Do not commit the cloned upstream repository or large generated report/data payloads.
- Every canonical RuleSpec implementation must live under `nz/statutes/`, `nz/regulations/`, or `nz/policies/` with a companion `.test.yaml`.
- Every canonical RuleSpec rule must cite official source locators. Oracle fixture links belong in manifests or tests as comparison evidence.
- Missing canonical surfaces discovered from `nztaxmicrosim` must be recorded as follow-on official-source extraction work unless official-source locators and companion tests already exist in this track.

## Acceptance Criteria

- The inventory manifest covers all rule-bearing `nztaxmicrosim` modules inspected at the pinned commit.
- `data/coverage/nztaxmicrosim-source-map.json` maps every inventory surface to official source requirements, current RuleSpec coverage, planned destinations, oracle-use boundaries, and blockers.
- Existing overlapping RuleSpec modules are reconciled before adding duplicates.
- Missing canonical surfaces are either implemented with companion tests and official-source locators, or explicitly deferred to named follow-on official-source extraction tracks when the oracle is simplified or official locators are not yet available.
- Oracle comparison fixtures are extracted only into approved fixture/manifests and remain labelled non-authoritative.
- `data/coverage/nztaxmicrosim-reconciliation.json` records the final closeout status for every inventory surface and the exact follow-on extraction units.
- The full quality suite passes: Ruff, format, basedpyright, pytest, and Rust tests.
