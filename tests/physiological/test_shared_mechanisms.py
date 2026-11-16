"""VAL-PHYS-SHARED: regional pump, autonomic, and cerebral mechanisms."""

from __future__ import annotations

import numpy as np
import pytest
from conftest import run_phenotype, stressed_volume_drift

from ocpe_disease_models.config import load_protocol
from ocpe_disease_models.models.shared import ComputationalPatient, ModelParameters
from ocpe_disease_models.models.shared.model import ProtocolSegment

pytestmark = pytest.mark.physiological


def _protocol(**inputs: float) -> list[ProtocolSegment]:
    return [ProtocolSegment(start=0.0, end=600.0, **inputs)]


def test_rhythmic_pump_is_an_exact_compartmental_transfer():
    patient = ComputationalPatient()
    state = patient.initial_state()
    inactive = patient._derived(0.0, state, _protocol(upright=1.0))
    active = patient._derived(0.0, state, _protocol(upright=1.0, rhythmic_muscle_activity=1.0))
    pump = active["muscle_pump_flow"]
    assert pump > 0.0
    assert active["lower_limb_venous_return"] - inactive["lower_limb_venous_return"] == pytest.approx(pump)
    rhs_inactive = patient.rhs(0.0, state, _protocol(upright=1.0))
    rhs_active = patient.rhs(0.0, state, _protocol(upright=1.0, rhythmic_muscle_activity=1.0))
    assert rhs_active[1] - rhs_inactive[1] == pytest.approx(pump)
    assert rhs_active[3] - rhs_inactive[3] == pytest.approx(-pump)
    assert rhs_active[:4].sum() == pytest.approx(0.0, abs=1e-12)
    assert active["heart_rate"] == inactive["heart_rate"]


def test_sustained_contraction_impedes_passive_lower_limb_return():
    patient = ComputationalPatient()
    state = patient.initial_state()
    # Use a positive passive upright gradient so resistance, not the flow floor,
    # determines the comparison.
    state[3] += 200.0
    relaxed = patient._derived(0.0, state, _protocol(upright=1.0))
    contracted = patient._derived(
        0.0, state, _protocol(upright=1.0, sustained_muscle_contraction=1.0)
    )
    assert relaxed["lower_limb_venous_return"] > 0.0
    assert contracted["lower_limb_venous_resistance_effective"] == pytest.approx(
        4.0 * relaxed["lower_limb_venous_resistance_effective"]
    )
    assert contracted["lower_limb_venous_return"] < relaxed["lower_limb_venous_return"]
    assert contracted["muscle_pump_flow"] == 0.0


def test_rhythmic_activity_conserves_volume_and_redistributes_it():
    inactive = run_phenotype("healthy-reference", "inactive-standing")
    active = run_phenotype("healthy-reference", "light-rhythmic-activity")
    assert stressed_volume_drift(inactive) < 1e-6
    assert stressed_volume_drift(active) < 1e-6
    assert active.outputs["muscle_pump_flow"][active.time >= 120].min() > 0.0
    active_late = active.time >= 480
    inactive_late = inactive.time >= 480
    assert active.states[3, active_late].mean() < inactive.states[3, inactive_late].mean()
    assert active.states[1, active_late].mean() > inactive.states[1, inactive_late].mean()


def test_walking_and_sustained_protocols_conserve_volume():
    for protocol_id in ("walking", "sustained-contraction"):
        result = run_phenotype("healthy-reference", protocol_id)
        assert stressed_volume_drift(result) < 1e-6
        assert np.all(np.isfinite(result.states))


def test_cardiac_sympathetic_vagal_and_vascular_pathways_are_independent():
    patient = ComputationalPatient()
    protocol = _protocol()
    baseline = patient._derived(0.0, patient.initial_state(), protocol)
    cardiac_state = patient.initial_state()
    cardiac_state[4] = 0.7
    cardiac = patient._derived(0.0, cardiac_state, protocol)
    vagal_state = patient.initial_state()
    vagal_state[6] = 0.3
    vagal = patient._derived(0.0, vagal_state, protocol)
    vascular_state = patient.initial_state()
    vascular_state[5] = 0.7
    vascular = patient._derived(0.0, vascular_state, protocol)
    assert cardiac["heart_rate"] > baseline["heart_rate"]
    assert cardiac["stroke_volume"] > baseline["stroke_volume"]
    assert vagal["heart_rate"] > baseline["heart_rate"]
    assert vagal["stroke_volume"] == pytest.approx(baseline["stroke_volume"])
    assert vascular["heart_rate"] == pytest.approx(baseline["heart_rate"])
    assert vascular["splanchnic_arterial_resistance_effective"] > baseline[
        "splanchnic_arterial_resistance_effective"
    ]
    assert vascular["lower_limb_arterial_resistance_effective"] > baseline[
        "lower_limb_arterial_resistance_effective"
    ]


