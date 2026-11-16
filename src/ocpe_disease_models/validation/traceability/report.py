"""JSON and Markdown reporting for the traceability audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit import (
    SEVERITIES,
    SEVERITY_ERROR,
    AuditContext,
    Finding,
)

TOOL_NAME = "ocpe-traceability-audit"
TOOL_VERSION = "1.0.0"
DEFAULT_JSON_NAME = "traceability_report.json"
DEFAULT_MARKDOWN_NAME = "traceability_report.md"


def summarize(findings: list[Finding]) -> dict[str, Any]:
    counts = {severity: 0 for severity in SEVERITIES}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return {
        "errors": counts.get(SEVERITY_ERROR, 0),
        "warnings": counts.get("warning", 0),
        "infos": counts.get("info", 0),
        "total_findings": len(findings),
        "status": "fail" if counts.get(SEVERITY_ERROR, 0) else "pass",
    }


def build_report(
    ctx: AuditContext,
    metadata: dict[str, Any],
    schema_validation: str = "skipped",
) -> dict[str, Any]:
    """Build the machine-readable report as a JSON-serializable dict."""
    registries = {}
    for name, registry in ctx.registries.items():
        path: str | None = None
        if registry.path is not None:
            try:
                path = str(registry.path.relative_to(ctx.root))
            except ValueError:
                path = str(registry.path)
        registries[name] = {
            "path": path,
            "found": registry.found,
            "entries": len(registry.entries),
            "id_prefix": registry.spec.id_prefix,
            "load_errors": list(registry.load_errors),
        }
    return {
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "generated_at": metadata.get("generated_at"),
        "git_sha": metadata.get("git_sha"),
        "ocpe_commit": metadata.get("ocpe_commit"),
        "deterministic": bool(metadata.get("deterministic", False)),
        "schema_validation": schema_validation,
        "root": str(ctx.root),
        "summary": summarize(ctx.findings),
        "registries": registries,
        "completeness": {
            registry: {metric: m.as_dict() for metric, m in metrics.items()}
            for registry, metrics in ctx.completeness.items()
        },
        "findings": [finding.as_dict() for finding in ctx.findings],
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render the report dict as a human-readable Markdown document."""
    lines: list[str] = []
    summary = report["summary"]
    lines.append("# Scientific Traceability Audit Report")
    lines.append("")
    lines.append(f"- Tool: `{report['tool']}` v{report['version']}")
    lines.append(f"- Generated at: {report.get('generated_at') or 'deterministic (suppressed)'}")
    lines.append(f"- Git SHA: {report.get('git_sha') or 'unknown'}")
    lines.append(f"- OCPE commit: {report.get('ocpe_commit') or 'unknown'}")
    lines.append(f"- Schema validation: {report.get('schema_validation', 'skipped')}")
    lines.append(
        f"- **Status: {'FAIL' if summary['status'] == 'fail' else 'PASS'}** "
        f"({summary['errors']} errors, {summary['warnings']} warnings, "
        f"{summary['infos']} infos)"
    )
    lines.append("")

    lines.append("## Registries")
    lines.append("")
    lines.append("| Registry | Path | Entries | Load errors |")
    lines.append("| --- | --- | ---: | ---: |")
    for name, info in report["registries"].items():
        path = info["path"] or "*(not found)*"
        lines.append(f"| {name} | {path} | {info['entries']} | {len(info['load_errors'])} |")
    lines.append("")

    lines.append("## Completeness")
    lines.append("")
    lines.append("| Registry | Metric | Passed | Total | Rate |")
    lines.append("| --- | --- | ---: | ---: | ---: |")
    for registry, metrics in report["completeness"].items():
        for metric, m in metrics.items():
            rate = "n/a" if m["rate"] is None else f"{m['rate'] * 100:.1f}%"
            lines.append(f"| {registry} | {metric} | {m['passed']} | {m['total']} | {rate} |")
    lines.append("")

    lines.append("## Findings")
    lines.append("")
    if not report["findings"]:
        lines.append("No findings. Full traceability achieved.")
        lines.append("")
    else:
        for severity in SEVERITIES:
            group = [f for f in report["findings"] if f["severity"] == severity]
            if not group:
                continue
            lines.append(f"### {severity.capitalize()}s ({len(group)})")
            lines.append("")
            for finding in group:
                location = ""
                if finding.get("registry"):
                    location = f"`{finding['registry']}`"
                if finding.get("entry_id"):
                    location += f" `{finding['entry_id']}`"
                where = f" {location.strip()}" if location else ""
                lines.append(f"- **[{finding['check']}]**{where}: {finding['message']}")
            lines.append("")
    return "\n".join(lines)


def write_reports(
    report: dict[str, Any],
    out_dir: Path,
    json_name: str = DEFAULT_JSON_NAME,
    markdown_name: str = DEFAULT_MARKDOWN_NAME,
) -> tuple[Path, Path]:
    """Write JSON and Markdown reports into ``out_dir``; return their paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / json_name
    markdown_path = out_dir / markdown_name
    json_path.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path
