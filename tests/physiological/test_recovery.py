"""VAL-PHYS-RECOVERY: post-tilt cerebral recovery (layer: physiological).

Acceptance: healthy cerebral index returns within 0.01 of baseline by 120 s
after return to supine; ME/CFS recovery is slower than decline and remains
finite; no negative cerebral index occurs. Recovery dynamics are tested
separately from end-tilt responses.
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

pytestmark = pytest.mark.physiological

# tilt-recovery protocol geometry (simulations/orthostatic/tilt-recovery.yaml)
TILT_START = 120.0
TILT_END = 600.0
PROTOCOL_END = 1200.0


def _cerebral(result):
    t = result.time
    cfi = result.outputs["cerebral_flow_index"]
    baseline = float(cfi[(t >= 0.0) & (t <= TILT_START - 2.0)].mean())
    end_tilt = float(cfi[(t >= TILT_END - 10.0) & (t <= TILT_END)].mean())
    return t, cfi, baseline, end_tilt


def _crossing_time(t, cfi, threshold, start, above=True):
    window = t >= start
    times = t[window]
    values = cfi[window]
    mask = values >= threshold if above else values <= threshold
    return float(times[mask][0] - start) if np.any(mask) else None


def test_healthy_cerebral_index_recovers_within_120s(healthy_tilt_recovery_result):
    t, cfi, baseline, _ = _cerebral(healthy_tilt_recovery_result)
    value_at_120s = float(cfi[np.argmin(np.abs(t - (TILT_END + 120.0)))])
    assert abs(value_at_120s - baseline) <= 0.01, (
        f"healthy cerebral index {value_at_120s:.4f} not within 0.01 of "
        f"baseline {baseline:.4f} at 120 s post-tilt"
    )


def test_mecfs_recovery_is_slower_than_decline(mecfs_tilt_recovery_result):
    t, cfi, baseline, end_tilt = _cerebral(mecfs_tilt_recovery_result)
    final = float(cfi[-1])
    drop = baseline - end_tilt
    assert drop > 0.0
    t_half_decline = _crossing_time(t, cfi, baseline - 0.5 * drop, TILT_START, above=False)
    # Recovery half-time relative to the recovery actually achieved in-protocol.
    t_half_recovery = _crossing_time(
        t, cfi, end_tilt + 0.5 * (final - end_tilt), TILT_END, above=True
    )
    assert t_half_decline is not None and t_half_recovery is not None
    assert t_half_recovery > t_half_decline, (
        f"ME/CFS cerebral recovery half-time ({t_half_recovery:.1f} s) is not "
        f"slower than decline half-time ({t_half_decline:.1f} s)"
    )
    # ME/CFS recovery is incomplete at the point where healthy has recovered.
    healthy_recovered_gap = 0.01
    value_at_120s = float(cfi[np.argmin(np.abs(t - (TILT_END + 120.0)))])
    assert abs(value_at_120s - baseline) > healthy_recovered_gap


def test_mecfs_cerebral_trace_remains_finite(mecfs_tilt_recovery_result):
    _, cfi, _, _ = _cerebral(mecfs_tilt_recovery_result)
    assert np.all(np.isfinite(cfi))


@pytest.mark.parametrize("fixture", ["healthy_tilt_recovery_result", "mecfs_tilt_recovery_result"])
def test_no_negative_cerebral_index(fixture, request):
    result = request.getfixturevalue(fixture)
    assert float(result.outputs["cerebral_flow_index"].min()) >= 0.0
