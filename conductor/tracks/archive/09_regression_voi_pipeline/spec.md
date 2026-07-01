# Track 9: Regression and Value of Information Outputs Pipeline

## Goal

Define the repository-side contract for handing RuleSpec simulation outputs to `mars` regression workflows and `voiage` value-of-information analysis without running external analysis tools in this track.

## Scope

- Record expected external analysis tools and their registry status.
- Define inputs from the Track 8 synthetic population builder and RuleSpec simulation outputs.
- Define regression, VOI, and summary report output contracts.
- Preserve local/raw analysis payload boundaries.
- Keep `mars` as an expected local external tool until it is pinned in `oracle-index.json`.

## Out of Scope

- Running live `mars` or `voiage` workflows.
- Committing raw country-scale analysis payloads.
- Creating a full regression model or decision-analysis implementation.
- Claiming `mars` is a pinned oracle before it appears in `data/oracles/oracle-index.json`.

## Acceptance Criteria

- A regression/VOI pipeline manifest exists under `data/analysis/`.
- The manifest covers both `mars` and `voiage` and records their registry status honestly.
- The manifest records input, output, metric, route, and repository-boundary contracts.
- Tests verify the pipeline contract without requiring live external analysis tools.

## Archive Status

Archived on 2026-06-23 after review confirmed the regression/VOI pipeline contract, fixture outputs, oracle registry boundary, and blocked live-validation record pass focused tests.
