#!/usr/bin/env python3
"""Run one example: python examples/run_example.py healthy_baseline."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocpe_disease_models.demonstrations import run_example  # noqa: E402

if __name__ == "__main__":
    import json

    print(json.dumps(run_example(sys.argv[1], ROOT), indent=2))
