"""VAL-REGRESSION: approved scientific regression fixtures (layer: software).

Stored summary metrics must match within declared numerical tolerances.
Fixture values are executable research baselines generated from current model
outputs -- not clinical targets. Fixture changes require a change record
explaining mechanism, evidence, and expected direction.
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

from conftest import stressed_volume_drift  # noqa: E402

pytestmark = pytest.mark.regression

FIXTURE_PATH = TESTS_DIR.parent / "validation" / "fixtures" / "regression_fixtures.json"


@pytest.fixture(scope="module")
def fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _tolerance(fixture, metric):
    cls = fixture["metric_tolerance_class"][metric]
    return fixture["tolerances"][cls]


def _fixture_run_ids(fixture):
    return sorted(fixture["runs"])


def test_fixture_is_labeled_research_baseline_not_clinical_target(fixture):
    label = (fixture["label"] + " " + fixture["scientific_status"]).lower()
    assert "research baseline" in label or "research baselines" in label
    assert "not clinical target" in label
    assert "not clinically validated" in fixture["scientific_status"]


def test_fixture_requires_change_records(fixture):
    assert fixture["change_policy"]
    records = fixture["change_records"]
    assert records, "fixture must carry at least one change record"
    for record in records:
        assert record["mechanism"]
        assert record["evidence"]
        assert "expected_direction" in record


def test_fixture_covers_all_declared_runs(fixture):
    assert len(_fixture_run_ids(fixture)) >= 10
    for run_key in _fixture_run_ids(fixture):
        phenotype_id, protocol_id = run_key.split("__")
        assert phenotype_id and protocol_id
        metrics = fixture["runs"][run_key]
        assert "heart_rate_final_bpm" in metrics
        assert "mean_arterial_pressure_final_mmHg" in metrics
        assert "pem_peak" in metrics
        assert "functional_capacity_final" in metrics


@pytest.mark.parametrize(
    "run_key",
    sorted(json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))["runs"]),
)
def test_summary_metrics_match_fixture(run_key, fixture, run_cached):
    phenotype_id, protocol_id = run_key.split("__")
    result = run_cached(phenotype_id, protocol_id)
    summary = result.summary()
    actual = {
        key: value for key, value in summary.items() if isinstance(value, (int, float))
    }
    actual["total_stressed_volume_drift_ml"] = stressed_volume_drift(result)
    expected = fixture["runs"][run_key]
    assert set(actual) == set(expected), (
        f"metric set drifted for {run_key}: "
        f"missing={set(expected) - set(actual)} new={set(actual) - set(expected)}"
    )
    for metric, expected_value in expected.items():
        tol = _tolerance(fixture, metric)
        if tol == 0.0:
            assert actual[metric] == expected_value, (
                f"{run_key}/{metric}: {actual[metric]} != {expected_value} (exact)"
            )
        else:
            assert actual[metric] == pytest.approx(expected_value, abs=tol), (
                f"{run_key}/{metric}: {actual[metric]} vs baseline "
                f"{expected_value} (tolerance {tol}). If this is a reviewed "
                "scientific change, update the fixture with a change record "
                "explaining mechanism, evidence, and expected direction."
            )
