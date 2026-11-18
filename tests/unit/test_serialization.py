"""VAL-SW-SERIALIZATION: serialization and numerical failure behavior (software).

Registry expectations:
- Small traces and metadata serialize reproducibly.
- Saved parameters/protocol/configuration hash match the in-memory run.
- Required metadata and arrays are present.
- Non-finite or failed solver output cannot be reported as success.
- Invalid parameter domains raise explicit errors.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

import numpy as np
import pytest

from ocpe_disease_models.models.shared.model import (
    ComputationalPatient,
    ModelParameters,
    ProtocolSegment,
)

pytestmark = pytest.mark.software

REQUIRED_METADATA_KEYS = {
    "model",
    "model_version",
    "phenotype_id",
    "configuration_sha256",
    "ocpe_commit",
    "python_version",
    "numpy_version",
    "scipy_version",
    "solver",
    "scientific_status",
}

EXPECTED_OUTPUT_NAMES = {
    "heart_rate",
    "arterial_pressure",
    "mean_arterial_pressure",
    "heart_level_mean_arterial_pressure",
    "central_venous_pressure",
    "splanchnic_venous_pressure",
    "lower_limb_venous_pressure",
    "other_systemic_venous_pressure",
    "aortic_baroreceptor_pressure",
    "carotid_sinus_pressure",
    "brain_arterial_pressure",
    "integrated_baroreflex_input",
    "baroreflex_target",
    "cerebral_outflow_pressure",
    "cerebral_perfusion_pressure",
    "end_tidal_co2_mmHg",
    "cerebral_co2_factor",
    "cerebral_impairment_factor",
    "tilt_angle_deg",
    "upright",
    "stroke_volume",
    "cardiac_output_l_min",
    "other_systemic_arterial_flow",
    "other_systemic_venous_return",
    "other_systemic_arterial_resistance_effective",
    "other_systemic_venous_volume",
    "venous_return",
    "systemic_resistance_effective",
    "metabolic_capacity",
    "oxygen_extraction",
    "functional_capacity",
    "cerebral_flow_target",
    "cerebral_flow_index",
    "pem_severity",
    "exertional_load",
    "delayed_stress",
    "sympathetic_state",
}

# The ambiguous heart-level "baroreflex_pressure" output was removed in Stage 1.1.
REMOVED_OUTPUT_NAMES = {"baroreflex_pressure"}


def _small_result():
    patient = ComputationalPatient(phenotype_id="serialization-check")
    protocol = [ProtocolSegment(start=0.0, end=60.0, label="rest")]
    return patient.simulate(protocol, sample_interval=2.0)


def _config_hash(parameters, protocol) -> str:
    payload = {
        "parameters": asdict(parameters),
        "protocol": [asdict(s) for s in protocol],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


# ----------------------------------------------------------------- round trip
def test_saved_artifacts_match_in_memory_run(tmp_path):
    result = _small_result()
    result.save(tmp_path)

    payload = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert payload["parameters"] == asdict(result.parameters)
    assert payload["protocol"] == [asdict(s) for s in result.protocol]
    assert payload["metadata"]["configuration_sha256"] == _config_hash(
        result.parameters, result.protocol
    )
    assert payload["summary"] == result.summary()

    trace = np.load(tmp_path / "trace.npz")
    np.testing.assert_array_equal(trace["time"], result.time)
    np.testing.assert_array_equal(trace["states"], result.states)
    for name, values in result.outputs.items():
        np.testing.assert_array_equal(trace[name], values)


def test_required_metadata_and_arrays_present(tmp_path):
    result = _small_result()
    result.save(tmp_path)
    payload = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert REQUIRED_METADATA_KEYS <= set(payload["metadata"])
    assert payload["metadata"]["solver"]["method"] == "DOP853"
    assert payload["metadata"]["solver"]["sample_interval"] == 2.0
    assert payload["metadata"]["solver"]["seed"] == 0
    assert "not clinically validated" in payload["metadata"]["scientific_status"]

    trace = np.load(tmp_path / "trace.npz")
    assert EXPECTED_OUTPUT_NAMES <= set(trace.files)
    assert REMOVED_OUTPUT_NAMES.isdisjoint(trace.files)
    assert trace["states"].shape == (
        len(payload["state_names"]),
        trace["time"].shape[0],
    )
    assert payload["metadata"]["model_version"] == "0.4.0"
    assert len(payload["state_names"]) == 12
    for name in trace.files:
        assert np.all(np.isfinite(trace[name])), f"non-finite values in {name}"


def test_serialization_is_reproducible(tmp_path):
    first = _small_result()
    second = _small_result()
    assert first.metadata["configuration_sha256"] == second.metadata["configuration_sha256"]
    first.save(tmp_path / "a")
    second.save(tmp_path / "b")
    assert (tmp_path / "a" / "result.json").read_bytes() == (
        tmp_path / "b" / "result.json"
    ).read_bytes()
    np.testing.assert_array_equal(
        np.load(tmp_path / "a" / "trace.npz")["states"],
        np.load(tmp_path / "b" / "trace.npz")["states"],
    )


# ------------------------------------------------------ numerical failure modes
def test_non_finite_solver_output_cannot_be_reported_as_success(monkeypatch):
    """If the solver returns non-finite states, simulate() must fail loudly."""
    from ocpe_disease_models.models.shared import model as model_module

    class NonFiniteSolution:
        success = True  # a "successful" solver result must still be rejected
        message = "forced non-finite states for validation"
        t = np.array([0.0, 1.0])
        y = np.array([[0.0, np.inf]] * 12)

    monkeypatch.setattr(model_module, "solve_ivp", lambda *a, **k: NonFiniteSolution())
    patient = ComputationalPatient(phenotype_id="nan-check")
    with pytest.raises(RuntimeError, match="non-finite"):
        patient.simulate([ProtocolSegment(start=0.0, end=10.0)])


def test_failed_solver_cannot_be_reported_as_success(monkeypatch):
    import scipy.integrate

    from ocpe_disease_models.models.shared import model as model_module

    class FailedSolution:
        success = False
        message = "forced failure for validation"
        t = np.array([0.0])
        y = np.zeros((12, 1))

    monkeypatch.setattr(
        model_module, "solve_ivp", lambda *a, **k: FailedSolution()
    )
    patient = ComputationalPatient(phenotype_id="solver-failure-check")
    with pytest.raises(RuntimeError, match="Simulation failed"):
        patient.simulate([ProtocolSegment(start=0.0, end=10.0)])
    assert scipy.integrate.solve_ivp is not None  # module import untouched elsewhere


@pytest.mark.parametrize(
    ("override", "match"),
    [
        ({"arterial_compliance": 0.0}, "arterial_compliance must be positive"),
        ({"lower_limb_venous_compliance": -1.0}, "lower_limb_venous_compliance must be positive"),
        ({"splanchnic_arterial_resistance": -0.5}, "splanchnic_arterial_resistance must be positive"),
        ({"blood_volume_factor": 0.0}, "blood_volume_factor must be positive"),
        ({"oxygen_extraction_fraction": 1.0}, "oxygen_extraction_fraction"),
        ({"oxygen_extraction_fraction": 0.0}, "oxygen_extraction_fraction"),
        ({"pem_recovery_time_constant": -3.0}, "pem_recovery_time_constant must be positive"),
    ],
)
def test_invalid_parameter_domains_raise_explicit_errors(override, match):
    with pytest.raises(ValueError, match=match):
        ComputationalPatient(ModelParameters().replaced(override))


# ----------------------------------------------------------- protocol validity
@pytest.mark.parametrize(
    "protocol",
    [
        [ProtocolSegment(start=1.0, end=10.0)],  # must start at t=0
        [ProtocolSegment(start=0.0, end=10.0), ProtocolSegment(start=5.0, end=12.0)],  # overlap
        [ProtocolSegment(start=0.0, end=10.0, upright=1.5)],  # input outside [0, 1]
        [ProtocolSegment(start=0.0, end=10.0, exertion=-0.1)],
        # Stage 1.1 posture semantics
        [ProtocolSegment(start=0.0, end=10.0, upright=0.5, tilt_angle_deg=30.0)],  # ambiguous
        [ProtocolSegment(start=0.0, end=10.0, tilt_angle_deg=120.0)],  # outside [0, 90]
        [ProtocolSegment(start=0.0, end=10.0, tilt_angle_deg=-5.0)],
        [ProtocolSegment(start=0.0, end=10.0, transition_duration=-1.0)],
        [ProtocolSegment(start=0.0, end=10.0, transition_duration=20.0)],  # exceeds segment
        # ETCO₂ must be finite and positive when declared.
        [ProtocolSegment(start=0.0, end=10.0, end_tidal_co2_mmHg=0.0)],
        [ProtocolSegment(start=0.0, end=10.0, end_tidal_co2_mmHg=-1.0)],
        [ProtocolSegment(start=0.0, end=10.0, end_tidal_co2_mmHg=float("nan"))],
        [ProtocolSegment(start=0.0, end=10.0, end_tidal_co2_mmHg=float("inf"))],
        [ProtocolSegment(start=0.0, end=10.0, end_tidal_co2_mmHg=float("-inf"))],
    ],
)
def test_invalid_protocols_fail_explicitly(protocol):
    patient = ComputationalPatient(phenotype_id="protocol-check")
    with pytest.raises(ValueError):
        patient.simulate(protocol)
