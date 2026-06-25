# Track Specification: Rust Core & Apache Arrow Integration

## 1. Description and Goal
Establish a Rust-based core engine for `rulespec-nz` that compiles to PyO3 bindings for Python and WebAssembly (WASM) targets, utilizing zero-copy Apache Arrow/Polars data frames and Arrow Flight streams.

## 2. Technical Stack Context
- **Runtimes:** Python (exposed via PyO3), WebAssembly (via `wasm-bindgen`).
- **Core Libraries:** `arrow`, `polars`, `pyo3`, `wasm-bindgen`, `timely-dataflow`, `differential-dataflow`, `tfhe-rs` (optional), `arkworks` (optional), `cranelift` (optional).
- **Quality Gates:** 
  - All Rust functions verified via cargo clippy/rustfmt.
  - Test suites covering native and Python binding layers with >90% coverage.
  - Zero-copy data integrity verified.

## 3. Archive Status

Archived on 2026-06-23 with the coverage quality gate unresolved. A later blocker-remediation pass removed unused native dependencies and refreshed the evidence contract, but this host still cannot prove the >90% native Rust and Python binding coverage threshold because GNU coverage lacks `profiler_builtins`, MSVC linking resolves to Git's Unix `link.exe`, and forcing `rust-lld` fails because Windows SDK import libraries are unavailable.
