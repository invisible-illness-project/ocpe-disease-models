"""VAL-SENSITIVITY: deterministic local sensitivity analysis.

Registry layer ``sensitivity_uncertainty`` (pytest marker
``sensitivity_uncertainty`` per pyproject.toml). One-at-a-time central finite differences on the healthy
reference background, head-up-tilt protocol. Key outputs must change traceably
under declared perturbations, including reversal of the hEDS exploratory
compliance assumption. No stochastic cohort is generated.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parents[1]
SRC = TESTS_DIR.parent / "src"
for _p in (str(TESTS_DIR), str(SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from conftest import orthostatic_metrics  # noqa: E402

from ocpe_disease_models.config import load_protocol  # noqa: E402
from ocpe_disease_models.models.shared.model import (  # noqa: E402
    ComputationalPatient,
    ModelParameters,
)

pytestmark = pytest.mark.sensitivity_uncertainty

FIXTURE_PATH = TESTS_DIR.parent / "validation" / "fixtures" / "sensitivity_ranges.json"
DERIVATIVE_RTOL = 1e-6

PARAMETERS = (
    "gravity_pressure_offset",
    "resistance_sympathetic_gain",
    "blood_volume_factor",
    "peripheral_venous_compliance",
)


_RUN_CACHE: dict[tuple, tuple[float, float]] = {}


def _metrics_for(overrides, use_cache=True):
    key = tuple(sorted(overrides.items()))
    if use_cache and key in _RUN_CACHE:
        return _RUN_CACHE[key]
    patient = ComputationalPatient(
        ModelParameters().replaced(overrides), phenotype_id="sensitivity-scenario"
    )
    segments, _settings = load_protocol("head-up-tilt")
    result = patient.simulate(segments, sample_interval=2.0, max_step=2.0)
    metrics = orthostatic_metrics(result)
    _RUN_CACHE[key] = (metrics["hr_rise"], metrics["map_final"])
    return _RUN_CACHE[key]


def _central_derivative(name, step, use_cache=True):
    nominal = getattr(ModelParameters(), name)
    lo_rise, lo_map = _metrics_for({name: nominal - step}, use_cache)
    hi_rise, hi_map = _metrics_for({name: nominal + step}, use_cache)
    return (hi_rise - lo_rise) / (2.0 * step), (hi_map - lo_map) / (2.0 * step)


@pytest.fixture(scope="module")
def fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", PARAMETERS)
def test_derivatives_finite_reproducible_and_traceable(name, fixture):
    spec = fixture["parameters"][name]
    step = fixture["parameters"][name]["step"]
    d_rise_1, d_map_1 = _central_derivative(name, step, use_cache=False)
    d_rise_2, d_map_2 = _central_derivative(name, step, use_cache=False)
    # Deterministic: identical recomputation.
    assert d_rise_1 == d_rise_2 and d_map_1 == d_map_2
    # Finite.
    assert abs(d_rise_1) < float("inf") and abs(d_map_1) < float("inf")
    # Traceable: outputs actually change under the declared perturbation.
    assert d_rise_1 != 0.0
    # Match the exported baseline ranges.
    assert d_rise_1 == pytest.approx(
        spec["d_orthostatic_heart_rate_rise_bpm"], rel=DERIVATIVE_RTOL
    )
    assert d_map_1 == pytest.approx(
        spec["d_mean_arterial_pressure_final_mmHg"], rel=DERIVATIVE_RTOL
    )


def test_derivative_directions_match_mechanism_interpretation(fixture):
    """Pooling (gravity offset) and compliance increase the HR rise; vascular
    compensation (resistance gain) and volume reduce it."""
    d = {n: _central_derivative(n, fixture["parameters"][n]["step"]) for n in PARAMETERS}
    assert d["gravity_pressure_offset"][0] > 0.0
    assert d["peripheral_venous_compliance"][0] > 0.0
    assert d["resistance_sympathetic_gain"][0] < 0.0
    assert d["blood_volume_factor"][0] < 0.0


def test_fixture_exports_ranges_and_assumptions(fixture):
    assert fixture["method"]["no_stochastic_cohort"] is True
    assert fixture["assumptions"]
    for name in PARAMETERS:
        spec = fixture["parameters"][name]
        assert spec["mechanism"].startswith("MEC-")
        assert len(spec["sampled_values"]) == 3
        assert spec["nominal"] in spec["sampled_values"]


def test_heds_sensitivity_includes_increased_and_healthy_compliance(fixture):
    """Reversal of the hEDS exploratory compliance assumption must be in scope."""
    heds = fixture["parameters"]["peripheral_venous_compliance"]["heds_assumption"]
    assert heds["healthy_value"] == 120.0
    assert heds["assumed_heds_value"] == 140.0
    rise_120, _ = _metrics_for({"peripheral_venous_compliance": 120.0})
    rise_140, _ = _metrics_for({"peripheral_venous_compliance": 140.0})
    assert rise_120 == pytest.approx(
        heds["orthostatic_heart_rate_rise_bpm_at_120"], rel=DERIVATIVE_RTOL
    )
    assert rise_140 == pytest.approx(
        heds["orthostatic_heart_rate_rise_bpm_at_140"], rel=DERIVATIVE_RTOL
    )
    # Assumed direction: increased compliance increases the orthostatic HR rise.
    assert rise_140 > rise_120
