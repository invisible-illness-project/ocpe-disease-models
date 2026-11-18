"""Stage 1.2 orthostatic cardiovascular fidelity regression tests.

These tests preserve the Stage 1/1.1 group-level plausibility anchors. They are
not patient-specific validation or diagnostic criteria. Stage 1.1 baseline
failures remain recorded in Git history; this module now guards the remediated
behavior.
"""

from __future__ import annotations

import numpy as np
import pytest
from conftest import TILT_END, TILT_START, run_phenotype

from ocpe_disease_models.models.shared.model import STATE_NAMES

pytestmark = pytest.mark.physiological

EARLY_CO_REDUCTION_BAND_PCT = (10.0, 30.0)
CAUDAL_POOLING_BAND_ML = (300.0, 900.0)
ZAIDI_CO_REDUCTION_BAND_PCT = (17.0, 20.0)
ZAIDI_SV_REDUCTION_BAND_PCT = (28.0, 34.0)
HEALTHY_CFI_REDUCTION_BAND_PCT = (3.0, 11.0)

def _mean_window(result, name: str, start: float, end: float) -> float:
    mask = (result.time >= start) & (result.time <= end)
    return float(result.outputs[name][mask].mean())


def _reduction_pct(baseline: float, upright: float) -> float:
    return 100.0 * (baseline - upright) / baseline


def _healthy_tilt():
    return run_phenotype("healthy-reference", "head-up-tilt")


def test_residual_systemic_bed_participates_in_dependent_pooling():
    """The 50%-flow residual bed must not remain a heart-level preload bypass."""
    result = _healthy_tilt()
    name = "other_systemic_venous_volume"
    baseline = _mean_window(result, name, 100.0, TILT_START - 2.0)
    late = _mean_window(result, name, TILT_END - 120.0, TILT_END)
    assert late > baseline, (
        f"residual systemic venous volume changes by {late - baseline:.2f} mL; "
        "a late decrease identifies the Stage 1.1 preload-buffer artifact"
    )


def test_healthy_early_cardiac_output_reduction_meets_preserved_anchor():
    result = _healthy_tilt()
    baseline = _mean_window(result, "cardiac_output", 100.0, TILT_START - 2.0)
    early_mask = (result.time >= TILT_START) & (result.time <= TILT_START + 30.0)
    early_minimum = float(result.outputs["cardiac_output"][early_mask].min())
    reduction = _reduction_pct(baseline, early_minimum)
    assert EARLY_CO_REDUCTION_BAND_PCT[0] <= reduction <= EARLY_CO_REDUCTION_BAND_PCT[1]


def test_healthy_caudal_pooling_meets_preserved_anchor():
    result = _healthy_tilt()
    pooling = 0.0
    for name in ("splanchnic_venous_volume", "lower_limb_venous_volume"):
        baseline = _mean_window(result, name, 100.0, TILT_START - 2.0)
        late = _mean_window(result, name, TILT_END - 120.0, TILT_END)
        pooling += late - baseline
    assert CAUDAL_POOLING_BAND_ML[0] <= pooling <= CAUDAL_POOLING_BAND_ML[1]


@pytest.mark.parametrize("offset_s", [120.0, 300.0])
def test_healthy_70_degree_co_and_sv_meet_preserved_group_anchors(offset_s):
    """REF-ZAIDI-2000 70-degree two/five-minute plausibility comparisons."""
    result = run_phenotype("healthy-reference", "passive-tilt-70")
    index = int(np.argmin(np.abs(result.time - (TILT_START + offset_s))))
    for name, band in (
        ("cardiac_output", ZAIDI_CO_REDUCTION_BAND_PCT),
        ("stroke_volume", ZAIDI_SV_REDUCTION_BAND_PCT),
    ):
        baseline = _mean_window(result, name, 100.0, TILT_START - 2.0)
        reduction = _reduction_pct(baseline, float(result.outputs[name][index]))
        assert band[0] <= reduction <= band[1], (
            f"{name} reduction {reduction:.3f}% at {offset_s:.0f} s is outside "
            f"the preserved {band}% group anchor"
        )


@pytest.mark.parametrize("offset_s", [120.0, 300.0])
def test_healthy_60_degree_stroke_volume_meets_preserved_group_anchor(offset_s):
    result = run_phenotype("healthy-reference", "passive-tilt-60")
    index = int(np.argmin(np.abs(result.time - (TILT_START + offset_s))))
    baseline = _mean_window(result, "stroke_volume", 100.0, TILT_START - 2.0)
    reduction = _reduction_pct(baseline, float(result.outputs["stroke_volume"][index]))
    assert ZAIDI_SV_REDUCTION_BAND_PCT[0] <= reduction <= ZAIDI_SV_REDUCTION_BAND_PCT[1]


def test_healthy_cerebral_pressure_response_meets_preserved_soft_band():
    result = run_phenotype("healthy-reference", "tilt-recovery")
    baseline = _mean_window(result, "cerebral_flow_index", 100.0, TILT_START - 2.0)
    end_tilt = _mean_window(result, "cerebral_flow_index", TILT_END - 10.0, TILT_END)
    reduction = _reduction_pct(baseline, end_tilt)
    assert HEALTHY_CFI_REDUCTION_BAND_PCT[0] <= reduction <= HEALTHY_CFI_REDUCTION_BAND_PCT[1]


def test_remediation_preserves_volume_state_layout():
    """Stage 1.2 calibrates geometry; it must not remove Stage 1.1 compartments."""
    assert STATE_NAMES[:5] == (
        "arterial_volume",
        "central_venous_volume",
        "splanchnic_venous_volume",
        "lower_limb_venous_volume",
        "other_systemic_venous_volume",
    )
