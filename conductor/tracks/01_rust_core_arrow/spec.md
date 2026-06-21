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
