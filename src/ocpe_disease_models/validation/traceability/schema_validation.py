"""Optional JSON Schema validation for the core registries.

Schemas live under ``validation/traceability/schemas`` in the repository.
Validation uses :mod:`jsonschema` when it is installed; otherwise it is
skipped cleanly (the structural audit checks in :mod:`.audit` are always
active and have no optional dependencies).

Because registry files are allowed the flexible bare-list form, entries are
wrapped into the canonical mapping form before being validated against the
schema.
"""

from __future__ import annotations

import json
from pathlib import Path

from .audit import SEVERITY_ERROR, SEVERITY_INFO, AuditContext
from .registries import SCHEMA_DIR, Registry

try:  # optional dependency
    import jsonschema
except ImportError:  # pragma: no cover - depends on environment
    jsonschema = None  # type: ignore[assignment]


def schema_available() -> bool:
    """True when the optional :mod:`jsonschema` dependency is importable."""
    return jsonschema is not None


def load_schema(root: Path, registry: Registry) -> dict | None:
    """Load the JSON Schema for a registry, or ``None`` when absent/invalid."""
    schema_path = Path(root) / SCHEMA_DIR / registry.spec.schema_file
    if not schema_path.is_file():
        return None
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def check_schemas(ctx: AuditContext) -> None:
    """Validate each found registry against its JSON Schema, when possible."""
    if jsonschema is None:
        ctx.add(
            "schema-validation-skipped",
            SEVERITY_INFO,
            "optional dependency 'jsonschema' is not installed; schema validation skipped",
        )
        return
    for registry in ctx.registries.values():
        if not registry.found or registry.load_errors:
            continue
        schema = load_schema(ctx.root, registry)
        if schema is None:
            ctx.add(
                "schema-not-found",
                SEVERITY_INFO,
                f"no JSON Schema found for registry {registry.name!r}",
                registry=registry.name,
            )
            continue
        document = {registry.spec.canonical_key: [e.data for e in registry.entries]}
        validator = jsonschema.validators.validator_for(schema)(schema)
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path)):
            entry_index = None
            path = list(error.absolute_path)
            if len(path) >= 2 and isinstance(path[1], int):
                entry_index = path[1]
            entry = (
                registry.entries[entry_index]
                if entry_index is not None and entry_index < len(registry.entries)
                else None
            )
            location = "/".join(str(p) for p in path) or "<root>"
            ctx.add(
                "schema-violation",
                SEVERITY_ERROR,
                f"schema {registry.spec.schema_file}: {error.message} (at {location})",
                entry=entry,
                registry=registry.name if entry is None else None,
            )
