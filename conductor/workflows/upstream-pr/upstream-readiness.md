# Workflow: Upstream Readiness

## Input

- Final PR sequence.
- Changed files for one PR slice.

## Steps

1. Verify legal provenance for RuleSpec content:
   - official corpus citation paths exist;
   - source URLs are not used as the only locator;
   - oracle files remain comparison-only.
2. Verify companion tests:
   - every RuleSpec implementation has a `.test.yaml`;
   - derived rules are exercised by expected outputs where applicable.
3. Run local gates:
   - `pixi run lint`
   - `pixi run format-check`
   - `pixi run typecheck`
   - `pixi run test`
   - `pixi run rust-test`
4. Record any unavailable external gate as a blocker with exact reproduction steps.
5. Draft the risk statement for the PR body.

## Output

Return a readiness block:

```markdown
### Validation
- [ ] lint
- [ ] format-check
- [ ] typecheck
- [ ] test
- [ ] rust-test

### Provenance
- Official sources:
- Oracle/comparison surfaces:

### Residual Risk
- Risk:
```

## Checks

- Do not claim remote CI success from local success.
- Do not claim official legal provenance from oracle or secondary-source code.
- Do not mark live validation complete if credentials or adjacent checkouts were unavailable.
