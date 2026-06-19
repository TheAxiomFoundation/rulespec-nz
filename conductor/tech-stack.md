# Technology Stack - NZ RuleSpec Encodings

This document defines the technology stack, compilers, runtimes, package managers, and toolchains utilized in this project.

## Core Rule Specification & Logic
- **RuleSpec (YAML)**: Direct declarative policy rules, parameters, and variable definitions.
- **RuleSpec Test Suites (YAML)**: Companion `.test.yaml` files containing scenario inputs and expected outcomes.
- **Axiom Toolchain**: Custom compilers and validators for translating RuleSpec inputs into executable engines (utilizing `axiom-corpus` and `axiom-encode`).

## Runtimes & Languages
- **Python**: Executable test suites, repository layout verification, and Axiom CLI wrapper execution.
- **R Language**: Legacy simulation comparisons, disposable-income computations, and EMTR chart generation.

## Environment & Dependency Management (Bleeding Edge)
- **Pixi**: Modern, high-performance package management and multi-language dependency workflow environment tool (based on conda/mamba, handling Python, R, and Axiom binaries).
- **uv**: Ultrafast Python resolver and runtime manager, nested within Pixi tasks if necessary for Python-specific workflows.
