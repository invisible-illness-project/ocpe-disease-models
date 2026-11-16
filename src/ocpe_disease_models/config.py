"""Load traceable phenotype and simulation-protocol configurations."""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .models.shared.model import ComputationalPatient, ModelParameters, ProtocolSegment


def repository_root() -> Path:
    """Locate repository data in a source checkout or through an explicit override."""
    if value := os.environ.get("OCPE_DM_ROOT"):
        return Path(value).resolve()
    candidate = Path(__file__).resolve().parents[2]
    if (candidate / "phenotypes").is_dir():
        return candidate
    if (Path.cwd() / "phenotypes").is_dir():
        return Path.cwd()
    raise FileNotFoundError("Set OCPE_DM_ROOT to the ocpe-disease-models repository root")


@dataclass(frozen=True)
class Phenotype:
    phenotype_id: str
    label: str
    diseases: tuple[str, ...]
    mechanisms: tuple[str, ...]
    evidence_claims: tuple[str, ...]
    parameter_overrides: dict[str, float]
    maturity: str
    classification: str
    limitations: tuple[str, ...]
    source_path: str

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: Path, root: Path) -> Phenotype:
        return cls(
            phenotype_id=data["id"],
            label=data["label"],
            diseases=tuple(data.get("diseases", [])),
            mechanisms=tuple(data.get("mechanisms", [])),
            evidence_claims=tuple(data.get("evidence_claims", [])),
            parameter_overrides=dict(data.get("parameter_overrides", {})),
            maturity=data.get("maturity", "M1"),
            classification=data.get("classification", "phenomenological"),
            limitations=tuple(data.get("limitations", [])),
            source_path=str(source.relative_to(root)),
        )


def load_phenotype(phenotype_id: str, root: Path | None = None) -> Phenotype:
    root = root or repository_root()
    matches = list((root / "phenotypes").rglob(f"{phenotype_id}.yaml"))
    if len(matches) != 1:
        raise ValueError(f"Expected one phenotype {phenotype_id!r}, found {len(matches)}")
    data = yaml.safe_load(matches[0].read_text(encoding="utf-8"))
    return Phenotype.from_dict(data, matches[0], root)


def compose_phenotypes(
    phenotype_ids: Iterable[str], root: Path | None = None, composed_id: str | None = None
) -> ComputationalPatient:
    """Compose disjoint mechanism configurations without duplicating an engine.

    Conflicting values are rejected rather than silently determined by order.
    A named comorbidity YAML can instead make an evidence-specific joint choice.
    """
    ids = list(phenotype_ids)
    if not ids:
        raise ValueError("At least one phenotype is required")
    phenotypes = [load_phenotype(pid, root) for pid in ids]
    overrides: dict[str, float] = {}
    owners: dict[str, str] = {}
    for phenotype in phenotypes:
        for key, value in phenotype.parameter_overrides.items():
            if key in overrides and overrides[key] != value:
                raise ValueError(
                    f"Parameter conflict for {key}: {owners[key]} vs {phenotype.phenotype_id}; "
                    "define an explicit comorbidity configuration"
                )
            overrides[key] = value
            owners[key] = phenotype.phenotype_id
    pid = composed_id or "+".join(ids)
    provenance = {
        "phenotypes": [p.source_path for p in phenotypes],
        "mechanisms": sorted({m for p in phenotypes for m in p.mechanisms}),
        "evidence_claims": sorted({c for p in phenotypes for c in p.evidence_claims}),
        "maturity": min(p.maturity for p in phenotypes),
        "limitations": sorted({x for p in phenotypes for x in p.limitations}),
    }
    return ComputationalPatient(ModelParameters.from_mapping(overrides), pid, provenance)


def load_protocol(path_or_id: str | Path, root: Path | None = None) -> tuple[list[ProtocolSegment], dict[str, Any]]:
    root = root or repository_root()
    path = Path(path_or_id)
    if not path.exists():
        matches = list((root / "simulations").rglob(f"{path_or_id}.yaml"))
        if len(matches) != 1:
            raise ValueError(f"Expected one protocol {path_or_id!r}, found {len(matches)}")
        path = matches[0]
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    segments = [ProtocolSegment(**item) for item in data["segments"]]
    settings = dict(data.get("solver", {}))
    settings.setdefault("protocol_id", data.get("id", path.stem))
    settings["source_path"] = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    return segments, settings
