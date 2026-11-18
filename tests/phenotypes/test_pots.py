"""POTS phenotype scenarios (layer: disease_phenotype).

Covers VAL-POTS-NEUROPATHIC, VAL-POTS-HYPER, VAL-POTS-HYPO and VAL-POTS-MIXED.
The >=30 bpm orthostatic HR rise is a consensus scenario threshold
(CLM-POTS-CRITERIA), not a diagnostic validation of the model.
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

from ocpe_disease_models.config import compose_phenotypes, load_phenotype  # noqa: E402
from ocpe_disease_models.models.shared.model import STATE_NAMES  # noqa: E402

pytestmark = pytest.mark.phenotype

POTS_RISE_CRITERION_BPM = 30.0  # adult consensus scenario threshold (CLM-POTS-CRITERIA)
MAP_FLOOR_MMHG = 70.0
POTS_PHENOTYPES = ("pots-neuropathic", "pots-hyperadrenergic", "pots-hypovolemic")


@pytest.fixture(scope="module")
def pots_results(run_cached, healthy_tilt_result):
    return {
        pid: orthostatic_metrics(run_cached(pid, "head-up-tilt")) for pid in POTS_PHENOTYPES
    }, orthostatic_metrics(healthy_tilt_result)


@pytest.mark.parametrize("phenotype_id", POTS_PHENOTYPES)
def test_orthostatic_hr_rise_at_least_30_bpm(phenotype_id, pots_results):
    """VAL-POTS-*: orthostatic HR rise >= 30 bpm (adult scenario threshold)."""
    results, _ = pots_results
    peak = results[phenotype_id]["hr_rise"]
    sustained = results[phenotype_id]["hr_rise_sustained"]
    assert sustained >= POTS_RISE_CRITERION_BPM, (
        f"{phenotype_id}: sustained orthostatic HR rise {sustained:.2f} bpm "
        f"(peak {peak:.2f} bpm) is below the {POTS_RISE_CRITERION_BPM} bpm "
        "scenario threshold"
    )


@pytest.mark.parametrize("phenotype_id", POTS_PHENOTYPES)
def test_orthostatic_hr_rise_exceeds_healthy(phenotype_id, pots_results):
    results, healthy = pots_results
    assert results[phenotype_id]["hr_rise"] > healthy["hr_rise"]


@pytest.mark.parametrize("phenotype_id", POTS_PHENOTYPES)
def test_final_map_preserved(phenotype_id, pots_results):
    """POTS scenarios are without orthostatic hypotension (CLM-POTS-CRITERIA)."""
    results, _ = pots_results
    assert results[phenotype_id]["map_final"] >= MAP_FLOOR_MMHG


@pytest.mark.parametrize("phenotype_id", POTS_PHENOTYPES + ("pots-mixed",))
def test_volume_conserved_not_disabled(phenotype_id, run_cached):
    """The HR rise must not be obtained by disabling volume conservation."""
    result = run_cached(phenotype_id, "head-up-tilt")
    assert stressed_volume_drift(result) < 1e-6


# ------------------------------------------------------------- hypovolemic
def test_hypovolemic_initial_stressed_volume_is_092_of_healthy(run_cached):
    result = run_cached("pots-hypovolemic", "head-up-tilt")
    n_volumes = STATE_NAMES.index("other_systemic_venous_volume") + 1
    initial_total = float(result.states[:n_volumes, 0].sum())
    healthy_total = 150.0 + 700.0 + 700.0 + 500.0 + 500.0
    # The 0.92 factor is an assumed demonstration value, not a measured deficit.
    assert initial_total == pytest.approx(0.92 * healthy_total, rel=1e-9)


def test_hypovolemic_configuration_uses_volume_factor():
    phenotype = load_phenotype("pots-hypovolemic")
    assert phenotype.parameter_overrides["blood_volume_factor"] == pytest.approx(0.92)
    assert "MEC-VOL-HYPOVOLEMIA" in phenotype.mechanisms


# ------------------------------------------------------------------- mixed
def test_mixed_configuration_has_explicit_mechanism_provenance():
    patient = compose_phenotypes(["pots-mixed"])
    assert set(patient.provenance["mechanisms"]) == {
        "MEC-VOL-HYPOVOLEMIA",
        "MEC-VASC-POOLING",
        "MEC-VASC-CONSTRICTION",
        "MEC-AUT-HYPERADRENERGIC",
    }
    assert patient.provenance["phenotypes"] == ["phenotypes/pots/pots-mixed.yaml"]
    phenotype = load_phenotype("pots-mixed")
    assert phenotype.classification == "phenomenological_composition"


def test_mixed_hr_rise_at_least_30_bpm(run_cached, healthy_tilt_result):
    mixed = orthostatic_metrics(run_cached("pots-mixed", "head-up-tilt"))
    healthy = orthostatic_metrics(healthy_tilt_result)
    # The mixed scenario must also preserve pressure and exceed the healthy response.
    assert mixed["hr_rise"] > healthy["hr_rise"]
    assert mixed["map_final"] >= MAP_FLOOR_MMHG
    assert mixed["hr_rise_sustained"] >= POTS_RISE_CRITERION_BPM, (
        f"pots-mixed: sustained orthostatic HR rise "
        f"{mixed['hr_rise_sustained']:.2f} bpm below {POTS_RISE_CRITERION_BPM} bpm"
    )


def test_conflicting_ad_hoc_composition_raises_value_error():
    """Overlapping POTS mechanisms must not be merged by parameter order."""
    with pytest.raises(ValueError, match="Parameter conflict"):
        compose_phenotypes(["pots-neuropathic", "pots-hyperadrenergic"])
    with pytest.raises(ValueError, match="Parameter conflict"):
        compose_phenotypes(["pots-hypovolemic", "pots-mixed"])
