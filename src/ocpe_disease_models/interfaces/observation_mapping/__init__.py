"""Mapping from simulated disease-model outputs to OCPE observation records.

Each simulated output (heart rate, mean arterial pressure, stroke volume,
cardiac output, cerebral flow index, metabolic capacity, PEM severity) is
mapped to an OCPE 0.1 observation record with an explicit UCUM unit,
``value_kind: simulated``, the declaring model CURIE and provenance, and is
validated with :func:`ocpe.validate_observation` against the registered
quantities of the external ``disease-models`` package.
"""

from .mapping import (
    MODEL_CURIE,
    QUANTITY_SPECS,
    SIMULATED_VALUE_KIND,
    SIMULATOR_OUTPUT_ALIASES,
    ObservationSpec,
    OCPEObservationError,
    build_observation,
    get_spec,
    map_simulation_outputs,
    validate_observation_record,
)

__all__ = [
    "MODEL_CURIE",
    "QUANTITY_SPECS",
    "SIMULATED_VALUE_KIND",
    "SIMULATOR_OUTPUT_ALIASES",
    "OCPEObservationError",
    "ObservationSpec",
    "build_observation",
    "get_spec",
    "map_simulation_outputs",
    "validate_observation_record",
]
