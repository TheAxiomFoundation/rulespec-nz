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
  Added a repository coverage evidence manifest and contract test for native Rust and Python binding layers. The artifact records reproducible coverage commands, the >90% threshold, supporting gates, and current blockers.
  Establish a reproducible coverage command and record whether Track 1 meets the >90% target from the specification.

---

## Review and Archive Note

- 2026-06-23 Conductor review outcome: archived with unresolved coverage validation blocker.
- Passing gates rerun during review:
  - `python -m pytest tests\test_rust_core_arrow_coverage_manifest.py -q -p no:cacheprovider`
  - `cargo test --manifest-path rulespec-nz\Cargo.toml --no-default-features`
- 2026-06-23 blocker remediation update: removed unused `serde`, `serde_yaml`, and `chrono` dependencies from `rulespec-nz/Cargo.toml` so the no-default/native test path compiles only the Track 1 crate.
- Passing gates rerun during blocker remediation:
  - `cargo fmt --manifest-path rulespec-nz\Cargo.toml --check`
  - `cargo test --manifest-path rulespec-nz\Cargo.toml --no-default-features`
- Current blocker evidence:
  - `cargo llvm-cov --manifest-path rulespec-nz\Cargo.toml --no-default-features --summary-only --json` still exits 101 on stable-x86_64-pc-windows-gnu with `error[E0463]: can't find crate for profiler_builtins`.
  - `cargo +stable-x86_64-pc-windows-msvc test --manifest-path rulespec-nz\Cargo.toml --no-default-features` exits 101 because `link.exe` resolves to Git's Unix linker rather than the Visual Studio linker.
  - `wmic logicaldisk` reported less than 60 MB free on `C:`, so the Python/PyO3 feature coverage path cannot be rebuilt safely on this host.
- Residual blocker: `data/coverage/rust-core-arrow-coverage.json` now reports `coverage_status: blocked_by_host_toolchain_and_disk`; do not treat Track 1 as fully complete until native Rust and Python binding coverage evidence proves the >90% gate required by `spec.md` on a host with a supported profiler runtime and Visual Studio Build Tools or Windows SDK import libraries available to the linker.
