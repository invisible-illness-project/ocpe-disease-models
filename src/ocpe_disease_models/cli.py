"""Command-line entry points for reproducible demonstrations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import compose_phenotypes, load_protocol
from .demonstrations import EXAMPLES, run_example


def main() -> int:
    parser = argparse.ArgumentParser(prog="ocpe-dm", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("simulate", help="Run one phenotype/protocol validation trace")
    run.add_argument("--phenotype", required=True)
    run.add_argument("--protocol", required=True)
    run.add_argument("--output", type=Path, required=True)
    example = sub.add_parser("example", help="Run a required computational demonstration")
    example.add_argument("name", choices=EXAMPLES)
    sub.add_parser("list-examples", help="List available demonstrations")
    args = parser.parse_args()
    if args.command == "list-examples":
        print("\n".join(EXAMPLES))
        return 0
    if args.command == "example":
        print(json.dumps(run_example(args.name), indent=2))
        return 0
    patient = compose_phenotypes([args.phenotype])
    segments, settings = load_protocol(args.protocol)
    solver = {k: v for k, v in settings.items() if k in {"sample_interval", "max_step", "rtol", "atol", "seed"}}
    result = patient.simulate(segments, **solver)
    result.save(args.output)
    print(json.dumps(result.summary(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
