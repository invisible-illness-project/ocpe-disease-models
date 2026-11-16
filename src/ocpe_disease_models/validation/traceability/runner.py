"""High-level audit runner: metadata collection, orchestration, exit codes."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .audit import (
    SEVERITY_ERROR,
    AuditContext,
    build_context,
    run_checks,
)
from .registries import load_all_registries
from .report import build_report, render_markdown, summarize, write_reports
from .schema_validation import check_schemas, schema_available

#: Default output directory for audit reports (relative to the repo root).
DEFAULT_OUT_DIR = Path("validation") / "traceability" / "audit"

#: Environment variables consulted for provenance metadata.
ENV_GIT_SHA = ("TRACEABILITY_GIT_SHA", "GIT_SHA", "GITHUB_SHA")
ENV_OCPE_COMMIT = ("OCPE_COMMIT", "OCPE_GIT_SHA")
ENV_DETERMINISTIC = "TRACEABILITY_DETERMINISTIC"

EXIT_OK = 0
EXIT_ERRORS = 1
EXIT_USAGE = 2


@dataclass
class AuditResult:
    """Outcome of a full audit run."""

    ctx: AuditContext
    report: dict[str, Any]
    markdown: str

    @property
    def error_count(self) -> int:
        return self.report["summary"]["errors"]

    @property
    def warning_count(self) -> int:
        return self.report["summary"]["warnings"]

    def exit_code(self, strict: bool) -> int:
        if strict and (self.error_count or self.warning_count):
            return EXIT_ERRORS
        return EXIT_OK


def _truthy(value: str | None) -> bool:
    return value is not None and value.strip().lower() in {"1", "true", "yes", "on"}


def _first_env(env: Mapping[str, str], names: Sequence[str]) -> str | None:
    for name in names:
        value = env.get(name)
        if value:
            return value
    return None


def _git_sha_from_repo(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def collect_metadata(
    root: Path,
    deterministic: bool = False,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Collect report provenance metadata.

    * ``generated_at``: UTC ISO-8601 timestamp, or ``None`` when
      ``deterministic`` is set (or ``TRACEABILITY_DETERMINISTIC`` is truthy)
      so that reports are byte-for-byte reproducible in tests.
    * ``git_sha``: from ``TRACEABILITY_GIT_SHA``/``GIT_SHA``/``GITHUB_SHA``
      when supplied, otherwise resolved with ``git rev-parse HEAD`` (skipped
      in deterministic mode).
    * ``ocpe_commit``: from ``OCPE_COMMIT``/``OCPE_GIT_SHA`` when supplied.
    """
    env = os.environ if env is None else env
    deterministic = deterministic or _truthy(env.get(ENV_DETERMINISTIC))
    git_sha = _first_env(env, ENV_GIT_SHA)
    if git_sha is None and not deterministic:
        git_sha = _git_sha_from_repo(Path(root))
    return {
        "generated_at": (
            None if deterministic else datetime.now(UTC).isoformat(timespec="seconds")
        ),
        "git_sha": git_sha,
        "ocpe_commit": _first_env(env, ENV_OCPE_COMMIT),
        "deterministic": deterministic,
    }


def run_audit(
    root: Path,
    deterministic: bool = False,
    env: Mapping[str, str] | None = None,
    validate_schemas: bool = True,
) -> AuditResult:
    """Load registries, run all checks, and build the reports."""
    root = Path(root).resolve()
    registries = load_all_registries(root)
    ctx = build_context(root, registries)
    run_checks(ctx)
    schema_status = "skipped"
    if validate_schemas:
        check_schemas(ctx)
        schema_status = "ran" if schema_available() else "unavailable"
    metadata = collect_metadata(root, deterministic=deterministic, env=env)
    report = build_report(ctx, metadata, schema_validation=schema_status)
    return AuditResult(ctx=ctx, report=report, markdown=render_markdown(report))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audit_traceability",
        description=(
            "Audit the machine-readable scientific traceability registries "
            "(references, evidence claims, mechanisms, equations, parameters, "
            "validation tests, simulations) and emit JSON + Markdown reports."
        ),
    )
    parser.add_argument(
        "--root",
        default=".",
        help="repository root containing the registries (default: cwd)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero when any error or warning finding exists (CI mode)",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help=f"report output directory (default: <root>/{DEFAULT_OUT_DIR})",
    )
    parser.add_argument(
        "--deterministic",
        action="store_true",
        help="suppress timestamps and git invocation for reproducible reports",
    )
    parser.add_argument(
        "--no-schema",
        action="store_true",
        help="skip JSON Schema validation even if jsonschema is installed",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="do not write report files (print summary only)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress the human-readable summary on stdout",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: --root {root} is not a directory", file=sys.stderr)
        return EXIT_USAGE

    result = run_audit(
        root,
        deterministic=args.deterministic,
        validate_schemas=not args.no_schema,
    )

    if not args.no_write:
        out_dir = Path(args.out_dir) if args.out_dir else root / DEFAULT_OUT_DIR
        json_path, md_path = write_reports(result.report, out_dir)
    else:
        json_path = md_path = None

    if not args.quiet:
        summary = summarize(result.ctx.findings)
        print(
            f"traceability audit: {summary['status'].upper()} "
            f"({summary['errors']} errors, {summary['warnings']} warnings, "
            f"{summary['infos']} infos)"
        )
        for finding in result.ctx.findings:
            if finding.severity == SEVERITY_ERROR:
                where = finding.entry_id or finding.registry or ""
                print(f"  ERROR [{finding.check}] {where}: {finding.message}")
        if json_path is not None:
            print(f"  JSON report:     {json_path}")
            print(f"  Markdown report: {md_path}")

    return result.exit_code(strict=args.strict)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
