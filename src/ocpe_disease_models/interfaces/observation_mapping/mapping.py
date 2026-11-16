"""Mapping from simulated disease-model outputs to OCPE 0.1 observation records.

The mapping is purely semantic: numerical values are produced elsewhere (the
disease-model simulators); this module wraps each value in a validated OCPE
observation exchange record with an explicit UCUM unit,
``value_kind: "simulated"``, the declaring model CURIE, and provenance tying
the record to the pinned upstream OCPE engine commit.

Records are validated with :func:`ocpe.validate_observation` against the
quantities registered in the external ``ocpe/packages/disease-models``
package (loaded via
:class:`~ocpe_disease_models.interfaces.ocpe_adapter.DiseaseModelsOCPEAdapter`).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import ocpe

from ..ocpe_adapter import (
    MODEL_CURIE,
    UPSTREAM_COMMIT,
    DiseaseModelsOCPEAdapter,
    load_adapter,
)

# All records produced by this mapping are model outputs, never measurements.
SIMULATED_VALUE_KIND = "simulated"

# Provenance block attached to every produced observation record.
SIMULATION_PROVENANCE: dict[str, Any] = {
    "derived_from": [
        {
            "source": "ocpe/packages/disease-models/models.yaml",
            "legacy_id": MODEL_CURIE,
            "transformation": (
                "Numerical simulation of the declarative OCPE model; "
                f"OCPE engine pinned at upstream commit {UPSTREAM_COMMIT}."
            ),
        }
    ],
    "contributors": [
        {
            "name": "ocpe-disease-models simulator",
            "kind": "tool",
            "role": "value generation",
        }
    ],
    "notes": "Simulated value; not a physiological measurement.",
}


@dataclass(frozen=True)
class ObservationSpec:
    """Semantic mapping entry for one simulated disease-model output."""

    name: str  # simulator-side output name (e.g. "heart_rate")
    curie: str  # registered OCPE quantity CURIE
    unit: str  # explicit UCUM unit of the mapped record
    symbol: str  # declaring output symbol of the model
    label: str  # human-readable quantity label


# The seven simulated disease-model outputs covered by this mapping.
QUANTITY_SPECS: dict[str, ObservationSpec] = {
    "heart_rate": ObservationSpec(
        name="heart_rate",
        curie="ocpe:disease-models/heart-rate",
        unit="/min",
        symbol="HR",
        label="Heart rate",
    ),
    "mean_arterial_pressure": ObservationSpec(
        name="mean_arterial_pressure",
        curie="ocpe:disease-models/mean-arterial-pressure",
        unit="mm[Hg]",
        symbol="MAP",
        label="Mean arterial pressure",
    ),
    "stroke_volume": ObservationSpec(
        name="stroke_volume",
        curie="ocpe:disease-models/stroke-volume",
        unit="mL",
        symbol="SV",
        label="Stroke volume",
    ),
    "cardiac_output": ObservationSpec(
        name="cardiac_output",
        curie="ocpe:disease-models/cardiac-output",
        unit="L/min",
        symbol="CO",
        label="Cardiac output",
    ),
    "cerebral_flow_index": ObservationSpec(
        name="cerebral_flow_index",
        curie="ocpe:disease-models/cerebral-flow-index",
        unit="1",
        symbol="CFI",
        label="Cerebral flow index",
    ),
    "metabolic_capacity": ObservationSpec(
        name="metabolic_capacity",
        curie="ocpe:disease-models/metabolic-capacity",
        unit="1",
        symbol="MC",
        label="Metabolic capacity",
    ),
    "pem_severity": ObservationSpec(
        name="pem_severity",
        curie="ocpe:disease-models/pem-severity",
        unit="1",
        symbol="PEM",
        label="Post-exertional malaise severity",
    ),
}


# ``SimulationResult.outputs`` exposes cardiac output under the simulator-native
# name ``cardiac_output_l_min`` (already in L/min), whereas the mapping entry is
# keyed by the OCPE model output name ``cardiac_output`` whose explicit UCUM
# unit is also ``L/min``. The alias is therefore a pure name adaptation; no
# unit conversion is applied (and none is needed).
SIMULATOR_OUTPUT_ALIASES: dict[str, str] = {
    "cardiac_output_l_min": "cardiac_output",
}


class OCPEObservationError(ValueError):
    """Raised when a mapped observation record fails OCPE validation."""

    def __init__(self, message: str, report=None) -> None:
        self.report = report
        if report is not None:
            details = "\n".join(str(issue) for issue in report.issues)
            if details:
                message = f"{message}\n{details}"
        super().__init__(message)


def get_spec(name: str) -> ObservationSpec:
    """Return the mapping entry for a simulator output name.

    Simulator-native names listed in :data:`SIMULATOR_OUTPUT_ALIASES` (e.g.
    ``cardiac_output_l_min`` from ``SimulationResult.outputs``) are resolved
    to their canonical mapping entry.
    """
    canonical = SIMULATOR_OUTPUT_ALIASES.get(name, name)
    try:
        return QUANTITY_SPECS[canonical]
    except KeyError:
        raise KeyError(
            f"unknown simulated quantity {name!r}; "
            f"expected one of {sorted(QUANTITY_SPECS)} "
            f"or an alias in {sorted(SIMULATOR_OUTPUT_ALIASES)}"
        ) from None


def build_observation(
    name: str,
    value: float,
    *,
    time: str | None = None,
    uncertainty: float | None = None,
    uncertainty_type: str | None = None,
    subject: str | None = None,
    observation_id: str | None = None,
    model: str = MODEL_CURIE,
    provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an OCPE observation record for one simulated output.

    The record carries an explicit UCUM unit, ``value_kind: "simulated"``,
    the declaring model CURIE and simulation provenance. Validation is the
    caller's choice via :func:`validate_observation_record` (or
    :func:`map_simulation_outputs`, which validates by default).
    """
    spec = get_spec(name)
    record: dict[str, Any] = {
        "quantity": spec.curie,
        "value": value,
        "unit": spec.unit,
        "value_kind": SIMULATED_VALUE_KIND,
        "model": model,
        "provenance": dict(provenance) if provenance is not None else dict(SIMULATION_PROVENANCE),
    }
    if observation_id is not None:
        record["observation_id"] = observation_id
    if time is not None:
        record["time"] = time
    if uncertainty is not None:
        record["uncertainty"] = uncertainty
        record["uncertainty_type"] = uncertainty_type or "unspecified"
    if subject is not None:
        record["subject"] = subject
    return record


