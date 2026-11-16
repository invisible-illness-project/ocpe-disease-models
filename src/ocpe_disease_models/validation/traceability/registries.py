"""Registry loading for the machine-readable scientific traceability subsystem.

Each registry is a YAML file containing a list of entries under a documented
top-level key:

===========================  ====================  ===========  ==============================
Registry                     Canonical top key     ID prefix    Default location(s)
===========================  ====================  ===========  ==============================
``references``               ``references``        ``REF-``     ``literature/references.yaml``
``evidence``                 ``evidence_claims``   ``CLM-``     ``evidence_registry.yaml``
``mechanisms``               ``mechanisms``        ``MEC-``     ``mechanism_registry.yaml``
``equations``                ``equations``         ``EQ-``      ``equation_registry.yaml``
``parameters``               ``parameters``        ``PAR-``     ``parameter_registry.yaml``
``validation_tests``         ``validation_tests``  ``VAL-``     ``validation/validation_registry.yaml``
``simulations``              ``simulations``       ``SIM-``     ``simulations/simulation_registry.yaml``
===========================  ====================  ===========  ==============================

The loader is deliberately flexible and robust:

* A missing registry file is tolerated (reported as "not found", not an error),
  because registries may be authored incrementally.
* A registry file may be either a mapping containing the documented top-level
  list key (canonical form) or a bare top-level YAML list of entries.
* Empty files load as empty registries.
* Malformed YAML, wrong top-level types, and non-mapping entries are reported
  as load errors (surfaced as audit ``error`` findings) instead of raising.

Only PyYAML and the standard library are required.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Registry specifications
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegistrySpec:
    """Static description of one traceability registry."""

    name: str
    """Logical registry name (e.g. ``"evidence"``)."""

    list_keys: tuple[str, ...]
    """Documented top-level YAML keys holding the entry list.

    The first key is the canonical/documented one; the others are accepted
    aliases for flexibility.
    """

    id_prefix: str
    """Stable ID prefix expected for entries (e.g. ``"CLM-"``)."""

    path_candidates: tuple[str, ...]
    """Relative paths (from the repo root) searched in order."""

    schema_file: str
    """Schema filename under ``validation/traceability/schemas``."""

    description: str = ""

    @property
    def canonical_key(self) -> str:
        return self.list_keys[0]


REGISTRY_SPECS: tuple[RegistrySpec, ...] = (
    RegistrySpec(
        name="references",
        list_keys=("references",),
        id_prefix="REF-",
        path_candidates=("literature/references.yaml",),
        schema_file="references.schema.json",
        description="Literature references / bibliographic sources",
    ),
    RegistrySpec(
        name="evidence",
        list_keys=("evidence_claims", "claims"),
        id_prefix="CLM-",
        path_candidates=(
            "literature/evidence_registry.yaml",
            "evidence_registry.yaml",
            "validation/traceability/evidence_registry.yaml",
        ),
        schema_file="evidence_registry.schema.json",
        description="Evidence claims extracted from the literature",
    ),
    RegistrySpec(
        name="mechanisms",
        list_keys=("mechanisms",),
        id_prefix="MEC-",
        path_candidates=(
            "literature/mechanism_registry.yaml",
            "mechanism_registry.yaml",
            "validation/traceability/mechanism_registry.yaml",
        ),
        schema_file="mechanism_registry.schema.json",
        description="Physiological mechanisms in the disease models",
    ),
    RegistrySpec(
        name="equations",
        list_keys=("equations",),
        id_prefix="EQ-",
        path_candidates=(
            "literature/equation_registry.yaml",
            "equation_registry.yaml",
            "validation/traceability/equation_registry.yaml",
        ),
        schema_file="equation_registry.schema.json",
        description="Model equations with assumptions and provenance",
    ),
    RegistrySpec(
        name="parameters",
        list_keys=("parameters",),
        id_prefix="PAR-",
        path_candidates=(
            "literature/parameter_registry.yaml",
            "parameter_registry.yaml",
            "validation/traceability/parameter_registry.yaml",
        ),
        schema_file="parameter_registry.schema.json",
        description="Model parameters with sources and estimation methods",
    ),
    RegistrySpec(
        name="validation_tests",
        list_keys=("validation_tests", "tests"),
        id_prefix="VAL-",
        path_candidates=("validation/validation_registry.yaml",),
        schema_file="validation_registry.schema.json",
        description="Scientific validation tests",
    ),
    RegistrySpec(
        name="simulations",
        list_keys=("simulations",),
        id_prefix="SIM-",
        path_candidates=("simulations/simulation_registry.yaml",),
        schema_file="simulation_registry.schema.json",
        description="Simulation outputs / runs",
    ),
)

SPECS_BY_NAME: dict[str, RegistrySpec] = {spec.name: spec for spec in REGISTRY_SPECS}

#: Directory (relative to repo root) holding the JSON Schemas.
SCHEMA_DIR = Path("validation") / "traceability" / "schemas"


# ---------------------------------------------------------------------------
# Loaded registry
# ---------------------------------------------------------------------------


@dataclass
class RegistryEntry:
    """A single entry in a registry, with its positional context."""

    registry: str
    index: int
    data: dict[str, Any]

    @property
    def entry_id(self) -> str | None:
        value = self.data.get("id")
        return str(value) if value is not None else None

    @property
    def label(self) -> str:
        return self.entry_id or f"{self.registry}[{self.index}]"


@dataclass
class Registry:
    """A loaded (or attempted) registry."""

    spec: RegistrySpec
    path: Path | None = None
    found: bool = False
    entries: list[RegistryEntry] = field(default_factory=list)
    load_errors: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def ids(self) -> set[str]:
        return {e.entry_id for e in self.entries if e.entry_id is not None}

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.entries)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def find_registry_path(root: Path, spec: RegistrySpec) -> Path | None:
    """Return the first existing candidate path for ``spec`` under ``root``."""
    for rel in spec.path_candidates:
        candidate = root / rel
        if candidate.is_file():
            return candidate
    return None


def load_registry(root: Path, spec: RegistrySpec) -> Registry:
    """Load a single registry, never raising on bad content.

    All problems are captured in ``Registry.load_errors``.
    """
    root = Path(root)
    path = find_registry_path(root, spec)
    if path is None:
        return Registry(spec=spec, path=None, found=False)

    registry = Registry(spec=spec, path=path, found=True)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - rare
        registry.load_errors.append(f"unreadable file: {exc}")
        return registry

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        registry.load_errors.append(f"YAML parse error: {exc}")
        return registry

    raw_entries: Any
    if data is None:
        raw_entries = []
    elif isinstance(data, list):
        # Flexible form: bare top-level list of entries.
        raw_entries = data
    elif isinstance(data, dict):
        raw_entries = None
        for key in spec.list_keys:
            if key in data:
                raw_entries = data[key]
                break
        if raw_entries is None:
            registry.load_errors.append(
                "top-level mapping has none of the documented list keys "
                + ", ".join(repr(k) for k in spec.list_keys)
            )
            return registry
    else:
        registry.load_errors.append(
            f"top-level YAML value must be a mapping or list, got {type(data).__name__}"
        )
        return registry

    if raw_entries is None:
        raw_entries = []
    if not isinstance(raw_entries, list):
        registry.load_errors.append(
            f"entry list under documented key must be a YAML list, got {type(raw_entries).__name__}"
        )
        return registry

    for index, item in enumerate(raw_entries):
        if not isinstance(item, dict):
            registry.load_errors.append(
                f"entry {index} is not a mapping (got {type(item).__name__})"
            )
            continue
        registry.entries.append(RegistryEntry(registry=spec.name, index=index, data=item))
    return registry


def load_all_registries(root: Path) -> dict[str, Registry]:
    """Load every known registry under ``root``."""
    root = Path(root)
    return {spec.name: load_registry(root, spec) for spec in REGISTRY_SPECS}


# ---------------------------------------------------------------------------
# Small helpers shared with the audit layer
# ---------------------------------------------------------------------------


def iter_strings(obj: Any) -> Iterator[str]:
    """Yield every string scalar nested inside ``obj`` (values only)."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from iter_strings(value)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            yield from iter_strings(item)


def first_present(entry: dict[str, Any], *names: str) -> tuple[Any, str | None]:
    """Return ``(value, field_name)`` for the first present, non-``None`` field.

    Returns ``(None, None)`` when none of the candidate fields are set. This
    implements the flexible field-name conventions documented in
    :mod:`ocpe_disease_models.validation.traceability.audit`.
    """
    for name in names:
        if name in entry and entry[name] is not None:
            return entry[name], name
    return None, None


def is_nonempty(value: Any) -> bool:
    """True when ``value`` is present and not an empty string/list/dict."""
    if value is None:
        return False
    if isinstance(value, (str, list, tuple, dict, set)):
        return len(value) > 0
    return True
