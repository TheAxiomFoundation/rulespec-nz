## Track 24: ACC Levies and Income Support Surfaces

### Scope

This track adds the first ACC-specific RuleSpec surfaces for New Zealand:

- ACC earners' levy inputs and levy-linked income constraints.
- Weekly compensation replacement-rate and floor/cap surfaces.
- The shared income-interface predicates needed by downstream levy and compensation logic.

### Acceptance Criteria

- The ACC weekly compensation module is encoded in RuleSpec form under `nz/statutes/acc/`.
- The module exposes the first weekly compensation surface needed for downstream modelling.
- The track includes companion tests for entitlement, floor, and cap behaviour.
- The implementation remains aligned with the shared income interfaces established in Track 23.
- The source evidence records the official legislation, ACC guidance, and rate notices used for the slice.

### Non-goals

- Full ACC earnings-loss, compensation, and levy coverage beyond the first slice.
- Oracle parity beyond the narrow comparison cases needed for this slice.
- NLP pipeline work; that remains a parallel dependency track.
