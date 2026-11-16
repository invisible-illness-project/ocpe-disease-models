#!/usr/bin/env python3
"""Run all six required computational demonstrations."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocpe_disease_models.demonstrations import EXAMPLES, run_example  # noqa: E402

if __name__ == "__main__":
    reports = {name: run_example(name, ROOT) for name in EXAMPLES}
    print(json.dumps(reports, indent=2))
