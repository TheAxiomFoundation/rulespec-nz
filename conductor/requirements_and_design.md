# System Requirements (MoSCoW) & Architecture Design

This document details the requirements and the system design for the NZ Rules-as-Code (RaC) simulation pipeline.

---

## 1. Requirements (MoSCoW)

### Must Have
*   **Rust-based Core & PyO3 Bindings:** High-performance evaluation core exposed to Python.
*   **Zero-Copy Memory Layout:** Integration of Apache Arrow/Polars for processing microdata without copying overhead.
*   **NZ Statutory Ingestion:** Adapt to local Parquet data layers parsed from `corpus-legislation-nz` and `corpus-nz-hansard`.
*   **YAML RuleSpec Validation:** Parse and compile the NZ RuleSpec schemas (`statutes`, `regulations`, `policies`).
*   **Strict Rust Quality Gates:** Comprehensive formatting (`rustfmt`) and strict linting constraints (`clippy --deny warnings`) in the local/CI loop.

### Should Have
*   **WASM Compilation Target:** Compile the core `rulespec-nz` logic to WebAssembly via `wasm-bindgen` for high-performance client-side browser evaluation.
*   **Arrow Flight Data Ingestion:** Use Apache Arrow Flight TCP streams for low-latency, parallel transfers of micro-simulation data between execution pipelines.
*   **Type-State Compile-Time Verification:** Enforce legislative states and calculations via Rust type-state pattern to catch invalid policy paths at compile-time.
*   **Cranelift JIT Compilation Engine:** JIT-compile RuleSpec files to native machine code at runtime using Cranelift to eliminate evaluation loop overhead.
*   **OpenFisca Migration Adapter:** Automatic parsing utility to map legacy `openfisca-aotearoa` Python code to RuleSpec YAML.
*   **Microsimulation Data Pipe:** Interface to inject synthetic populations from `open_social_data`.
*   **Value of Information Routing:** Link outputs to the `mars` regression and `voiage` VoI libraries.

### Could Have
*   **Fully Homomorphic Encryption (FHE):** Run simulations on encrypted administrative population microdata using `tfhe-rs` without exposing raw records.
*   **Zero-Knowledge Proof (ZKP) Targets:** Compile rules to zk-SNARK constraint systems using `arkworks` or Noir for private eligibility assertions.
*   **Differential Dataflow Calculations:** Low-latency incremental engine evaluations using `differential-dataflow` to re-compute only affected population nodes.
*   **Formal Proof Solvers:** Compile RuleSpec equations into SMT-LIB2 structures for formal proof verification via Z3 Solver.
*   **Distributed Ray-on-Arrow Grid:** Scale simulations horizontally using a distributed cluster architecture.
*   **WebGPU/SIMD Vectorized Acceleration:** Massively parallel GPU/SIMD execution (via `wgpu-rs`) for country-scale synthetic populations.
*   **Automated Source-Spec Auditing:** Automated CI validation layers matching compiled rules to parsed legislative text in `corpus-legislation-nz` using semantic checking.
*   **Scraped Admin Ingestion:** Integration with `fyi-cli` metadata.
*   **Temporal Ledger Management:** Policy state lifecycle tracking using `kairos` and `TheAxiomFoundation`.

### Won't Have (for this phase)
*   Real-time public API web service deployment.

---

## 2. System Architecture Design

```mermaid
graph TD
    subgraph Raw Data Ingestion
        A[corpus-legislation-nz] -->|Parquet| B[nlp-policy-nz]
        C[open_social_data] -->|Synthetic Microdata| D[Polars DataFrames]
    end

    subgraph Simulation Core
        B -->|Ingested Statutes| E[rulespec-nz Rust Engine]
        D -->|Zero-Copy Arrow RecordBatches| E
        F[OpenFisca Migration Adapter] -->|Transpiled YAML| E
        E -->|Compiled WASM target| E_WASM[WebAssembly Engine Client-Side]
        E -->|WebGPU/SIMD Hardware Acceleration| E_GPU[Parallel Execution Grid]
        E -->|Formal Verification Target| E_SMT[Z3 SMT Proof Solver]
        E -->|Compile-Time Verification| E_TYPE[Type-State Static Asserts]
        E -->|Timely / Differential Stream| E_DIFF[Differential Dataflow Pipeline]
        E -->|Cranelift JIT Pipeline| E_JIT[JIT Native Compiler Engine]
        E -->|Noir/zk-SNARK compilation| E_ZKP[Zero-Knowledge Proof Gates]
        E -->|tfhe-rs evaluation| E_FHE[Homomorphic Private Microdata Layer]
    end

    subgraph Evaluation & Analysis
        E -->|Arrow Flight TCP Stream| G[mars Regression]
        E -->|Arrow Flight TCP Stream| H[voiage VoI Library]
    end

    subgraph State Ledger
        I[TheAxiomFoundation + kairos] <-->|Temporal Policies Ledger| E
    end
```

### Zero-Copy Arrow & Flight Integration Flow

```mermaid
sequenceDiagram
    participant C as Web Browser (Client Calculator)
    participant P as Python Environment (Polars)
    participant R as Rust Core (rulespec-nz)
    participant A as Apache Arrow Shared Memory
    participant F as Arrow Flight Endpoint (mars/voiage)

    C->>R: Load WebAssembly module (wasm-bindgen)
    P->>A: Allocate Arrow Table (Synthetic Population)
    P->>R: Pass Memory Pointer (Arrow Array Interface)
    Note over R: Safe Zero-Copy Read
    R->>R: SIMD/WebGPU Vectorized Calculation
    R->>A: Write Outputs (Tax Liability, Entitlements)
    R->>F: Stream batches via Arrow Flight TCP
    R->>P: Return Arrow Output Array Reference
```
