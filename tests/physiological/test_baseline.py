"""VAL-PHYS-BASELINE: healthy resting operating point (layer: physiological).

Acceptance: mean supine HR 55-85 bpm; MAP 80-105 mmHg; cardiac output
4-8 L/min; PEM severity zero; late-rest HR drift below 0.1 bpm.
These are broad operating-point checks, not population validation.
"""

from __future__ import annotations

import numpy as np
import pytest

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
