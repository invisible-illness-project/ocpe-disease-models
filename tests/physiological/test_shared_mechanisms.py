"""VAL-PHYS-SHARED: regional pump, autonomic, and cerebral mechanisms."""

from __future__ import annotations

import math

import numpy as np
import pytest
from conftest import run_phenotype, stressed_volume_drift

from ocpe_disease_models.config import load_protocol
from ocpe_disease_models.models.shared import ComputationalPatient, ModelParameters
from ocpe_disease_models.models.shared.model import (
    HYDROSTATIC_MMHG_PER_CM,
    STATE_NAMES,
    ProtocolSegment,
)

pytestmark = pytest.mark.physiological

CENTRAL = STATE_NAMES.index("central_venous_volume")
SPLANCHNIC = STATE_NAMES.index("splanchnic_venous_volume")
LOWER_LIMB = STATE_NAMES.index("lower_limb_venous_volume")
OTHER = STATE_NAMES.index("other_systemic_venous_volume")
CARDIAC_SYM = STATE_NAMES.index("cardiac_sympathetic_state")
VASCULAR_SYM = STATE_NAMES.index("vascular_sympathetic_state")
VAGAL = STATE_NAMES.index("vagal_state")
CEREBRAL = STATE_NAMES.index("cerebral_flow_index")
ARTERIAL = STATE_NAMES.index("arterial_volume")


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
    assert rhs_active[CENTRAL] - rhs_inactive[CENTRAL] == pytest.approx(pump)
    assert rhs_active[LOWER_LIMB] - rhs_inactive[LOWER_LIMB] == pytest.approx(-pump)
    assert rhs_active[: OTHER + 1].sum() == pytest.approx(0.0, abs=1e-12)
    assert active["heart_rate"] == inactive["heart_rate"]


def test_sustained_contraction_impedes_passive_lower_limb_return():
    patient = ComputationalPatient()
    state = patient.initial_state()
    # Use a positive passive upright gradient so resistance, not the flow floor,
    # determines the comparison. The increment exceeds the Stage 1.3 dependent
    # hydrostatic column plus the nonlinear venous-pressure contribution.
    state[LOWER_LIMB] += 500.0
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
    assert (
        active.states[LOWER_LIMB, active_late].mean()
        < inactive.states[LOWER_LIMB, inactive_late].mean()
    )
    assert (
        active.states[CENTRAL, active_late].mean()
        > inactive.states[CENTRAL, inactive_late].mean()
    )


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
    cardiac_state[CARDIAC_SYM] = 0.7
    cardiac = patient._derived(0.0, cardiac_state, protocol)
    vagal_state = patient.initial_state()
    vagal_state[VAGAL] = 0.3
    vagal = patient._derived(0.0, vagal_state, protocol)
    vascular_state = patient.initial_state()
    vascular_state[VASCULAR_SYM] = 0.7
    vascular = patient._derived(0.0, vascular_state, protocol)
    assert cardiac["heart_rate"] > baseline["heart_rate"]
    assert cardiac["stroke_volume"] > baseline["stroke_volume"]
    assert vagal["heart_rate"] > baseline["heart_rate"]
    assert vagal["stroke_volume"] == pytest.approx(baseline["stroke_volume"])
    assert vascular["heart_rate"] == pytest.approx(baseline["heart_rate"])
    for bed in ("splanchnic", "lower_limb", "other_systemic"):
        assert vascular[f"{bed}_arterial_resistance_effective"] > baseline[
            f"{bed}_arterial_resistance_effective"
        ]


def _expected_baroreflex_target(patient: ComputationalPatient, tilt_angle_deg: float) -> float:
    """Integrated aortic/carotid baroreflex target for the default initial state."""
    p = patient.parameters
    sin_tilt = math.sin(math.radians(tilt_angle_deg))
    pa = p.arterial_volume_initial / p.arterial_compliance
    p_aortic = max(0.0, pa - HYDROSTATIC_MMHG_PER_CM * p.aortic_baroreceptor_height_cm * sin_tilt)
    p_carotid = max(
        0.0, pa - HYDROSTATIC_MMHG_PER_CM * p.carotid_baroreceptor_height_cm * sin_tilt
    )
    error = (
        p.aortic_baroreflex_weight
        * (p.aortic_baroreflex_pressure_setpoint - p_aortic)
        / p.aortic_baroreflex_pressure_scale
        + p.carotid_baroreflex_weight
        * (p.carotid_baroreflex_pressure_setpoint - p_carotid)
        / p.carotid_baroreflex_pressure_scale
    )
    return 1.0 / (1.0 + math.exp(-float(np.clip(error, -40.0, 40.0))))


def test_vagal_state_responds_faster_than_cardiac_sympathetic_state():
    patient = ComputationalPatient()
    protocol, _ = load_protocol("head-up-tilt")
    state = patient.initial_state()
    # After the 30 s transition completes the tilt is a steady 70 degrees.
    derivative = patient.rhs(160.0, state, protocol)
    target = _expected_baroreflex_target(patient, 70.0)
    assert target > 0.9  # the 70 degree tilt is a strong baroreflex stimulus
    assert derivative[CARDIAC_SYM] == pytest.approx(
        (target - 0.5) / patient.parameters.cardiac_sympathetic_time_constant
    )
    assert derivative[VASCULAR_SYM] == pytest.approx(
        (target - 0.5) / patient.parameters.vascular_sympathetic_time_constant
    )
    assert derivative[VAGAL] == pytest.approx(
        (1.0 - target - 0.5) / patient.parameters.vagal_time_constant
    )


