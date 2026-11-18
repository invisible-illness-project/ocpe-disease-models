"""VAL-PHYS-BASELINE: healthy resting operating point (layer: physiological).

Acceptance: mean supine HR 55-85 bpm; MAP 80-105 mmHg; cardiac output
4-8 L/min; PEM severity zero; late-rest HR drift below 0.1 bpm.
These are broad operating-point checks, not population validation.
"""

from __future__ import annotations

import numpy as np
import pytest

from ocpe_disease_models.models.shared.model import STATE_NAMES

pytestmark = pytest.mark.physiological


def test_mean_supine_heart_rate_in_range(healthy_baseline_result):
    hr = healthy_baseline_result.outputs["heart_rate"]
    assert 55.0 <= float(hr.mean()) <= 85.0


def test_mean_arterial_pressure_in_range(healthy_baseline_result):
    map_ = healthy_baseline_result.outputs["mean_arterial_pressure"]
    assert 80.0 <= float(map_.mean()) <= 105.0


def test_cardiac_output_in_range(healthy_baseline_result):
    co = healthy_baseline_result.outputs["cardiac_output_l_min"]
    assert 4.0 <= float(co.mean()) <= 8.0


def test_exact_healthy_flow_partition_and_stressed_volume(healthy_baseline_result):
    """Exact Stage 1.1 healthy operating point: 25/25/50 systemic flow split
    (splanchnic/lower-limb/other-systemic) and 2550 mL total stressed volume."""
    outputs = healthy_baseline_result.outputs
    flows = (
        float(outputs["splanchnic_arterial_flow"][0]),
        float(outputs["lower_limb_arterial_flow"][0]),
        float(outputs["other_systemic_arterial_flow"][0]),
    )
    assert flows == pytest.approx((20.4166667, 20.4166667, 40.8333333), abs=1e-6)
    cardiac_output = float(outputs["cardiac_output"][0])
    assert cardiac_output == pytest.approx(81.6666667, abs=1e-6)
    systemic = float(outputs["systemic_flow"][0])
    assert systemic == pytest.approx(cardiac_output, rel=1e-10)
    # Each regional share is exactly 0.25/0.25/0.50 of systemic flow.
    assert flows[0] / systemic == pytest.approx(0.25, rel=1e-9)
    assert flows[1] / systemic == pytest.approx(0.25, rel=1e-9)
    assert flows[2] / systemic == pytest.approx(0.50, rel=1e-9)
    # Venous returns match arterial inflows bed by bed at the fixed point.
    for bed in ("splanchnic", "lower_limb", "other_systemic"):
        assert float(outputs[f"{bed}_venous_return"][0]) == pytest.approx(
            float(outputs[f"{bed}_arterial_flow"][0]), rel=1e-10
        )
    # Exact Stage 1.3 stressed-volume partition: 150/700/900/600/200 mL.
    # Total stressed volume remains 2550 mL; only regional allocation changes.
    states = healthy_baseline_result.states
    expected_volumes = {
        "arterial_volume": 150.0,
        "central_venous_volume": 700.0,
        "splanchnic_venous_volume": 900.0,
        "lower_limb_venous_volume": 600.0,
        "other_systemic_venous_volume": 200.0,
    }
    for name, expected in expected_volumes.items():
        idx = STATE_NAMES.index(name)
        assert float(states[idx, 0]) == pytest.approx(expected, rel=1e-12)
    total = float(states[: STATE_NAMES.index("other_systemic_venous_volume") + 1, 0].sum())
    assert total == pytest.approx(2550.0, rel=1e-12)


def test_pem_severity_is_zero_at_rest(healthy_baseline_result):
    pem = healthy_baseline_result.outputs["pem_severity"]
    assert float(np.max(pem)) == 0.0


def test_late_rest_heart_rate_drift_below_tolerance(healthy_baseline_result):
    t = healthy_baseline_result.time
    hr = healthy_baseline_result.outputs["heart_rate"]
    late = hr[t >= t[-1] - 200.0]
    drift = float(late[-1] - late[0])
    assert abs(drift) < 0.1, f"late-rest HR drift {drift} bpm"
    # The operating point is stable, not slowly drifting.
    assert float(np.abs(np.diff(late)).max()) < 0.1