def validate_observation_record(
    record: Mapping[str, Any],
    adapter: DiseaseModelsOCPEAdapter | None = None,
) -> None:
    """Validate a record with :func:`ocpe.validate_observation`.

    Raises :class:`OCPEObservationError` on any validation error or warning
    (the mapping guarantees registered quantities, known units and a
    model-accounted simulated value kind).
    """
    if adapter is None:
        adapter = load_adapter()
    report = ocpe.validate_observation(dict(record), adapter.registry)
    if not report.ok or report.warnings:
        raise OCPEObservationError(
            f"OCPE observation for {record.get('quantity')!r} failed validation",
            report,
        )


def map_simulation_outputs(
    outputs: Mapping[str, float],
    *,
    adapter: DiseaseModelsOCPEAdapter | None = None,
    validate: bool = True,
    **record_kwargs: Any,
) -> dict[str, dict[str, Any]]:
    """Map a dict of simulated outputs to validated OCPE observation records.

    ``outputs`` keys must be simulator output names registered in
    :data:`QUANTITY_SPECS` or aliases from :data:`SIMULATOR_OUTPUT_ALIASES`
    (e.g. ``cardiac_output_l_min`` as exposed by ``SimulationResult.outputs``).
    Returned records are keyed by the name given in ``outputs``. With
    ``validate=True`` (default) every record is
    checked with :func:`validate_observation_record` against the external
    package before being returned.
    """
    if adapter is None and validate:
        adapter = load_adapter()
    records: dict[str, dict[str, Any]] = {}
    for name, value in outputs.items():
        record = build_observation(name, value, **record_kwargs)
        if validate:
            validate_observation_record(record, adapter)
        records[name] = record
    return records