def test_cerebral_proxy_uses_brain_pressure_and_obeys_curve_invariants():
    patient = ComputationalPatient()
    state = patient.initial_state()
    p = patient.parameters
    upright = _protocol(upright=1.0)
    brain_column = HYDROSTATIC_MMHG_PER_CM * p.brain_hydrostatic_height_cm
    outflow = p.cerebral_outflow_pressure_mmHg
    # CPP uses the fixed effective outflow pressure, not thoracic CVP.
    state[CENTRAL] *= 1.5  # raise central venous pressure
    derived = patient._derived(0.0, state, upright)
    assert derived["central_venous_pressure"] > outflow
    assert derived["cerebral_perfusion_pressure"] == pytest.approx(
        max(0.0, derived["brain_arterial_pressure"] - outflow)
    )
    # Zero CPP gives zero target despite nonzero systemic arterial pressure.
    state = patient.initial_state()
    state[ARTERIAL] = p.arterial_compliance * (brain_column + outflow)
    derived = patient._derived(0.0, state, upright)
    assert derived["brain_arterial_pressure"] == pytest.approx(
        derived["arterial_pressure"] - brain_column
    )
    assert derived["cerebral_perfusion_pressure"] == 0.0
    assert derived["cerebral_pressure_target"] == 0.0
    # CPP at the reference pressure maps exactly to one.
    state = patient.initial_state()
    state[ARTERIAL] = p.arterial_compliance * (
        brain_column + outflow + p.cerebral_reference_perfusion_pressure
    )
    assert patient._derived(0.0, state, upright)["cerebral_pressure_target"] == pytest.approx(1.0)
    # The bounded high-pressure asymptote is 1/(1-s), not an unbounded index.
    state[ARTERIAL] *= 20.0
    high = patient._derived(0.0, state, upright)["cerebral_pressure_target"]
    assert 1.0 < high < 1.0 / (1.0 - p.cerebral_autoregulation_residual_slope)


def test_invalid_or_nonfinite_states_fail_explicitly():
    patient = ComputationalPatient()
    state = patient.initial_state()
    state[ARTERIAL] = np.nan
    with pytest.raises(FloatingPointError, match="Non-finite"):
        patient.rhs(0.0, state, _protocol())


def test_cerebral_index_remains_within_declared_bounds():
    p = ModelParameters()
    upper_bound = (1.0 / (1.0 - p.cerebral_autoregulation_residual_slope)) * math.exp(
        p.cerebral_co2_reactivity_per_mmHg * p.cerebral_co2_extrapolation_limit_mmHg
    )
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
        assert cfi.max() <= upper_bound + 1e-9
        assert cpp.min() >= 0.0
        assert np.allclose(
            cpp,
            np.maximum(
                0.0,
                result.outputs["brain_arterial_pressure"]
                - result.outputs["cerebral_outflow_pressure"],
            ),
            atol=1e-10,
        )


def test_parameter_bounds_reject_nonpositive_or_unbounded_mechanisms():
    for name in (
        "splanchnic_venous_compliance",
        "lower_limb_arterial_resistance",
        "other_systemic_arterial_resistance",
        "other_systemic_venous_compliance",
        "muscle_pump_half_volume",
        "cerebral_reference_perfusion_pressure",
        "end_tidal_co2_reference_mmHg",
        "cerebral_co2_extrapolation_limit_mmHg",
    ):
        with pytest.raises(ValueError, match="must be positive"):
            ComputationalPatient(ModelParameters().replaced({name: 0.0}))
    with pytest.raises(ValueError, match="below 2"):
        ComputationalPatient(ModelParameters().replaced({"lower_limb_resistance_sympathetic_gain": 2.0}))
    with pytest.raises(ValueError, match="below 2"):
        ComputationalPatient(
            ModelParameters().replaced({"other_systemic_resistance_sympathetic_gain": 2.0})
        )
    with pytest.raises(ValueError, match="residual_slope"):
        ComputationalPatient(ModelParameters().replaced({"cerebral_autoregulation_residual_slope": 0.0}))
    # Baroreflex weights must be nonnegative and sum to one.
    with pytest.raises(ValueError, match="sum to 1"):
        ComputationalPatient(ModelParameters().replaced({"aortic_baroreflex_weight": 0.5}))
    with pytest.raises(ValueError, match="must be nonnegative"):
        ComputationalPatient(ModelParameters().replaced({"carotid_baroreflex_weight": -0.1}))
    # Hydrostatic heights, the fixed cerebral outflow pressure, and the CO2
    # reactivity must be nonnegative.
    for name in (
        "splanchnic_hydrostatic_height_cm",
        "lower_limb_hydrostatic_height_cm",
        "other_systemic_hydrostatic_height_cm",
        "aortic_baroreceptor_height_cm",
        "carotid_baroreceptor_height_cm",
        "brain_hydrostatic_height_cm",
        "cerebral_outflow_pressure_mmHg",
        "cerebral_co2_reactivity_per_mmHg",
    ):
        with pytest.raises(ValueError, match="must be nonnegative"):
            ComputationalPatient(ModelParameters().replaced({name: -1.0}))
