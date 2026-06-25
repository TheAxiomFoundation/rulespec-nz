# Track 16: nztaxmicrosim Follow-on Reconciliation

## Goal

Complete nztaxmicrosim follow-on surfaces by reconciling deferred or simplified oracle surfaces against official New Zealand sources and the checked-in RuleSpec inventory.

## Scope

- Resolve payroll deductions, paid parental leave, PIE/RWT, and child-support surfaces.
- Treat nztaxmicrosim as an oracle and historical parameter discovery tool, not canonical law.
- Use official statutes, regulations, and IRD rate/formula guidance as authority.
- Cross-check overlaps with PolicyEngine NZ and OpenFisca Aotearoa.
- Update duplicate clusters in `data/coverage/rulespec-rule-inventory.json`.

## Acceptance Criteria

- Each deferred surface has a source-backed disposition: encoded, extracted but not encoded, or blocked by missing official source evidence.
- Simplified oracle logic remains excluded until official formula extraction is recorded.
- Duplicate/overlap handling is test-backed in the rule inventory.
- Focused nztaxmicrosim reconciliation and rule inventory tests pass.
