"""VAL-PHYS-CBF-CO2: Stage 1.1 cerebral pressure/CO2 regulation (physiological).

Covers the separated aortic/carotid/brain hydrostatic pressures, the fixed
5 mmHg effective cerebral outflow pressure (explicitly not thoracic CVP or a
resolved ICP), explicit end-tidal CO2 forcing with bounded extrapolation, and
the persistent one-factor recovery protocols (pressure recovery with
persistent hypocapnia; CO2 recovery with persistent pressure reduction).
Protocols are constructed inline so these mechanisms are tested independently
of the simulation registry contents.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from ocpe_disease_models.models.shared import ComputationalPatient, ModelParameters
from ocpe_disease_models.models.shared.model import (
    HYDROSTATIC_MMHG_PER_CM,
    ProtocolSegment,
)

pytestmark = pytest.mark.physiological

TILT_START = 120.0
TILT_END = 600.0
RECOVERY_END = 1200.0
TRANSITION = 30.0


def _supine_then_tilt(angle_deg: float = 70.0, **kwargs) -> list[ProtocolSegment]:
    return [
        ProtocolSegment(start=0.0, end=TILT_START, tilt_angle_deg=0.0, label="supine"),
        ProtocolSegment(
            start=TILT_START,
            end=TILT_END,
            tilt_angle_deg=angle_deg,
            transition_duration=TRANSITION,
            label="tilt",
            **kwargs,
        ),
    ]


def _expected_co2_factor(etco2: float, p: ModelParameters) -> float:
    deviation = float(
        np.clip(
            etco2 - p.end_tidal_co2_reference_mmHg,
            -p.cerebral_co2_extrapolation_limit_mmHg,
            p.cerebral_co2_extrapolation_limit_mmHg,
        )
    )
    return math.exp(p.cerebral_co2_reactivity_per_mmHg * deviation)


# ------------------------------------------- pressure separation (Stage 1.1)
def test_aortic_carotid_and_brain_pressures_separate_with_tilt():
    patient = ComputationalPatient()
    p = patient.parameters
    state = patient.initial_state()
    protocol = _supine_then_tilt()
    supine = patient._inputs(0.0, protocol, p.end_tidal_co2_reference_mmHg)
    assert supine.tilt_angle_deg == 0.0
    d_supine = patient._derived(0.0, state, protocol)
    # Supine: no hydrostatic gradient, all measurement sites equal Pa.
    assert d_supine["aortic_baroreceptor_pressure"] == pytest.approx(
        d_supine["arterial_pressure"]
    )
    assert d_supine["carotid_sinus_pressure"] == pytest.approx(d_supine["arterial_pressure"])
    assert d_supine["brain_arterial_pressure"] == pytest.approx(d_supine["arterial_pressure"])
    # Tilted (steady 70 degrees): pressures separate by height above the heart.
    t_tilted = TILT_START + TRANSITION + 1.0
    d_tilted = patient._derived(t_tilted, state, protocol)
    sin70 = math.sin(math.radians(70.0))
    pa = d_tilted["arterial_pressure"]
    assert d_tilted["aortic_baroreceptor_pressure"] == pytest.approx(pa)  # heart level
    assert d_tilted["carotid_sinus_pressure"] == pytest.approx(
        pa - HYDROSTATIC_MMHG_PER_CM * p.carotid_baroreceptor_height_cm * sin70
    )
    assert d_tilted["brain_arterial_pressure"] == pytest.approx(
        pa - HYDROSTATIC_MMHG_PER_CM * p.brain_hydrostatic_height_cm * sin70
    )
    assert (
        d_tilted["aortic_baroreceptor_pressure"]
        > d_tilted["carotid_sinus_pressure"]
        > d_tilted["brain_arterial_pressure"]
    )


def test_integrated_baroreflex_input_combines_aortic_and_carotid_errors():
    patient = ComputationalPatient()
    p = patient.parameters
    state = patient.initial_state()
    protocol = _supine_then_tilt()
    d = patient._derived(TILT_START + TRANSITION + 1.0, state, protocol)
    e_a = (
        p.aortic_baroreflex_pressure_setpoint - d["aortic_baroreceptor_pressure"]
    ) / p.aortic_baroreflex_pressure_scale
    e_c = (
        p.carotid_baroreflex_pressure_setpoint - d["carotid_sinus_pressure"]
    ) / p.carotid_baroreflex_pressure_scale
    expected = p.aortic_baroreflex_weight * e_a + p.carotid_baroreflex_weight * e_c
    assert d["integrated_baroreflex_input"] == pytest.approx(expected, rel=1e-12)
    assert d["baroreflex_target"] == pytest.approx(
        1.0 / (1.0 + math.exp(-expected)), rel=1e-12
    )


def test_cpp_uses_fixed_outflow_pressure_not_central_venous_pressure():
    patient = ComputationalPatient()
    p = patient.parameters
    state = patient.initial_state()
    protocol = _supine_then_tilt()
    d = patient._derived(TILT_START + TRANSITION + 1.0, state, protocol)
    assert d["cerebral_outflow_pressure"] == p.cerebral_outflow_pressure_mmHg == 5.0
    assert d["cerebral_perfusion_pressure"] == pytest.approx(
        max(0.0, d["brain_arterial_pressure"] - d["cerebral_outflow_pressure"])
    )
    # Raising central venous pressure must not change CPP at fixed arterial state.
    raised = state.copy()
    raised[1] *= 1.5  # central_venous_volume
    d_raised = patient._derived(TILT_START + TRANSITION + 1.0, raised, protocol)
    assert d_raised["central_venous_pressure"] > d["central_venous_pressure"]
    assert d_raised["cerebral_perfusion_pressure"] == pytest.approx(
        d["cerebral_perfusion_pressure"]
    )


# ------------------------------------------------------------------- CO2 input
def test_absent_end_tidal_co2_means_model_reference():
    patient = ComputationalPatient()
    p = patient.parameters
    state = patient.initial_state()
    implicit = patient._derived(0.0, state, [ProtocolSegment(start=0.0, end=10.0)])
    explicit = patient._derived(
        0.0,
        state,
        [
            ProtocolSegment(
                start=0.0, end=10.0, end_tidal_co2_mmHg=p.end_tidal_co2_reference_mmHg
            )
        ],
    )
    assert implicit["end_tidal_co2_mmHg"] == p.end_tidal_co2_reference_mmHg == 40.0
    assert implicit["cerebral_co2_factor"] == 1.0
    assert implicit["cerebral_flow_target"] == explicit["cerebral_flow_target"]


def test_co2_factor_is_bounded_and_symmetric_around_reference():
    patient = ComputationalPatient()
    p = patient.parameters
    state = patient.initial_state()
    for etco2 in (40.0, 30.0, 50.0):
        d = patient._derived(
            0.0, state, [ProtocolSegment(start=0.0, end=10.0, end_tidal_co2_mmHg=etco2)]
        )
        assert d["cerebral_co2_factor"] == pytest.approx(_expected_co2_factor(etco2, p))
        # Pressure curve is untouched by the CO2 input (isolation).
        assert d["cerebral_pressure_target"] == pytest.approx(1.0)
        assert d["cerebral_flow_target"] == pytest.approx(
            d["cerebral_pressure_target"] * d["cerebral_co2_factor"]
        )


def test_co2_extrapolation_limit_clips_to_plateaus():
    patient = ComputationalPatient()
    p = patient.parameters
    state = patient.initial_state()

    def factor(etco2):
        return patient._derived(
            0.0, state, [ProtocolSegment(start=0.0, end=10.0, end_tidal_co2_mmHg=etco2)]
        )["cerebral_co2_factor"]

    low_plateau = _expected_co2_factor(
        p.end_tidal_co2_reference_mmHg - p.cerebral_co2_extrapolation_limit_mmHg, p
    )
    high_plateau = _expected_co2_factor(
        p.end_tidal_co2_reference_mmHg + p.cerebral_co2_extrapolation_limit_mmHg, p
    )
    assert factor(25.0) == pytest.approx(low_plateau)  # at the limit
    assert factor(10.0) == pytest.approx(low_plateau)  # beyond the limit: clipped
    assert factor(55.0) == pytest.approx(high_plateau)
    assert factor(70.0) == pytest.approx(high_plateau)


def test_pressure_and_co2_factors_are_independent_and_multiplicative():
    patient = ComputationalPatient()
    state = patient.initial_state()
    protocol_pressure_only = _supine_then_tilt(end_tidal_co2_mmHg=40.0)
    protocol_combined = _supine_then_tilt(end_tidal_co2_mmHg=30.0)
    t_tilted = TILT_START + TRANSITION + 1.0
    d_pressure = patient._derived(t_tilted, state, protocol_pressure_only)
    d_combined = patient._derived(t_tilted, state, protocol_combined)
    # Same posture and state: identical pressure-side quantities.
    assert d_combined["brain_arterial_pressure"] == d_pressure["brain_arterial_pressure"]
    assert d_combined["cerebral_perfusion_pressure"] == d_pressure[
        "cerebral_perfusion_pressure"
    ]
    assert d_combined["cerebral_pressure_target"] == d_pressure["cerebral_pressure_target"]
    # The CO2 factor enters purely multiplicatively.
    ratio = d_combined["cerebral_flow_target"] / d_pressure["cerebral_flow_target"]
    assert ratio == pytest.approx(_expected_co2_factor(30.0, patient.parameters), rel=1e-12)
    assert ratio < 1.0


def test_co2_sensitivity_parameters_move_the_response_as_declared():
    """CO2 sensitivity coverage: reactivity scales the factor slope and the
    extrapolation limit moves the clipping plateau."""
    p = ModelParameters()
    state = ComputationalPatient().initial_state()

    def factor(parameters: ModelParameters, etco2: float) -> float:
        patient = ComputationalPatient(parameters)
        return patient._derived(
            0.0, state, [ProtocolSegment(start=0.0, end=10.0, end_tidal_co2_mmHg=etco2)]
        )["cerebral_co2_factor"]

    more_reactive = p.replaced({"cerebral_co2_reactivity_per_mmHg": 2.0 * p.cerebral_co2_reactivity_per_mmHg})
    # Larger reactivity: larger |factor - 1| for the same in-range deviation.
    assert factor(more_reactive, 30.0) < factor(p, 30.0) < 1.0
    assert factor(more_reactive, 50.0) > factor(p, 50.0) > 1.0
    # Wider limit: the same extreme ETCO2 no longer clips at the old plateau.
    wider_limit = p.replaced({"cerebral_co2_extrapolation_limit_mmHg": 25.0})
    # At ETCO2 20 mmHg the deviation (-20) exceeds the default limit (15) but
    # fits inside the widened one, so the wider-limit model responds more.
    assert factor(wider_limit, 20.0) < factor(p, 20.0)
    assert factor(wider_limit, 20.0) == pytest.approx(
        math.exp(p.cerebral_co2_reactivity_per_mmHg * -20.0)
    )


# --------------------------------------- persistent one-factor recovery runs
def _run(segments) -> object:
    return ComputationalPatient().simulate(segments, sample_interval=2.0)


def test_pressure_recovery_with_persistent_hypocapnia_limits_recovery():
    """Tilt-back restores pressure geometry but ETCO2 stays low: the cerebral
    index recovers only to the CO2-factor floor, not to baseline."""
    result = _run(
        [
            ProtocolSegment(
                start=0.0, end=TILT_START, tilt_angle_deg=0.0, end_tidal_co2_mmHg=40.0
            ),
            ProtocolSegment(
                start=TILT_START,
                end=TILT_END,
                tilt_angle_deg=70.0,
                transition_duration=TRANSITION,
                end_tidal_co2_mmHg=30.0,
            ),
            ProtocolSegment(
                start=TILT_END,
                end=RECOVERY_END,
                tilt_angle_deg=0.0,
                transition_duration=TRANSITION,
                end_tidal_co2_mmHg=30.0,
            ),
        ]
    )
    cfi = result.outputs["cerebral_flow_index"]
    baseline = float(cfi[result.time <= TILT_START - 2.0].mean())
    floor = _expected_co2_factor(30.0, result.parameters)
    final = float(cfi[-1])
    assert baseline == pytest.approx(1.0, abs=1e-9)
    assert result.outputs["cerebral_co2_factor"][-1] == pytest.approx(floor)
    # Pressure geometry is fully restored supine...
    assert result.outputs["cerebral_pressure_target"][-1] == pytest.approx(1.0, abs=1e-3)
    # ...but the persistent hypocapnia holds the index at the CO2 floor.
    assert final == pytest.approx(floor, abs=0.02)
    assert final < baseline - 0.2


def test_co2_recovery_with_persistent_pressure_reduction_limits_recovery():
    """ETCO2 returns to reference while the 70 degree tilt persists: the index
    recovers from the combined reduction only up to the tilted pressure target."""
    result = _run(
        [
            ProtocolSegment(
                start=0.0, end=TILT_START, tilt_angle_deg=0.0, end_tidal_co2_mmHg=40.0
            ),
            ProtocolSegment(
                start=TILT_START,
                end=TILT_END,
                tilt_angle_deg=70.0,
                transition_duration=TRANSITION,
                end_tidal_co2_mmHg=30.0,
            ),
            ProtocolSegment(
                start=TILT_END,
                end=RECOVERY_END,
                tilt_angle_deg=70.0,
                end_tidal_co2_mmHg=40.0,
            ),
        ]
    )
    cfi = result.outputs["cerebral_flow_index"]
    t = result.time
    combined = float(cfi[np.argmin(np.abs(t - TILT_END))])
    final = float(cfi[-1])
    floor = _expected_co2_factor(30.0, result.parameters)
    assert result.outputs["cerebral_co2_factor"][-1] == pytest.approx(1.0)
    # Recovery above the hypocapnic floor but capped by the persisting tilt.
    assert combined < floor
    assert final > floor + 0.1
    assert final < 1.0
    assert final == pytest.approx(
        float(result.outputs["cerebral_pressure_target"][-1]), abs=0.02
    )
