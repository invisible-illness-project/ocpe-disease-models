"""VAL-MATH-CONSERVATION: stressed-volume conservation (layer: mathematical).

The compartment equations imply
    dV_arterial + dV_central + dV_splanchnic + dV_lower_limb + dV_other = 0
exactly, so total stressed volume is an invariant. Drift would reveal an
implementation or solver error.

Acceptance: max absolute volume drift < 1e-6 mL over baseline and orthostatic
runs; instantaneous RHS volume derivatives sum to zero within floating-point
tolerance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

TESTS_DIR = Path(__file__).resolve().parents[1]
SRC = TESTS_DIR.parent / "src"
for _p in (str(TESTS_DIR), str(SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from conftest import VOLUME_STATE_COUNT, run_phenotype, stressed_volume_drift  # noqa: E402

pytestmark = pytest.mark.mathematical

VOLUME_DRIFT_TOLERANCE_ML = 1e-6

CONSERVATION_RUNS = (
    ("healthy-reference", "resting-baseline"),
    ("healthy-reference", "head-up-tilt"),
    ("healthy-reference", "tilt-recovery"),
    ("pots-neuropathic", "head-up-tilt"),
    ("pots-hyperadrenergic", "head-up-tilt"),
    ("pots-hypovolemic", "head-up-tilt"),
    ("eds-heds-vascular", "head-up-tilt"),
    ("long-covid-autonomic", "head-up-tilt"),
    ("pots-neuropathic", "walking"),
    ("eds-heds-vascular", "sustained-contraction"),
)


@pytest.mark.parametrize(
    ("phenotype_id", "protocol_id"),
    CONSERVATION_RUNS,
    ids=[f"{p}__{pr}" for p, pr in CONSERVATION_RUNS],
)
def test_total_stressed_volume_is_invariant(phenotype_id, protocol_id):
    result = run_phenotype(phenotype_id, protocol_id)
    drift = stressed_volume_drift(result)
    assert drift < VOLUME_DRIFT_TOLERANCE_ML, (
        f"{phenotype_id}/{protocol_id}: total stressed volume drifted by "
        f"{drift:.3e} mL (tolerance {VOLUME_DRIFT_TOLERANCE_ML} mL)"
    )


def test_rhs_volume_derivatives_sum_to_zero_exactly(run_cached):
    """All five instantaneous volume derivatives telescope exactly."""
    from ocpe_disease_models.config import compose_phenotypes

    trajectory = run_cached("healthy-reference", "head-up-tilt")
    patient = compose_phenotypes(["healthy-reference"])
    # Sample states along the trajectory, including orthostatic stress.
    for idx in range(0, len(trajectory.time), 25):
        t = float(trajectory.time[idx])
        y = trajectory.states[:, idx]
        rhs = patient.rhs(t, y, trajectory.protocol)
        volume_sum = float(rhs[:VOLUME_STATE_COUNT].sum())
        scale = max(1.0, float(np.abs(rhs[:VOLUME_STATE_COUNT]).max()))
        assert abs(volume_sum) <= 1e-12 * scale, (
            f"volume derivatives do not telescope at t={t}: sum={volume_sum}"
        )


def test_conservation_holds_under_reduced_volume(run_cached):
    """Hypovolemia scales the invariant; it must still be conserved."""
    result = run_cached("pots-hypovolemic", "head-up-tilt")
    initial_total = float(result.states[:VOLUME_STATE_COUNT, 0].sum())
    healthy_total = 150.0 + 700.0 + 700.0 + 500.0 + 500.0
    assert initial_total == pytest.approx(0.92 * healthy_total, rel=1e-12)
    assert stressed_volume_drift(result) < VOLUME_DRIFT_TOLERANCE_ML


def test_residual_bed_volume_follows_its_own_flow_balance(run_cached):
    """The other-systemic compartment integrates dV_o = Q_o,a - Q_o,v exactly."""
    from ocpe_disease_models.config import compose_phenotypes
    from ocpe_disease_models.models.shared.model import STATE_NAMES

    trajectory = run_cached("healthy-reference", "head-up-tilt")
    patient = compose_phenotypes(["healthy-reference"])
    vo_idx = STATE_NAMES.index("other_systemic_venous_volume")
    for idx in range(0, len(trajectory.time), 25):
        t = float(trajectory.time[idx])
        y = trajectory.states[:, idx]
        derived = patient._derived(t, y, trajectory.protocol)
        rhs = patient.rhs(t, y, trajectory.protocol)
        assert rhs[vo_idx] == pytest.approx(
            derived["other_systemic_arterial_flow"] - derived["other_systemic_venous_return"],
            rel=1e-12,
            abs=1e-12,
        )
    # The residual compartment is part of the conserved total.
    assert stressed_volume_drift(trajectory) < VOLUME_DRIFT_TOLERANCE_ML
