# Project Ledger Conventions

This repository uses the GitHub Project as an operational ledger for tracked
work. The board is not a substitute for the conductor track files; it mirrors
them.

## Field meanings

- `Status`: lifecycle of the project item.
- `Source status`: whether the source spine, citation paths, or blockers are
  known.
- `Oracle status`: comparison/parity state, or `not applicable` for pure
  tooling and roadmap items.
- `Conductor track`: the local track folder when a conductor track exists.
- `Upstream issue`: the issue that mirrors the track or roadmap item.
- `Upstream PR`: the PR that implements the item, when present.

## Operating rules

- Keep the source/oracle/status fields populated for every board item.
- Keep conductor tracks small and one-family only.
- Use the board for traceability, not for storing implementation details.
- Mirror repository changes in the relevant issue body when the project item
  changes.

## Roadmap linkage

The roadmap issue is the umbrella tracker for remaining coverage work. It should
point explicitly at the project-ledger conventions so contributors know how the
board, the issue, and conductor tracks relate.

## Practical rule

If a track or issue changes in the repository, update the matching project item
and the corresponding issue body in the same pass.
