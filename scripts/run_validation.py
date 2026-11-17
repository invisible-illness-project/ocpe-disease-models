#!/usr/bin/env python3
"""Report all seven validation layers independently and fail on missing tests."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocpe_disease_models import OCPE_COMMIT, __version__  # noqa: E402
from ocpe_disease_models.validation.traceability.runner import run_audit  # noqa: E402

LAYERS = {
    "software": "software or regression",
    "mathematical": "mathematical",
    "physiological": "physiological",
    "disease_phenotype": "phenotype",
    "empirical": "empirical",
    "sensitivity_uncertainty": "sensitivity_uncertainty",
    "scientific_traceability": "scientific_traceability",
}


def _run_layer(layer: str, marker: str, report_dir: Path) -> dict[str, object]:
    command = [sys.executable, "-m", "pytest", "-q", "-m", marker]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    log = completed.stdout + completed.stderr
    (report_dir / f"{layer}.log").write_text(log, encoding="utf-8")
    summary = next((line for line in reversed(log.splitlines()) if "passed" in line or "failed" in line or "no tests ran" in line), "no pytest summary")
    # Exit code 5 (no tests collected) is deliberately a failure, not a skip.
    # A strict xfail keeps the executable suite reproducible, but the unchanged
    # scientific assertion still failed and must not become a validation pass.
    expected_failures = "xfailed" in log
    execution_passed = completed.returncode == 0
    return {
        "layer": layer,
        "marker": marker,
        "command": command,
        "exit_code": completed.returncode,
        "execution_status": "PASS" if execution_passed else "FAIL",
        "status": "PASS" if execution_passed and not expected_failures else "FAIL",
        "contains_strict_expected_failures": expected_failures,
        "status_reason": (
            "Strict expected failures preserve unresolved scientific criterion misses."
            if expected_failures
            else None
        ),
        "pytest_summary": summary,
        "log": str((report_dir / f"{layer}.log").relative_to(ROOT)),
    }


def _repository_commit() -> str:
    """Record the exact source revision under test without changing it."""
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "UNKNOWN"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layer", action="append", choices=list(LAYERS), help="run only the selected layer; repeatable")
    parser.add_argument("--no-analysis", action="store_true", help="do not regenerate sensitivity outputs before its test layer")
    args = parser.parse_args()
    selected = args.layer or list(LAYERS)
    report_dir = ROOT / "validation" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    if "sensitivity_uncertainty" in selected and not args.no_analysis:
        command = [sys.executable, "scripts/run_sensitivity.py"]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        (report_dir / "sensitivity-analysis.log").write_text(completed.stdout + completed.stderr, encoding="utf-8")
        if completed.returncode:
            print(completed.stdout + completed.stderr, file=sys.stderr)
            return completed.returncode
    results = [_run_layer(layer, LAYERS[layer], report_dir) for layer in selected]
    audit = run_audit(ROOT, deterministic=True)
    audit_summary = dict(audit.report["summary"])
    audit_passed = audit.exit_code(strict=True) == 0
    if "scientific_traceability" in selected:
        for result in results:
            if result["layer"] == "scientific_traceability":
                result["audit"] = audit_summary
                if not audit_passed:
                    result["status"] = "FAIL"
    overall = all(result["status"] == "PASS" for result in results) and (
        audit_passed or "scientific_traceability" not in selected
    )
    payload = {
        "schema_version": "1.0",
        "model_version": __version__,
        "repository_commit": _repository_commit(),
        "ocpe_commit": OCPE_COMMIT,
        "python_version": platform.python_version(),
        "clinical_status": "Research software and scenario validation only; no clinical validity or diagnostic accuracy is established.",
        "required_tests_policy": "A missing layer, empty pytest selection, failed audit, or warning in strict traceability is a failure, not a skip. Strict expected failures remain scientific failures even when pytest exits successfully.",
        "overall_status": "PASS" if overall else "FAIL",
        "layers": results,
    }
    (report_dir / "validation-report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Seven-layer validation report",
        "",
        "A pass denotes completion of the declared computational check only. Software execution, numerical convergence, phenotype threshold matching, and group-level empirical agreement are independently necessary and are not clinical validation.",
        "",
        "| Layer | Status | Pytest result |",
        "|---|---|---|",
    ]
    lines.extend(f"| {r['layer']} | {r['status']} | {r['pytest_summary']} |" for r in results)
    lines.extend(["", f"Strict traceability: {'PASS' if audit_passed else 'FAIL'} — {audit_summary['errors']} errors, {audit_summary['warnings']} warnings.", "", f"**Overall: {payload['overall_status']}**", ""])
    (report_dir / "validation-report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