def test_vagal_state_responds_faster_than_cardiac_sympathetic_state():
    patient = ComputationalPatient()
    protocol, _ = load_protocol("head-up-tilt")
    state = patient.initial_state()
    derivative = patient.rhs(121.0, state, protocol)
    target = 1.0 / (1.0 + np.exp(-10.0))
    assert derivative[4] == pytest.approx(
        (target - 0.5) / patient.parameters.cardiac_sympathetic_time_constant
    )
    assert derivative[5] == pytest.approx(
        (target - 0.5) / patient.parameters.vascular_sympathetic_time_constant
    )
    assert derivative[6] == pytest.approx(
        (1.0 - target - 0.5) / patient.parameters.vagal_time_constant
    )


def test_cerebral_proxy_uses_head_pressure_and_obeys_curve_invariants():
    patient = ComputationalPatient()
    state = patient.initial_state()
    p = patient.parameters
    upright = _protocol(upright=1.0)
    # Zero CPP gives zero target despite nonzero systemic arterial pressure.
    state[0] = p.arterial_compliance * (
        p.head_hydrostatic_pressure_offset + state[1] / p.central_venous_compliance
    )
    derived = patient._derived(0.0, state, upright)
    assert derived["baroreflex_pressure"] == pytest.approx(
        derived["arterial_pressure"] - p.head_hydrostatic_pressure_offset
    )
    assert derived["cerebral_perfusion_pressure"] == 0.0
    assert derived["cerebral_pressure_target"] == 0.0
    # CPP at the reference pressure maps exactly to one.
    state = patient.initial_state()
    state[0] = p.arterial_compliance * (
        p.head_hydrostatic_pressure_offset
        + state[1] / p.central_venous_compliance
        + p.cerebral_reference_perfusion_pressure
    )
    assert patient._derived(0.0, state, upright)["cerebral_pressure_target"] == pytest.approx(1.0)
    # The bounded high-pressure asymptote is 1/(1-s), not an unbounded index.
    state[0] *= 20.0
    high = patient._derived(0.0, state, upright)["cerebral_pressure_target"]
    assert 1.0 < high < 1.25


def test_invalid_or_nonfinite_states_fail_explicitly():
    patient = ComputationalPatient()
    state = patient.initial_state()
    state[0] = np.nan
    with pytest.raises(FloatingPointError, match="Non-finite"):
        patient.rhs(0.0, state, _protocol())


def test_cerebral_index_remains_within_declared_bounds():
    for phenotype_id in (
        "healthy-reference",
        "pots-neuropathic",
        "pots-hyperadrenergic",
        "pots-hypovolemic",
        "pots-mixed",
        "eds-heds-vascular",
        "eds-heds-mecfs-comorbid",
        "mecfs-pem",
        "long-covid-autonomic",
        "long-covid-exertional",
    ):
        result = run_phenotype(phenotype_id, "head-up-tilt")
        cfi = result.outputs["cerebral_flow_index"]
        cpp = result.outputs["cerebral_perfusion_pressure"]
        assert cfi.min() >= 0.0
        assert cfi.max() <= 1.25
        assert cpp.min() >= 0.0
        assert np.allclose(
            cpp,
            np.maximum(
                0.0,
                result.outputs["baroreflex_pressure"]
                - result.outputs["central_venous_pressure"],
            ),
            atol=1e-10,
        )


def test_parameter_bounds_reject_nonpositive_or_unbounded_mechanisms():
    for name in (
        "splanchnic_venous_compliance",
        "lower_limb_arterial_resistance",
        "muscle_pump_half_volume",
        "cerebral_reference_perfusion_pressure",
    ):
        with pytest.raises(ValueError, match="must be positive"):
            ComputationalPatient(ModelParameters().replaced({name: 0.0}))
    with pytest.raises(ValueError, match="below 2"):
        ComputationalPatient(ModelParameters().replaced({"lower_limb_resistance_sympathetic_gain": 2.0}))
    with pytest.raises(ValueError, match="residual_slope"):
        ComputationalPatient(ModelParameters().replaced({"cerebral_autoregulation_residual_slope": 0.0}))
