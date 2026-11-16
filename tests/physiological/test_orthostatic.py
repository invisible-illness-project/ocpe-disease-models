"""VAL-PHYS-TILT: orthostatic directionality and compensation (physiological).

Acceptance: healthy upright HR increases 3-20 bpm; upright MAP remains above
70 mmHg; sympathetic state increases; venous return initially falls; volume
remains conserved. Qualitative physiology independent of POTS thresholds.
"""

from __future__ import annotations

import sys
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


def test_pressure_homeostasis_not_destroyed(metrics):
    """Compensation keeps upright pressure near the supine operating point."""
    assert metrics["map_final"] > metrics["map_upright_min"] - 1e-9
    assert metrics["map_final"] > 0.8 * 100.0  # no orthostatic hypotension scenario
