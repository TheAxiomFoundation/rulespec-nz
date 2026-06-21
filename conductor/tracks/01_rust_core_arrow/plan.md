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

- [x] Task: Add a WASM target smoke contract (5796d63)
  Added an explicit `wasm` feature and minimal `wasm-bindgen` export that compiles without Python extension-module linking; verified with native no-default tests, WASM target check, WASM-feature tests, and clippy.
- [x] Task: Add Arrow Flight integration contract (cd9aaed)
  Added a repository-side Arrow Flight stream boundary contract for future transport work, including endpoint URI, stream name, schema fields, zero-copy expectation, and `live_transport_validated: false`.
- [x] Task: Add coverage gate evidence for native and Python binding layers (d21e1c3)
  Added a repository coverage evidence manifest and contract test for native Rust and Python binding layers. The artifact records reproducible coverage commands, the >90% threshold, supporting gates, and current blockers; the threshold remains `threshold_not_proven` because native `cargo llvm-cov` is blocked by missing `profiler_builtins` on this Windows GNU toolchain and the Python/PyO3 test path is blocked by disk-space exhaustion during final linking.
  Establish a reproducible coverage command and record whether Track 1 meets the >90% target from the specification.
