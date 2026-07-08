#!/usr/bin/env python3
"""Print the guard-generated `--roots` for an applied module path.

`axiom-encode guard-generated --roots` wants the space-separated content roots
that the changed files live under. rulespec-nz keeps all encoded modules under a
single `nz/` jurisdiction directory (`nz/statutes/`, `nz/regulations/`,
`nz/policies/`), so a bulk job's root is always `nz`.

Usage:
  python bulk/roots_for.py nz/statutes/income_tax/family_scheme/tax_credits.yaml  # -> "nz"
"""

from __future__ import annotations

import sys
from pathlib import PurePosixPath


def roots_for(module_path: str) -> str:
    parts = PurePosixPath(module_path).parts
    if parts and parts[0] == "nz":
        return "nz"
    # Fall back to the jurisdiction root; every encoded module lives under nz/.
    return "nz"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: roots_for.py <module-path>", file=sys.stderr)
        raise SystemExit(2)
    print(roots_for(sys.argv[1]))
