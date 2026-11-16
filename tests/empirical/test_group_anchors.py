"""Empirical group-level anchors (layer: empirical).

Covers VAL-ME-CPET, VAL-ME-CBF and VAL-EMPIRICAL-ANCHORS. These are
heterogeneous group-level plausibility checks against cited literature
anchors -- not fitted individual data and not prospective external validation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

TESTS_DIR = Path(__file__).resolve().parents[1]
SRC = TESTS_DIR.parent / "src"
for _p in (str(TESTS_DIR), str(SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

pytestmark = pytest.mark.empirical

REPO_ROOT = Path(__file__).resolve().parents[2]

# Predeclared scenario bands from validation_registry.yaml.
CPET_REDUCTION_BAND_PCT = (2.0, 20.0)  # broad band around 5.3% / 13.8% anchors
CBF_REDUCTION_BAND_PCT = (15.0, 35.0)  # broad band around the 26% group mean

EXERTION_DAY1_START = 3600.0
EXERTION_DAY2_START = 86400.0
TILT_START = 120.0
TILT_END = 600.0


def _evidence_claims():
    raw = yaml.safe_load((REPO_ROOT / "literature" / "evidence_registry.yaml").read_text())
    return {c["id"]: c for c in raw["evidence_claims"]}


def _reference_ids():
    raw = yaml.safe_load((REPO_ROOT / "literature" / "references.yaml").read_text())
    entries = raw["references"] if isinstance(raw, dict) else raw
    return {r["id"] for r in entries}


def _at(result, t):
    return int(np.argmin(np.abs(result.time - t)))


# ------------------------------------------------------------- VAL-ME-CPET
def test_reduced_subsequent_exertional_capacity(mecfs_repeated_exertion_result):
    """A single scenario reduces subsequent normalized functional capacity by
    a magnitude within the predeclared broad 2-20% band (anchors: 5.3% and
    13.8% repeated-CPET VO2peak findings, CLM-ME-CPET)."""
    result = mecfs_repeated_exertion_result
    fc = result.outputs["functional_capacity"]
    day1 = float(fc[_at(result, EXERTION_DAY1_START)])
    day2 = float(fc[_at(result, EXERTION_DAY2_START)])
    assert day1 > 0.0
    reduction_pct = 100.0 * (day1 - day2) / day1
    assert reduction_pct > 0.0, "no subsequent capacity reduction"
    assert CPET_REDUCTION_BAND_PCT[0] <= reduction_pct <= CPET_REDUCTION_BAND_PCT[1], (
        f"subsequent capacity reduction {reduction_pct:.2f}% outside the "
        f"predeclared {CPET_REDUCTION_BAND_PCT}% scenario band"
    )


def test_capacity_output_is_normalized_construct(mecfs_repeated_exertion_result):
    """The compared output is a normalized dimensionless construct, not
    measured VO2."""
    result = mecfs_repeated_exertion_result
    fc = result.outputs["functional_capacity"]
    assert 0.0 <= float(fc.min()) and float(fc.max()) <= 1.0 + 1e-9
    # The run is explicitly labeled a research demonstration, not a measurement.
    assert "not clinically validated" in result.metadata["scientific_status"]
    claim = _evidence_claims()["CLM-ME-CPET"]
    assert "5.3" in claim["reported_effect"] and "13.8" in claim["reported_effect"]
    assert "not a fixed patient effect" in claim["parameter_implications"]


# -------------------------------------------------------------- VAL-ME-CBF
def _end_tilt_reduction_pct(result):
    t = result.time
    cfi = result.outputs["cerebral_flow_index"]
    baseline = float(cfi[(t >= 0.0) & (t <= TILT_START - 2.0)].mean())
    end_tilt = float(cfi[(t >= TILT_END - 10.0) & (t <= TILT_END)].mean())
    return 100.0 * (baseline - end_tilt) / baseline


def test_mecfs_cerebral_flow_reduction_within_anchor_band(
    mecfs_tilt_recovery_result, healthy_tilt_recovery_result
):
    """End-tilt cerebral-flow-index reduction within the broad 15-35% band
    around the reported 26% group mean (CLM-ME-CBF); healthy reduction is
    smaller. Recovery behavior is tested separately (test_recovery.py)."""
    mecfs_reduction = _end_tilt_reduction_pct(mecfs_tilt_recovery_result)
    healthy_reduction = _end_tilt_reduction_pct(healthy_tilt_recovery_result)
    assert CBF_REDUCTION_BAND_PCT[0] <= mecfs_reduction <= CBF_REDUCTION_BAND_PCT[1], (
        f"ME/CFS end-tilt cerebral index reduction {mecfs_reduction:.2f}% "
        f"outside the {CBF_REDUCTION_BAND_PCT}% scenario band"
    )
    assert healthy_reduction < mecfs_reduction


# --------------------------------------------------- VAL-EMPIRICAL-ANCHORS
ANCHOR_CLAIMS = {
    "CLM-POTS-CRITERIA": ["30"],  # adult >=30 bpm scenario threshold
    "CLM-ME-PEM-KINETICS": ["12", "48"],  # reported PEM onset window (hours)
    "CLM-ME-CPET": ["5.3", "13.8"],  # repeated-CPET VO2peak decrements (%)
    "CLM-ME-CBF": ["26"],  # end-tilt CBF reduction group mean (%)
    "CLM-LC-EXTRACTION": ["0.49", "0.78"],  # invasive-CPET extraction anchors
}


@pytest.mark.parametrize("claim_id", sorted(ANCHOR_CLAIMS))
def test_anchor_claims_resolve_to_evidence(claim_id):
    """Every quantitative empirical comparison resolves to a cited group-level
    finding with references, limitations, and validation links."""
    claims = _evidence_claims()
    references = _reference_ids()
    assert claim_id in claims, f"evidence claim {claim_id} missing"
    claim = claims[claim_id]
    assert claim["references"], f"{claim_id} has no references"
    assert set(claim["references"]) <= references, (
        f"{claim_id} references {set(claim['references']) - references} not in references.yaml"
    )
    assert claim.get("limitations"), f"{claim_id} reports no limitations"
    assert claim.get("validation_links"), f"{claim_id} has no validation links"
    text = " ".join(
        str(claim.get(key, "")) for key in ("statement", "reported_effect", "description")
    )
    for token in ANCHOR_CLAIMS[claim_id]:
        assert token in text, f"{claim_id} does not state the anchor value {token!r}"


def test_no_patient_level_fit_or_diagnostic_accuracy_claimed():
    """Registry-level policy: empirical comparisons are group-level
    plausibility checks; no patient-level fit or diagnostic accuracy claim."""
    registry = yaml.safe_load(
        (REPO_ROOT / "validation" / "validation_registry.yaml").read_text()
    )
    policy = registry["validation_policy"]
    clinical = policy["clinical_status"].lower()
    assert clinical.startswith("no layer establishes")
    assert "clinical validity" in clinical and "diagnostic accuracy" in clinical
    assert "plausibility" in policy["empirical_comparisons"]
    for claim in _evidence_claims().values():
        assert claim.get("evidence_grade", "E0") >= "E1"
