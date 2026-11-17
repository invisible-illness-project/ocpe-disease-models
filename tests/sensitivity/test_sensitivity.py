"""VAL-SENSITIVITY: deterministic regional and autonomic sensitivity analysis."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import orthostatic_metrics

from ocpe_disease_models.config import load_protocol
from ocpe_disease_models.models.shared.model import ComputationalPatient, ModelParameters
from ocpe_disease_models.validation.sensitivity import chronotropic_split_grid, local_sensitivity

pytestmark = pytest.mark.sensitivity_uncertainty

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "validation" / "fixtures" / "sensitivity_ranges.json"
DERIVATIVE_RTOL = 1e-6
PARAMETERS = (
    "lower_limb_hydrostatic_height_cm",
    "splanchnic_resistance_sympathetic_gain",
    "blood_volume_factor",
    "lower_limb_venous_compliance",
)
_RUN_CACHE: dict[tuple, tuple[float, float]] = {}


def _metrics_for(overrides, use_cache=True):
    key = tuple(sorted(overrides.items()))
    if use_cache and key in _RUN_CACHE:
        return _RUN_CACHE[key]
    patient = ComputationalPatient(
        ModelParameters().replaced(overrides), phenotype_id="sensitivity-scenario"
    )
    segments, _ = load_protocol("head-up-tilt")
    result = patient.simulate(segments, sample_interval=2.0, max_step=2.0)
    metrics = orthostatic_metrics(result)
    _RUN_CACHE[key] = (metrics["hr_rise_sustained"], metrics["map_final"])
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
    step = spec["step"]
    first = _central_derivative(name, step, use_cache=False)
    second = _central_derivative(name, step, use_cache=False)
    assert first == second
    assert all(abs(value) < float("inf") for value in first)
    assert first[0] != 0.0
    assert first[0] == pytest.approx(
        spec["d_orthostatic_heart_rate_sustained_rise_bpm"], rel=DERIVATIVE_RTOL
    )
    assert first[1] == pytest.approx(
        spec["d_mean_arterial_pressure_final_mmHg"], rel=DERIVATIVE_RTOL
    )


def test_derivative_directions_match_mechanism_interpretation(fixture):
    derivatives = {
        name: _central_derivative(name, fixture["parameters"][name]["step"])
        for name in PARAMETERS
    }
    assert derivatives["lower_limb_hydrostatic_height_cm"][0] > 0.0
    assert derivatives["lower_limb_venous_compliance"][0] > 0.0
    assert derivatives["splanchnic_resistance_sympathetic_gain"][0] < 0.0
    assert derivatives["blood_volume_factor"][0] < 0.0


def test_fixture_exports_ranges_and_assumptions(fixture):
    assert fixture["method"]["no_stochastic_cohort"] is True
    assert fixture["assumptions"]
    for name in PARAMETERS:
        spec = fixture["parameters"][name]
        assert spec["mechanism"].startswith("MEC-")
        assert len(spec["sampled_values"]) == 3
        assert spec["nominal"] in spec["sampled_values"]


def test_heds_sensitivity_includes_increased_and_healthy_compliance(fixture):
    heds = fixture["parameters"]["lower_limb_venous_compliance"]["heds_assumption"]
    assert heds["healthy_value"] == 50.0
    assert heds["assumed_heds_value"] == pytest.approx(58.333333333333336)
    rise_healthy, _ = _metrics_for({"lower_limb_venous_compliance": 50.0})
    rise_heds, _ = _metrics_for({"lower_limb_venous_compliance": 58.333333333333336})
    assert rise_healthy == pytest.approx(
        heds["orthostatic_heart_rate_sustained_rise_bpm_at_50"], rel=DERIVATIVE_RTOL
    )
    assert rise_heds == pytest.approx(
        heds["orthostatic_heart_rate_sustained_rise_bpm_at_58_333"], rel=DERIVATIVE_RTOL
    )
    assert rise_heds > rise_healthy


def test_local_analysis_covers_declared_shared_assumptions():
    rows = local_sensitivity()
    covered = {(row["protocol_id"], row["parameter"]) for row in rows}
    required = {
        ("head-up-tilt", "splanchnic_venous_compliance"),
        ("head-up-tilt", "lower_limb_venous_compliance"),
        ("head-up-tilt", "splanchnic_resistance_sympathetic_gain"),
        ("head-up-tilt", "lower_limb_resistance_sympathetic_gain"),
        ("head-up-tilt", "splanchnic_hydrostatic_height_cm"),
        ("head-up-tilt", "lower_limb_hydrostatic_height_cm"),
        ("co2-reduction", "cerebral_co2_reactivity_per_mmHg"),
        ("co2-reduction", "cerebral_co2_extrapolation_limit_mmHg"),
        ("head-up-tilt", "cardiac_sympathetic_time_constant"),
        ("head-up-tilt", "vascular_sympathetic_time_constant"),
        ("head-up-tilt", "vagal_time_constant"),
        ("head-up-tilt", "cerebral_autoregulation_residual_slope"),
        ("light-rhythmic-activity", "muscle_pump_stroke_volume"),
        ("light-rhythmic-activity", "muscle_pump_frequency"),
        ("light-rhythmic-activity", "muscle_pump_effectiveness"),
        ("light-rhythmic-activity", "muscle_pump_half_volume"),
        ("sustained-contraction", "sustained_contraction_resistance_gain"),
    }
    assert required <= covered
    assert all(row["scenario_interpretation"].startswith("deterministic") for row in rows)


def test_chronotropic_split_is_explicit_and_total_gain_is_fixed():
    rows = chronotropic_split_grid()
    assert [row["cardiac_sympathetic_fraction"] for row in rows] == [0.0, 0.5, 1.0]
    assert len({row["total_chronotropic_gain"] for row in rows}) == 1
    assert len({row["configuration_sha256"] for row in rows}) == 3
    peaks = [row["orthostatic_heart_rate_rise_bpm"] for row in rows]
    sustained = [row["orthostatic_heart_rate_sustained_rise_bpm"] for row in rows]
    # With the total chronotropic gain fixed, the vagal/cardiac-sympathetic
    # split is non-identifiable at the sustained steady state: sustained rises
    # must be approximately equal (observed: identical to within 1e-3 bpm).
    sustained_spread = max(sustained) - min(sustained)
    assert sustained_spread < 0.05, (
        f"sustained rises differ by {sustained_spread:.4f} bpm across the split; "
        "fixed total gain should be non-identifiable at steady state"
    )
    # Any split dependence is confined to the transient peak (observed spread
    # 0.04 bpm, fraction 0.0 highest); it must not appear at sustained state.
    peak_spread = max(peaks) - min(peaks)
    assert peak_spread > 0.0  # transient separation is observed in the model
    assert peak_spread >= sustained_spread
    for row in rows:
        total = row["total_chronotropic_gain"]
        assert row["overrides"]["heart_rate_cardiac_sympathetic_gain"] + row["overrides"][
            "heart_rate_vagal_gain"
        ] == pytest.approx(total)
