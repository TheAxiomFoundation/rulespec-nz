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
- [~] Task: Validate Polars zero-copy reads in Rust
  Verify memory sharing of synthetic populations from Python Polars to Rust memory spaces.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Zero-Copy Arrow Processing' (Protocol in workflow.md)
