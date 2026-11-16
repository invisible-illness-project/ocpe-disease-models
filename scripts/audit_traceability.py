#!/usr/bin/env python3
"""Audit the scientific traceability registries and emit reports.

Usage (from the repository root):

    python scripts/audit_traceability.py --root . --strict

Writes ``traceability_report.json`` and ``traceability_report.md`` under
``validation/traceability/audit/`` by default and exits non-zero in
``--strict`` mode when any error-severity finding exists (CI gate).

Environment variables:
    TRACEABILITY_GIT_SHA / GIT_SHA / GITHUB_SHA
        Git SHA recorded in the report (otherwise ``git rev-parse HEAD``).
    OCPE_COMMIT / OCPE_GIT_SHA
        Commit of the OCPE engine recorded in the report, when supplied.
    TRACEABILITY_DETERMINISTIC
        When truthy (1/true/yes), suppress timestamps and git invocation so
        reports are byte-for-byte reproducible.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make ``src/`` importable without requiring an installed package.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

try:
    from ocpe_disease_models.validation.traceability.runner import main
except ImportError as exc:  # pragma: no cover - defensive
    print(f"error: unable to import traceability subsystem: {exc}", file=sys.stderr)
    print(f"(looked for package under {_SRC})", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    sys.exit(main())
