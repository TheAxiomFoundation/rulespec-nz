# Track Plan: Rust Core & Apache Arrow Integration

This plan implements Track 1 to build the Rust core engine with Apache Arrow/Polars zero-copy bindings.

---

## Phase 1: Engine Core Scaffolding

- [ ] Task: Set up Rust crate structure under rulespec-nz core
  Initialize `Cargo.toml` with `pyo3`, `arrow`, `polars`, and `serde`.
- [ ] Task: Implement PyO3 binding framework
  Expose simple Rust mathematical operations to Python to verify the pyo3 toolchain.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Engine Core Scaffolding' (Protocol in workflow.md)

---

## Phase 2: Zero-Copy Arrow Processing

- [ ] Task: Implement Arrow record batch passing
  Build PyO3 wrappers receiving Arrow Array pointers from Python.
- [ ] Task: Validate Polars zero-copy reads in Rust
  Verify memory sharing of synthetic populations from Python Polars to Rust memory spaces.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Zero-Copy Arrow Processing' (Protocol in workflow.md)
