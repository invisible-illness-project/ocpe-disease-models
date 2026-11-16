"""Integration test: real simulation -> OCPE observation mapping -> strict validation.

Runs a small :class:`ComputationalPatient` simulation and maps the seven
registered simulated outputs of the resulting ``SimulationResult.outputs``
(including the simulator-native ``cardiac_output_l_min`` name, in L/min) to
OCPE observation records, each strictly validated against the external
``disease-models`` package (errors *and* warnings fail).
"""
# ruff: noqa: E402  (sys.path bootstrap for the src layout precedes imports)

import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.software

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocpe_disease_models.interfaces.observation_mapping import (  # noqa: E402
    map_simulation_outputs,
    validate_observation_record,
)
from ocpe_disease_models.interfaces.ocpe_adapter import load_adapter  # noqa: E402
from ocpe_disease_models.models.shared import ComputationalPatient  # noqa: E402
from ocpe_disease_models.models.shared.model import ProtocolSegment  # noqa: E402

# The seven mapped quantities, keyed by their SimulationResult.outputs names.
MAPPED_OUTPUT_NAMES = (
    "heart_rate",
    "mean_arterial_pressure",
    "stroke_volume",
    "cardiac_output_l_min",  # L/min; aliased to the cardiac-output mapping entry
    "cerebral_flow_index",
    "metabolic_capacity",
    "pem_severity",
)

EXPECTED_CURIES = {
    "heart_rate": "ocpe:disease-models/heart-rate",
    "mean_arterial_pressure": "ocpe:disease-models/mean-arterial-pressure",
    "stroke_volume": "ocpe:disease-models/stroke-volume",
    "cardiac_output_l_min": "ocpe:disease-models/cardiac-output",
    "cerebral_flow_index": "ocpe:disease-models/cerebral-flow-index",
    "metabolic_capacity": "ocpe:disease-models/metabolic-capacity",
    "pem_severity": "ocpe:disease-models/pem-severity",
}


def _small_simulation():
    """A short resting simulation of the healthy reference patient."""
    patient = ComputationalPatient()  # healthy-reference defaults
    protocol = [ProtocolSegment(start=0.0, end=120.0, label="rest")]
    return patient.simulate(protocol, sample_interval=2.0)


def test_simulation_outputs_map_to_strictly_valid_observations():
    result = _small_simulation()
    for name in MAPPED_OUTPUT_NAMES:
        assert name in result.outputs, f"missing simulator output {name!r}"

    final_outputs = {
        name: float(result.outputs[name][-1]) for name in MAPPED_OUTPUT_NAMES
    }
    adapter = load_adapter()  # strict: errors and warnings fail
    records = map_simulation_outputs(
        final_outputs,
        adapter=adapter,
        subject=result.phenotype_id,
        observation_id=f"{result.phenotype_id}-final",
    )

    assert set(records) == set(MAPPED_OUTPUT_NAMES)
    for name, record in records.items():
        assert record["quantity"] == EXPECTED_CURIES[name]
        assert record["value"] == final_outputs[name]
        assert record["value_kind"] == "simulated"
        assert record["subject"] == result.phenotype_id
        validate_observation_record(record, adapter)
        adapter.assert_observation_valid(record)  # strict engine-level check

    # The simulator exposes cardiac output in L/min under cardiac_output_l_min;
    # the mapped record must carry the same value with an explicit L/min unit.
    co = records["cardiac_output_l_min"]
    assert co["unit"] == "L/min"
    assert 3.0 < co["value"] < 8.0  # plausible resting healthy cardiac output
