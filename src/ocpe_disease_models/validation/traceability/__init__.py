"""Machine-readable scientific traceability subsystem.

Loads the YAML registries (literature references, evidence claims,
mechanisms, equations, parameters, validation tests, simulations), audits
their completeness and cross-registry linkage, and emits JSON + Markdown
reports suitable for CI.

Only PyYAML and the standard library are required; :mod:`jsonschema` is used
for schema validation when available.
"""

from .audit import (
    SEVERITY_ERROR,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    AuditContext,
    Finding,
    Metric,
    build_context,
    run_checks,
)
from .registries import (
    REGISTRY_SPECS,
    Registry,
    RegistryEntry,
    RegistrySpec,
    load_all_registries,
    load_registry,
)
from .report import build_report, render_markdown, write_reports
from .runner import AuditResult, collect_metadata, main, run_audit

__all__ = [
    "AuditContext",
    "AuditResult",
    "Finding",
    "Metric",
    "REGISTRY_SPECS",
    "Registry",
    "RegistryEntry",
    "RegistrySpec",
    "SEVERITY_ERROR",
    "SEVERITY_INFO",
    "SEVERITY_WARNING",
    "build_context",
    "build_report",
    "collect_metadata",
    "load_all_registries",
    "load_registry",
    "main",
    "render_markdown",
    "run_audit",
    "run_checks",
    "write_reports",
]
