"""Adapter between ocpe-disease-models and the OCPE 0.1 engine.

The adapter is the single supported entry point for the semantic layer:

* it pins the upstream OCPE engine/specification commit
  (:data:`UPSTREAM_COMMIT`);
* it loads the external OCPE domain package ``ocpe/packages/disease-models``
  with :func:`ocpe.load` (bundled core vocabulary included);
* it strictly validates the loaded registry with :func:`ocpe.validate` —
  any error, and (in strict mode, the default) any warning, raises
  :class:`OCPERegistryError`;
* it exposes the registered quantities, the declarative model and
  :func:`ocpe.validate_observation` for observation records.

Only stable, generic OCPE APIs are used; nothing here depends on other
modules of ``ocpe_disease_models``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ocpe.loader import EntityRecord, Registry, Report

import ocpe

# Pinned upstream Open Computational Physiology Engine commit
# (open-computational-physiology-engine @ 3f04b6f). The installed ``ocpe``
# 0.1.0 engine and its bundled specification must come from this commit.
UPSTREAM_REPOSITORY = (
    "https://github.com/invisible-illness-project/open-computational-physiology-engine"
)
UPSTREAM_COMMIT = "3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d"

# Identity of the external OCPE domain package shipped by this repository.
PACKAGE_ID = "disease-models"
PACKAGE_VERSION = "0.2.0"

# The declarative shared four-compartment cardiovascular/autonomic ODE model.
MODEL_CURIE = "ocpe:disease-models/shared-physiology"

# OCPE specification version implemented by the pinned engine (e.g. "0.1.0").
OCPE_SPEC_VERSION = ocpe.spec_version()

PathLike = str | os.PathLike


class OCPEAdapterError(RuntimeError):
    """Base error raised by the OCPE adapter."""


class OCPERegistryError(OCPEAdapterError):
    """Raised when the OCPE package fails to load or to validate."""

    def __init__(self, message: str, report: Report | None = None) -> None:
        self.report = report
        if report is not None:
            details = "\n".join(str(issue) for issue in report.issues)
            if details:
                message = f"{message}\n{details}"
        super().__init__(message)


def default_package_dir() -> Path:
    """Directory of the bundled ``ocpe/packages/disease-models`` package."""
    return Path(__file__).resolve().parents[4] / "ocpe" / "packages" / PACKAGE_ID


class DiseaseModelsOCPEAdapter:
    """Loads and strictly validates the disease-models OCPE package.

    Parameters
    ----------
    package_dir:
        Directory containing the external package's ``package.yaml``
        (default: the repository's ``ocpe/packages/disease-models``).
    strict:
        Treat validation warnings as failures (default ``True``).
    """

    def __init__(
        self,
        package_dir: PathLike | None = None,
        *,
        strict: bool = True,
    ) -> None:
        self.package_dir = Path(package_dir) if package_dir is not None else default_package_dir()
        if not (self.package_dir / "package.yaml").is_file():
            raise OCPERegistryError(f"no package.yaml in {self.package_dir}")
        self.strict = strict
        self.registry: Registry = ocpe.load([self.package_dir], include_core=True)
        self.report: Report = ocpe.validate(self.registry)
        self._enforce_valid()

    # ------------------------------------------------------------------ load
    def _enforce_valid(self) -> None:
        if not self.report.ok:
            raise OCPERegistryError(
                f"OCPE package {PACKAGE_ID!r} failed validation "
                f"({len(self.report.errors)} error(s))",
                self.report,
            )
        if self.strict and self.report.warnings:
            raise OCPERegistryError(
                f"OCPE package {PACKAGE_ID!r} has {len(self.report.warnings)} "
                "validation warning(s) (strict mode)",
                self.report,
            )
        if PACKAGE_ID not in self.registry.packages:
            raise OCPERegistryError(
                f"package {PACKAGE_ID!r} not present in the loaded registry"
            )

    # --------------------------------------------------------------- queries
    @property
    def package(self):
        """The loaded :class:`ocpe.loader.Package` record."""
        return self.registry.packages[PACKAGE_ID]

    def get(self, curie: str) -> EntityRecord:
        """Resolve an entity CURIE, raising ``KeyError`` if unregistered."""
        ent = self.registry.get(curie)
        if ent is None:
            raise KeyError(f"no OCPE entity registered as {curie!r}")
        return ent

    def quantities(self) -> list[EntityRecord]:
        """All registered quantity entities (variables, latent constructs,
        derived metrics) of the disease-models package."""
        out = []
        for kind in ("variable", "latent_construct", "derived_metric"):
            out.extend(
                e for e in self.registry.by_kind(kind) if e.package == PACKAGE_ID
            )
        return out

    def model(self, curie: str = MODEL_CURIE) -> EntityRecord:
        """The declarative four-compartment shared physiological model."""
        ent = self.get(curie)
        if ent.kind != "model":
            raise OCPEAdapterError(f"{curie} is a {ent.kind}, not a model")
        return ent

    def output_quantities(self, curie: str = MODEL_CURIE) -> dict[str, str]:
        """Map of model output symbol -> represented quantity CURIE."""
        model = self.model(curie)
        return {
            s["symbol"]: s["represents"]
            for s in model.data.get("symbols", [])
            if s.get("role") == "output" and s.get("represents")
        }

    # ----------------------------------------------------------- observations
    def validate_observation(self, record: dict[str, Any]) -> Report:
        """Validate an observation record against this registry.

        Uses :func:`ocpe.validate_observation`; the returned report is *not*
        raised as an exception so callers can inspect issues. Use
        :func:`assert_observation_valid` for the strict form.
        """
        return ocpe.validate_observation(record, self.registry)

    def assert_observation_valid(self, record: dict[str, Any]) -> Report:
        """Validate an observation record, raising on any error (and, in
        strict mode, any warning)."""
        report = self.validate_observation(record)
        if not report.ok or (self.strict and report.warnings):
            raise OCPERegistryError(
                f"invalid OCPE observation for {record.get('quantity')!r}", report
            )
        return report

    def summary(self) -> dict[str, Any]:
        """Registry summary plus adapter pins, for diagnostics."""
        out = dict(self.registry.summary())
        out["upstream_commit"] = UPSTREAM_COMMIT
        out["ocpe_spec_version"] = OCPE_SPEC_VERSION
        out["package_dir"] = str(self.package_dir)
        return out


def load_adapter(
    package_dir: PathLike | None = None,
    *,
    strict: bool = True,
) -> DiseaseModelsOCPEAdapter:
    """Load and strictly validate the disease-models OCPE package."""
    return DiseaseModelsOCPEAdapter(package_dir, strict=strict)
