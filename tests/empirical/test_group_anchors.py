"""Empirical group-level anchors (layer: empirical).

Covers VAL-ME-CPET, VAL-ME-CBF and VAL-EMPIRICAL-ANCHORS. These are
heterogeneous group-level plausibility checks against cited literature
anchors -- not fitted individual data and not prospective external validation.
"""

from __future__ import annotations

import sys
import warnings
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
HEALTHY_CBF_REDUCTION_SOFT_BAND_PCT = (3.0, 11.0)  # disclosure band around 7% controls

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
    """ME/CFS end-tilt reduction must meet its broad 15-35% scenario band.

    The healthy comparison is deliberately only directional at the hard-test
    level. Its separate 3-11% soft band around the reported 7% control mean is
    a disclosure screen: the current near-zero response emits a warning rather
    than being hidden or converted into a hard fitted target. Recovery behavior
    is tested separately (test_recovery.py).
    """
    mecfs_reduction = _end_tilt_reduction_pct(mecfs_tilt_recovery_result)
    healthy_reduction = _end_tilt_reduction_pct(healthy_tilt_recovery_result)
    assert CBF_REDUCTION_BAND_PCT[0] <= mecfs_reduction <= CBF_REDUCTION_BAND_PCT[1], (
        f"ME/CFS end-tilt cerebral index reduction {mecfs_reduction:.2f}% "
        f"outside the {CBF_REDUCTION_BAND_PCT}% scenario band"
    )
    assert healthy_reduction < mecfs_reduction
    if not (
        HEALTHY_CBF_REDUCTION_SOFT_BAND_PCT[0]
        <= healthy_reduction
        <= HEALTHY_CBF_REDUCTION_SOFT_BAND_PCT[1]
    ):
        warnings.warn(
            f"Healthy end-tilt cerebral-flow-index reduction {healthy_reduction:.3f}% "
            f"is outside the broad {HEALTHY_CBF_REDUCTION_SOFT_BAND_PCT}% soft "
            "plausibility band around the reported 7% control reduction; this "
            "control-side miss is retained as a structural limitation, not tuned away.",
            UserWarning,
            stacklevel=2,
        )


def _reduction_pct_at_offset(result, offset_s: float) -> float:
    """CFI reduction (%) at ``offset_s`` seconds after tilt onset."""
    t = result.time
    cfi = result.outputs["cerebral_flow_index"]
    baseline = float(cfi[(t >= 0.0) & (t <= TILT_START - 2.0)].mean())
    value = float(cfi[_at(result, TILT_START + offset_s)])
    return 100.0 * (baseline - value) / baseline


def test_cerebral_flow_reduction_time_course_is_group_separated(
    mecfs_tilt_recovery_result, healthy_tilt_recovery_result
):
    """Protocol-specific time-resolved comparison along the head-up tilt.

    Reductions are compared at immediate (0 s, transition onset), 10 s, 30 s,
    60 s, 2 min and 5 min after tilt onset plus the sustained end-tilt window.
    The ME/CFS group must separate above the healthy control at every resolved
    post-onset time point; no additional numeric thresholds are introduced.
    """
    offsets = {
        "immediate": 0.0,
        "10s": 10.0,
        "30s": 30.0,
        "60s": 60.0,
        "2min": 120.0,
        "5min": 300.0,
    }
    healthy = {
        label: _reduction_pct_at_offset(healthy_tilt_recovery_result, off)
        for label, off in offsets.items()
    }
    mecfs = {
        label: _reduction_pct_at_offset(mecfs_tilt_recovery_result, off)
        for label, off in offsets.items()
    }
    healthy["sustained"] = _end_tilt_reduction_pct(healthy_tilt_recovery_result)
    mecfs["sustained"] = _end_tilt_reduction_pct(mecfs_tilt_recovery_result)
    # At transition onset neither group has responded yet.
    assert healthy["immediate"] == pytest.approx(0.0, abs=1e-6)
    assert mecfs["immediate"] == pytest.approx(0.0, abs=1e-6)
    # Group separation at every resolved post-onset time point.
    for label in ("10s", "30s", "60s", "2min", "5min", "sustained"):
        assert mecfs[label] > healthy[label], (
            f"no group separation at {label}: ME/CFS {mecfs[label]:.2f}% "
            f"vs healthy {healthy[label]:.2f}%"
        )
    # The 5 min reading has reached the sustained end-tilt level in both groups.
    assert mecfs["5min"] == pytest.approx(mecfs["sustained"], abs=1.0)
    assert healthy["5min"] == pytest.approx(healthy["sustained"], abs=1.0)


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
