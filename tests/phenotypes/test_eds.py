"""VAL-EDS-DIRECTION: exploratory hEDS vascular-mechanics scenario (phenotype).

Tests the consequences of an *assumed* lower-limb venous-compliance increase
(hypothesis-constrained phenomenology), not the truth or magnitude of venous
hypercompliance. Acceptance: scenario labeled exploratory and hEDS-specific;
HR rise exceeds healthy; results finite with MAP above 70 mmHg; sensitivity
includes the healthy compliance value; volume conservation preserved.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

TESTS_DIR = Path(__file__).resolve().parents[1]
SRC = TESTS_DIR.parent / "src"
for _p in (str(TESTS_DIR), str(SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from conftest import orthostatic_metrics  # noqa: E402

from ocpe_disease_models.config import load_phenotype  # noqa: E402

pytestmark = pytest.mark.phenotype

SENSITIVITY_FIXTURE = (
    Path(__file__).resolve().parents[2] / "validation" / "fixtures" / "sensitivity_ranges.json"
)


@pytest.fixture(scope="module")
def heds_metrics(run_cached):
    return orthostatic_metrics(run_cached("eds-heds-vascular", "head-up-tilt"))


def test_scenario_is_labeled_exploratory_and_heds_specific():
    phenotype = load_phenotype("eds-heds-vascular")
    assert phenotype.diseases == ("hEDS",)
    assert phenotype.maturity == "M2"
    assert phenotype.classification == "hypothesis_constrained_phenomenology"
    limitations = " ".join(phenotype.limitations).lower()
    assert "hypothesis" in limitations
    assert "not an hEDS-specific measured value" in " ".join(phenotype.limitations)


def test_hr_rise_exceeds_healthy(heds_metrics, healthy_tilt_result):
    healthy = orthostatic_metrics(healthy_tilt_result)
    assert heds_metrics["hr_rise"] > healthy["hr_rise"], (
        f"hEDS HR rise {heds_metrics['hr_rise']:.2f} bpm does not exceed "
        f"healthy {healthy['hr_rise']:.2f} bpm"
    )


def test_results_finite_and_map_preserved(heds_metrics, run_cached):
    result = run_cached("eds-heds-vascular", "head-up-tilt")
    assert np.all(np.isfinite(result.states))
    for name, values in result.outputs.items():
        assert np.all(np.isfinite(values)), f"non-finite output {name!r}"
    assert heds_metrics["map_final"] > 70.0
    assert heds_metrics["map_upright_min"] > 70.0


def test_volume_conserved(heds_metrics):
    assert heds_metrics["volume_drift"] < 1e-6


def test_sensitivity_includes_healthy_compliance_value():
    """The exported ranges include healthy and assumed hEDS lower-limb compliance."""
    fixture = json.loads(SENSITIVITY_FIXTURE.read_text(encoding="utf-8"))
    compliance = fixture["parameters"]["lower_limb_venous_compliance"]
    values = {float(v) for v in compliance["sampled_values"]}
    values |= {float(v) for v in compliance["heds_assumption"]["sampled_values"]}
    assert 60.0 in values, "healthy compliance value missing from sensitivity"
    assert 70.0 in values, "assumed hEDS compliance missing from sensitivity"
