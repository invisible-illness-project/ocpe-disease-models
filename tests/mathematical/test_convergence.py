"""VAL-MATH-CONVERGENCE: solver convergence and bounded states (mathematical).

Tightening rtol/atol and max_step must change key summary metrics by less than
0.1 bpm, 0.1 mmHg, or 0.001 normalized units, and all states/outputs must be
finite in all demonstrated protocols. Numerical convergence does not establish
model truth; it detects numerical artifacts.
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

from conftest import run_phenotype  # noqa: E402

pytestmark = pytest.mark.mathematical

TIGHT = {"rtol": 1e-9, "atol": 1e-11, "max_step": 1.0}

HR_TOLERANCE_BPM = 0.1
MAP_TOLERANCE_MMHG = 0.1
NORMALIZED_TOLERANCE = 0.001

CONVERGENCE_RUNS = (
    ("healthy-reference", "resting-baseline"),
    ("healthy-reference", "head-up-tilt"),
    ("pots-neuropathic", "head-up-tilt"),
    ("pots-hyperadrenergic", "head-up-tilt"),
    ("healthy-reference", "tilt-recovery"),
    ("mecfs-pem", "tilt-recovery"),
)


@pytest.mark.parametrize(
    ("phenotype_id", "protocol_id"),
    CONVERGENCE_RUNS,
    ids=[f"{p}__{pr}" for p, pr in CONVERGENCE_RUNS],
)
def test_tighter_tolerances_change_key_metrics_negligibly(phenotype_id, protocol_id):
    nominal = run_phenotype(phenotype_id, protocol_id)
    tight = run_phenotype(phenotype_id, protocol_id, **TIGHT)

    assert abs(
        nominal.summary()["heart_rate_final_bpm"]
        - tight.summary()["heart_rate_final_bpm"]
    ) < HR_TOLERANCE_BPM
    assert abs(
        nominal.summary()["mean_arterial_pressure_final_mmHg"]
        - tight.summary()["mean_arterial_pressure_final_mmHg"]
    ) < MAP_TOLERANCE_MMHG
    if "orthostatic_heart_rate_rise_bpm" in nominal.summary():
        assert abs(
            nominal.summary()["orthostatic_heart_rate_rise_bpm"]
            - tight.summary()["orthostatic_heart_rate_rise_bpm"]
        ) < HR_TOLERANCE_BPM
    # Normalized constructs converge in normalized units.
    assert abs(
        nominal.outputs["cerebral_flow_index"][-1] - tight.outputs["cerebral_flow_index"][-1]
    ) < NORMALIZED_TOLERANCE
    assert abs(nominal.outputs["pem_severity"][-1] - tight.outputs["pem_severity"][-1]) < (
        NORMALIZED_TOLERANCE
    )


@pytest.mark.parametrize(
    ("phenotype_id", "protocol_id"),
    CONVERGENCE_RUNS,
    ids=[f"{p}__{pr}" for p, pr in CONVERGENCE_RUNS],
)
def test_all_states_and_outputs_are_finite(phenotype_id, protocol_id):
    result = run_phenotype(phenotype_id, protocol_id)
    assert np.all(np.isfinite(result.states))
    for name, values in result.outputs.items():
        assert np.all(np.isfinite(values)), f"non-finite values in output {name!r}"
    assert np.all(np.isfinite(result.time))
