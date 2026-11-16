"""Long COVID autonomic/extraction subgroups (layer: disease_phenotype).

Covers VAL-LC-AUTONOMIC and VAL-LC-EXTRACTION. The two configurations must
remain distinct: one autonomic subgroup can show POTS-like responses; the
exertional/extraction subgroup carries no POTS-like HR criterion.
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

from conftest import orthostatic_metrics, run_phenotype  # noqa: E402

from ocpe_disease_models.config import load_phenotype  # noqa: E402
from ocpe_disease_models.models.shared import ModelParameters  # noqa: E402

pytestmark = pytest.mark.phenotype

POTS_RISE_CRITERION_BPM = 30.0
MAP_FLOOR_MMHG = 70.0


# --------------------------------------------------------- VAL-LC-AUTONOMIC
def test_autonomic_subgroup_hr_rise_at_least_30_bpm(run_cached):
    metrics = orthostatic_metrics(run_cached("long-covid-autonomic", "head-up-tilt"))
    assert metrics["hr_rise_sustained"] >= POTS_RISE_CRITERION_BPM, (
        f"long-covid-autonomic sustained HR rise "
        f"{metrics['hr_rise_sustained']:.2f} bpm below {POTS_RISE_CRITERION_BPM} bpm"
    )


def test_autonomic_subgroup_map_preserved(run_cached):
    metrics = orthostatic_metrics(run_cached("long-covid-autonomic", "head-up-tilt"))
    assert metrics["map_final"] >= MAP_FLOOR_MMHG


def test_autonomic_and_exertional_configurations_remain_distinct():
    autonomic = load_phenotype("long-covid-autonomic")
    exertional = load_phenotype("long-covid-exertional")
    assert autonomic.phenotype_id != exertional.phenotype_id
    assert "MEC-MET-EXTRACTION" in exertional.mechanisms
    assert "MEC-MET-EXTRACTION" not in autonomic.mechanisms
    assert "MEC-AUT-BAROREFLEX" in autonomic.mechanisms
    assert "MEC-AUT-BAROREFLEX" not in exertional.mechanisms
    # One subgroup must not silently claim to represent all Long COVID.
    assert any("not" in lim and "uniform" in lim or "subgroup" in lim for lim in autonomic.limitations)


# -------------------------------------------------------- VAL-LC-EXTRACTION
def test_extraction_fraction_matches_registry_anchor():
    """VAL-LC-EXTRACTION acceptance: extraction fraction is 0.49 versus 0.78
    healthy, matching CLM-LC-EXTRACTION and REF-SINGH-2022."""
    exertional = load_phenotype("long-covid-exertional")
    healthy_default = ModelParameters().oxygen_extraction_fraction
    assert healthy_default == pytest.approx(0.78)
    configured = exertional.parameter_overrides.get("oxygen_extraction_fraction")
    assert configured == pytest.approx(0.49), (
        f"long-covid-exertional oxygen_extraction_fraction is {configured}; "
        "VAL-LC-EXTRACTION and CLM-LC-EXTRACTION require 0.49 versus 0.78 "
        "healthy (REF-SINGH-2022). The 0.74 ME/CFS subgroup anchor belongs "
        "to CLM-ME-PRELOAD and must not be substituted here."
    )


def test_functional_capacity_lower_at_matched_pem_severity():
    """At matched PEM severity (zero at rest), the extraction subgroup has
    lower functional capacity than healthy."""
    healthy = run_phenotype("healthy-reference", "resting-baseline")
    exertional = run_phenotype("long-covid-exertional", "resting-baseline")
    pem_h = float(healthy.outputs["pem_severity"][-1])
    pem_e = float(exertional.outputs["pem_severity"][-1])
    assert pem_h == pytest.approx(pem_e)  # matched PEM severity
    fc_h = float(healthy.outputs["functional_capacity"][-1])
    fc_e = float(exertional.outputs["functional_capacity"][-1])
    assert fc_e < fc_h, (
        f"functional capacity not lower at matched PEM: {fc_e:.3f} vs {fc_h:.3f}"
    )
    # Central cardiac output is preserved separately from the extraction deficit.
    co_h = float(healthy.outputs["cardiac_output_l_min"][-1])
    co_e = float(exertional.outputs["cardiac_output_l_min"][-1])
    assert co_e == pytest.approx(co_h, rel=0.05)


def test_no_pots_like_hr_criterion_on_exertional_subgroup(run_cached, healthy_tilt_result):
    """The exertional subgroup is not required to produce POTS-like HR rises;
    verify it is physiologically distinct from the autonomic subgroup."""
    exertional = orthostatic_metrics(
        run_cached("long-covid-exertional", "head-up-tilt")
    )
    autonomic = orthostatic_metrics(run_cached("long-covid-autonomic", "head-up-tilt"))
    healthy = orthostatic_metrics(healthy_tilt_result)
    assert exertional["hr_rise"] < POTS_RISE_CRITERION_BPM
    assert autonomic["hr_rise_sustained"] >= POTS_RISE_CRITERION_BPM
    assert exertional["hr_rise"] == pytest.approx(healthy["hr_rise"], abs=1.0)
