# Track 8: Microsimulation Synthetic Population Builder

## Goal

Define the repository-side builder contract for synthetic microsimulation populations sourced from `open_social_data` and `fyi-cli`, without committing raw population payloads or administrative microdata.

## Scope

- Record expected local external generators and environment-variable path hooks.
- Define stable Arrow-oriented entity tables for persons, households, and benefit units.
- Map entity columns to RuleSpec input names used by tax-benefit evaluations.
- Preserve privacy boundaries: synthetic-only data, no direct identifiers, no raw administrative data.
- Define repository boundaries for local payloads and deliberately promoted small fixtures.

## Out of Scope

- Running live `open_social_data` or `fyi-cli` generators.
- Committing full synthetic population Parquet payloads.
- Ingesting raw administrative microdata.
- Building a complete microsimulation engine or calibration pipeline in this track.

## Acceptance Criteria

- A synthetic population builder manifest exists under `data/microsimulation/`.
- The manifest covers both `open_social_data` and `fyi-cli` as expected local external inputs.
- The manifest records entity schemas, RuleSpec input mappings, target policy surfaces, privacy boundaries, and repository boundaries.
- Tests verify the builder contract without requiring live generator access.

## Archive Status

Archived on 2026-06-23 after review confirmed the builder contract, privacy boundary, synthetic smoke fixture, and partial-blocked live-validation record pass focused tests.
