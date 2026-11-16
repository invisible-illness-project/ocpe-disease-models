#!/usr/bin/env python3
"""Source-checkout wrapper for the ocpe-dm CLI."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocpe_disease_models.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
