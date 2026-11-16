"""VAL-PHYS-TILT: orthostatic directionality and compensation (physiological).

Acceptance: healthy upright HR increases 3-20 bpm; upright MAP remains above
70 mmHg; sympathetic state increases; venous return initially falls; volume
remains conserved. Qualitative physiology independent of POTS thresholds.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parents[1]
SRC = TESTS_DIR.parent / "src"
for _p in (str(TESTS_DIR), str(SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from conftest import orthostatic_metrics, stressed_volume_drift  # noqa: E402

pytestmark = pytest.mark.physiological


@pytest.fixture(scope="module")
def metrics(healthy_tilt_result):
    return orthostatic_metrics(healthy_tilt_result)


def test_upright_heart_rate_increases_within_healthy_band(metrics):
    assert 3.0 <= metrics["hr_rise"] <= 20.0, (
        f"healthy orthostatic HR rise {metrics['hr_rise']:.2f} bpm outside 3-20 bpm"
    )
    assert 3.0 <= metrics["hr_rise_sustained"] <= 20.0


def test_upright_map_remains_above_70(metrics):
    assert metrics["map_upright_min"] > 70.0
    assert metrics["map_final"] > 70.0


def test_sympathetic_state_increases(metrics):
    assert metrics["sympathetic_upright_late"] > metrics["sympathetic_supine"]


def test_venous_return_initially_falls(metrics):
    assert metrics["venous_return_upright_early_min"] < metrics["venous_return_supine"]


def test_volume_remains_conserved_during_tilt(healthy_tilt_result):
    assert stressed_volume_drift(healthy_tilt_result) < 1e-6


def test_early_co_and_caudal_pooling_soft_anchors_are_explicit(healthy_tilt_result):
    result = healthy_tilt_result
    t = result.time
    supine = (t >= 100.0) & (t < 120.0)
    early = (t >= 120.0) & (t <= 150.0)
    late = t >= 480.0
    baseline_co = result.outputs["cardiac_output"][supine].mean()
    early_co = result.outputs["cardiac_output"][early].min()
    reduction_percent = 100.0 * (baseline_co - early_co) / baseline_co
    initial_regional = result.states[:4, supine].mean(axis=1)
    late_regional = result.states[:4, late].mean(axis=1)
    caudal_accumulation = float((late_regional - initial_regional)[2:].sum())
    assert 0.0 <= reduction_percent <= 50.0
    assert 0.0 <= caudal_accumulation <= 1200.0
    if not 10.0 <= reduction_percent <= 30.0:
        warnings.warn(
            f"early CO reduction {reduction_percent:.2f}% is outside the 10-30% soft anchor",
            UserWarning,
            stacklevel=1,
        )
    if not 300.0 <= caudal_accumulation <= 900.0:
        warnings.warn(
            f"caudal accumulation {caudal_accumulation:.1f} mL is outside the 300-900 mL soft anchor",
            UserWarning,
            stacklevel=1,
        )


def test_summary_sustained_rise_uses_upright_window(healthy_tilt_result):
    metrics = orthostatic_metrics(healthy_tilt_result)
    assert healthy_tilt_result.summary()[
        "orthostatic_heart_rate_sustained_rise_bpm"
    ] == pytest.approx(metrics["hr_rise_sustained"])


def test_pressure_homeostasis_not_destroyed(metrics):
    """Compensation keeps upright pressure near the supine operating point."""
    assert metrics["map_final"] > metrics["map_upright_min"] - 1e-9
    assert metrics["map_final"] > 0.8 * 100.0  # no orthostatic hypotension scenario
