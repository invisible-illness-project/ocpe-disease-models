#!/usr/bin/env python3
"""Run deterministic sensitivity and assumption-uncertainty scenarios."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocpe_disease_models.validation.sensitivity import run_analysis  # noqa: E402

if __name__ == "__main__":
    print(json.dumps(run_analysis(ROOT), indent=2))
