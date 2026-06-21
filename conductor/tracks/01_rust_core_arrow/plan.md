# Track Plan: Rust Core & Apache Arrow Integration

This plan implements Track 1 to build the Rust core engine with Apache Arrow/Polars zero-copy bindings.

---

## Phase 1: Engine Core Scaffolding

- [x] Task: Set up Rust crate structure under rulespec-nz core (085b1d5)
  Initialize `Cargo.toml` with `pyo3`, `arrow`, `polars`, and `serde`.
- [x] Task: Implement PyO3 binding framework (5e83f6c)
  Expose simple Rust mathematical operations to Python to verify the pyo3 toolchain.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Engine Core Scaffolding' (Protocol in workflow.md) (624c316)
  Verified on 2026-06-19 with `cargo fmt --check`, `cargo check`, and `cargo test --no-default-features`. PyO3 now uses `abi3-py38` so Rust tests run without a version-specific Python DLL while the default extension-module feature remains enabled.

---

## Phase 2: Zero-Copy Arrow Processing

- [x] Task: Implement Arrow record batch passing (50b97a8)
  Build PyO3 wrappers receiving Arrow Array pointers from Python.
- [x] Task: Validate Polars zero-copy reads in Rust (c6e5a9f)
  Verified on 2026-06-21 with `cargo fmt --check` and `cargo test --no-default-features`; the Rust unit test `polars_i64_series_reads_through_arrow_batch_without_copying_values` confirms the Arrow values buffer pointer matches the source Polars contiguous slice pointer.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Zero-Copy Arrow Processing' (Protocol in workflow.md) (bd99855)
  Verified on 2026-06-21 with `cargo fmt --check`, `cargo check --no-default-features`,
  `cargo test --no-default-features`, and `cargo clippy --no-default-features -- -D warnings`.

---

## Phase 3: Remaining Runtime and Quality Coverage

- [ ] Task: Add a WASM target smoke contract
  Verify the Rust core exposes a minimal `wasm-bindgen` build path without depending on Python extension-module linking.
- [ ] Task: Add Arrow Flight integration contract
  Define the repository-side Arrow Flight stream boundary and add a focused contract test or fixture for future transport work.
- [ ] Task: Add coverage gate evidence for native and Python binding layers
  Establish a reproducible coverage command and record whether Track 1 meets the >90% target from the specification.
