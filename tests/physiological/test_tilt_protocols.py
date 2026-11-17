"""VAL-PHYS-TILT-ANGLE and VAL-PHYS-GRADED-TILT (layer: physiological).

Stage 1.1 posture specification semantics: the dual posture specification
(legacy ``upright`` fraction versus explicit ``tilt_angle_deg``), mutual
exclusion, arcsin equivalence, linear angle-only transitions from the prior
segment, and graded-tilt monotonicity. Protocols are constructed inline so
these semantics are tested independently of the simulation registry contents.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from ocpe_disease_models.models.shared import ComputationalPatient
from ocpe_disease_models.models.shared.model import ProtocolSegment

pytestmark = pytest.mark.physiological

TILT_START = 120.0
TILT_END = 600.0
TRANSITION = 30.0


def _patient() -> ComputationalPatient:
    return ComputationalPatient()


def _simulate(segments, **kwargs):
    return _patient().simulate(segments, sample_interval=2.0, **kwargs)


def _tilt_protocol(angle_deg: float) -> list[ProtocolSegment]:
    return [
        ProtocolSegment(start=0.0, end=TILT_START, tilt_angle_deg=0.0, label="supine"),
        ProtocolSegment(
            start=TILT_START,
            end=TILT_END,
            tilt_angle_deg=angle_deg,
            transition_duration=TRANSITION,
            label=f"tilt-{angle_deg:g}",
        ),
    ]


def _sustained_hr_rise(result) -> float:
    t = result.time
    hr = result.outputs["heart_rate"]
    baseline = float(hr[t <= TILT_START - 2.0].mean())
    late = (t >= TILT_END - 120.0) & (t <= TILT_END)
    return float(hr[late].mean() - baseline)


# ------------------------------------------------------- posture resolution
def test_no_posture_field_means_supine():
    segment = ProtocolSegment(start=0.0, end=10.0)
    assert segment.upright is None and segment.tilt_angle_deg is None
    assert segment.resolved_tilt_angle_deg() == 0.0
    result = _simulate([ProtocolSegment(start=0.0, end=20.0, label="rest")])
    assert np.all(result.outputs["tilt_angle_deg"] == 0.0)
    assert np.all(result.outputs["upright"] == 0.0)


def test_upright_and_tilt_angle_are_mutually_exclusive():
    with pytest.raises(ValueError, match="only one of upright or tilt_angle_deg"):
        ProtocolSegment(start=0.0, end=10.0, upright=0.5, tilt_angle_deg=30.0).validate()


@pytest.mark.parametrize("angle", [-1.0, 90.5, 120.0])
def test_tilt_angle_outside_0_90_rejected(angle):
    with pytest.raises(ValueError, match="tilt_angle_deg"):
        ProtocolSegment(start=0.0, end=10.0, tilt_angle_deg=angle).validate()


@pytest.mark.parametrize("upright", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_legacy_upright_maps_to_arcsin(upright):
    segment = ProtocolSegment(start=0.0, end=10.0, upright=upright)
    assert segment.resolved_tilt_angle_deg() == pytest.approx(
        math.degrees(math.asin(upright)), rel=1e-12
    )
    # upright=1.0 is exactly the 90 degree vertical posture.
    if upright == 1.0:
        assert segment.resolved_tilt_angle_deg() == pytest.approx(90.0)


@pytest.mark.parametrize("upright", [0.25, 0.5, 1.0])
def test_legacy_upright_and_explicit_tilt_produce_identical_trajectories(upright):
    """Legacy ``upright`` is exactly ``arcsin`` sugar for ``tilt_angle_deg``."""
    legacy = _simulate(
        [
            ProtocolSegment(start=0.0, end=TILT_START),
            ProtocolSegment(
                start=TILT_START,
                end=TILT_END,
                upright=upright,
                transition_duration=TRANSITION,
            ),
        ]
    )
    explicit = _simulate(
        [
            ProtocolSegment(start=0.0, end=TILT_START),
            ProtocolSegment(
                start=TILT_START,
                end=TILT_END,
                tilt_angle_deg=math.degrees(math.asin(upright)),
                transition_duration=TRANSITION,
            ),
        ]
    )
    np.testing.assert_array_equal(legacy.states, explicit.states)
    np.testing.assert_array_equal(legacy.outputs["heart_rate"], explicit.outputs["heart_rate"])
    np.testing.assert_array_equal(
        legacy.outputs["tilt_angle_deg"], explicit.outputs["tilt_angle_deg"]
    )


def test_upright_output_is_the_vertical_sine():
    result = _simulate(_tilt_protocol(60.0))
    angle = np.deg2rad(result.outputs["tilt_angle_deg"])
    np.testing.assert_allclose(result.outputs["upright"], np.sin(angle), atol=1e-12)


def test_summary_detects_upright_via_either_posture_field():
    for kwargs in ({"upright": 1.0}, {"tilt_angle_deg": 70.0}):
        result = _simulate(
            [
                ProtocolSegment(start=0.0, end=TILT_START),
                ProtocolSegment(start=TILT_START, end=TILT_END, **kwargs),
            ]
        )
        summary = result.summary()
        assert "orthostatic_heart_rate_rise_bpm" in summary
        assert "orthostatic_heart_rate_sustained_rise_bpm" in summary


def test_summary_treats_active_stand_and_quiet_standing_as_one_bout():
    """An active-stand transition segment followed by a quiet-standing segment
    at the same angle is one continuous orthostatic bout: the sustained window
    extends to the end of the quiet-standing segment, not the first segment."""
    protocol = [
        ProtocolSegment(start=0.0, end=TILT_START, tilt_angle_deg=0.0, label="supine"),
        ProtocolSegment(
            start=120.0,
            end=130.0,
            tilt_angle_deg=90.0,
            transition_duration=3.0,
            rhythmic_muscle_activity=0.25,
            sustained_muscle_contraction=0.25,
            label="active-stand-transition",
        ),
        ProtocolSegment(
            start=130.0, end=600.0, tilt_angle_deg=90.0, label="sustained-quiet-standing"
        ),
    ]
    result = _simulate(protocol)
    summary = result.summary()
    t = result.time
    hr = result.outputs["heart_rate"]
    baseline = float(hr[(t >= 0.0) & (t <= 119.0)].mean())
    # The sustained window is the final 120 s of the whole bout ([480, 600]),
    # which only exists if the bout spans both upright segments.
    expected_sustained = float(hr[(t >= 480.0) & (t <= 600.0)].mean() - baseline)
    assert summary["orthostatic_heart_rate_sustained_rise_bpm"] == pytest.approx(
        expected_sustained
    )
    expected_peak = float(hr[(t >= 120.0) & (t <= 420.0)].max() - baseline)
    assert summary["orthostatic_heart_rate_rise_bpm"] == pytest.approx(expected_peak)


# -------------------------------------------------------------- transitions
def test_transition_duration_must_fit_inside_segment():
    with pytest.raises(ValueError, match="transition_duration"):
        ProtocolSegment(start=0.0, end=10.0, transition_duration=-1.0).validate()
    with pytest.raises(ValueError, match="transition_duration"):
        ProtocolSegment(start=0.0, end=10.0, transition_duration=10.5).validate()
    # Equal to the segment duration is allowed.
    ProtocolSegment(start=0.0, end=10.0, transition_duration=10.0).validate()


def test_angle_interpolates_linearly_from_prior_segment_angle():
    patient = _patient()
    protocol = [
        ProtocolSegment(start=0.0, end=TILT_START, tilt_angle_deg=30.0, label="tilt-30"),
        ProtocolSegment(
            start=TILT_START,
            end=TILT_END,
            tilt_angle_deg=70.0,
            transition_duration=40.0,
            label="tilt-70",
        ),
    ]
    inputs_mid = patient._inputs(TILT_START + 20.0, protocol, 40.0)
    assert inputs_mid.tilt_angle_deg == pytest.approx(50.0)  # halfway 30 -> 70
    inputs_end_transition = patient._inputs(TILT_START + 40.0, protocol, 40.0)
    assert inputs_end_transition.tilt_angle_deg == pytest.approx(70.0)
    inputs_late = patient._inputs(TILT_END - 1.0, protocol, 40.0)
    assert inputs_late.tilt_angle_deg == pytest.approx(70.0)


def test_first_segment_transition_interpolates_from_supine():
    patient = _patient()
    protocol = [
        ProtocolSegment(
            start=0.0, end=100.0, tilt_angle_deg=60.0, transition_duration=20.0
        )
    ]
    assert patient._inputs(10.0, protocol, 40.0).tilt_angle_deg == pytest.approx(30.0)


def test_transition_interpolates_only_the_angle():
    """Non-posture inputs remain piecewise constant during a transition."""
    patient = _patient()
    protocol = [
        ProtocolSegment(start=0.0, end=TILT_START, tilt_angle_deg=0.0, exertion=0.0),
        ProtocolSegment(
            start=TILT_START,
            end=TILT_END,
            tilt_angle_deg=60.0,
            transition_duration=40.0,
            exertion=1.0,
            rhythmic_muscle_activity=1.0,
            end_tidal_co2_mmHg=30.0,
        ),
    ]
    before = patient._inputs(TILT_START - 1.0, protocol, 40.0)
    mid = patient._inputs(TILT_START + 20.0, protocol, 40.0)  # mid-transition
    assert mid.tilt_angle_deg == pytest.approx(30.0)
    # Exertion, muscle activity and ETCO2 step at the boundary; they are not
    # interpolated over the transition window.
    assert before.exertion == 0.0
    assert mid.exertion == 1.0
    assert mid.rhythmic_muscle_activity == 1.0
    assert mid.end_tidal_co2_mmHg == 30.0


# -------------------------------------------------------------- graded tilt
def test_graded_tilt_response_increases_monotonically_with_angle():
    """Larger tilt angles produce strictly larger sustained HR rises and
    strictly more caudal (splanchnic + lower-limb) venous pooling."""
    from ocpe_disease_models.models.shared.model import STATE_NAMES

    rises = []
    pooling = []
    splanchnic = STATE_NAMES.index("splanchnic_venous_volume")
    lower_limb = STATE_NAMES.index("lower_limb_venous_volume")
    for angle in (30.0, 45.0, 60.0, 70.0):
        result = _simulate(_tilt_protocol(angle))
        rises.append(_sustained_hr_rise(result))
        t = result.time
        supine = t <= TILT_START - 2.0
        late = t >= TILT_END - 120.0
        caudal = result.states[splanchnic : lower_limb + 1]
        pooling.append(
            float(caudal[:, late].mean(axis=1).sum() - caudal[:, supine].mean(axis=1).sum())
        )
    assert all(b > a for a, b in zip(rises, rises[1:], strict=False)), rises
    assert all(b > a for a, b in zip(pooling, pooling[1:], strict=False)), pooling


def test_gapped_protocol_is_rejected_before_integration():
    with pytest.raises(ValueError, match="contiguous"):
        _patient().simulate(
            [
                ProtocolSegment(start=0.0, end=10.0),
                ProtocolSegment(start=11.0, end=20.0),
            ]
        )


@pytest.mark.parametrize("solver", [{"sample_interval": 0.0}, {"max_step": -1.0}])
def test_solver_step_sizes_must_be_positive(solver):
    with pytest.raises(ValueError, match="positive and finite"):
        _patient().simulate([ProtocolSegment(start=0.0, end=10.0)], **solver)
