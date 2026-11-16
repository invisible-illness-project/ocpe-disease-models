"""VAL-ME-PEM: delayed PEM onset and prolonged recovery (disease_phenotype).

Acceptance (registry): PEM is below 0.01 during exertion and the first hour;
subsequent peak exceeds 0.05; peak occurs after exertion; healthy PEM remains
zero under the same protocol; recovery is slower than a simple
immediate-fatigue response.

Protocol: repeated-exertion-recovery (baseline 0-3600 s, exertion day 1
3600-4800 s, recovery, exertion day 2 at 86400 s, approximately 48 h of
post-day-2 follow-up within a 72 h total protocol).
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

pytestmark = pytest.mark.phenotype

EXERTION_1 = (3600.0, 4800.0)
EXERTION_2 = (86400.0, 87600.0)
FIRST_HOUR_AFTER_EXERTION = (4800.0, 8400.0)


def _window(result, start, end):
    mask = (result.time >= start) & (result.time <= end)
    return result.outputs["pem_severity"][mask]


def test_pem_below_threshold_during_exertion(mecfs_repeated_exertion_result):
    pem = _window(mecfs_repeated_exertion_result, *EXERTION_1)
    assert float(pem.max()) < 0.01


def test_pem_below_threshold_during_first_hour(mecfs_repeated_exertion_result):
    """PEM must remain < 0.01 for the first hour after exertion ends;
    otherwise onset is immediate fatigue rather than delayed PEM."""
    pem = _window(mecfs_repeated_exertion_result, *FIRST_HOUR_AFTER_EXERTION)
    peak_first_hour = float(pem.max())
    assert peak_first_hour < 0.01, (
        f"PEM reached {peak_first_hour:.4f} within the first hour after "
        "exertion ended (PEM crossed 0.01 at ~30 min post-exertion); onset is "
        "not delayed as required by VAL-ME-PEM"
    )


def test_subsequent_pem_peak_exceeds_threshold(mecfs_repeated_exertion_result):
    pem = mecfs_repeated_exertion_result.outputs["pem_severity"]
    assert float(pem.max()) > 0.05


def test_pem_peak_occurs_after_exertion(mecfs_repeated_exertion_result):
    t = mecfs_repeated_exertion_result.time
    pem = mecfs_repeated_exertion_result.outputs["pem_severity"]
    t_peak = float(t[int(np.argmax(pem))])
    assert t_peak > EXERTION_1[1], f"PEM peak at {t_peak} s is not after exertion"


def test_healthy_pem_remains_zero_under_same_protocol(healthy_repeated_exertion_result):
    pem = healthy_repeated_exertion_result.outputs["pem_severity"]
    assert float(np.max(pem)) == 0.0


def test_recovery_slower_than_immediate_fatigue(mecfs_repeated_exertion_result):
    """An immediate-fatigue response would track the exertional-load state
    (tau = 1800 s); PEM must decay far more slowly after its peak."""
    result = mecfs_repeated_exertion_result
    t = result.time
    pem = result.outputs["pem_severity"]
    load = result.outputs["exertional_load"]

    # Immediate-fatigue reference: load half-life after the day-2 bout ends.
    load_peak = float(load[(t >= EXERTION_2[0]) & (t <= EXERTION_2[1])].max())
    after = t >= EXERTION_2[1]
    t_after = t[after]
    load_after = load[after]
    half_load = t_after[load_after <= 0.5 * load_peak]
    t_half_load = float(half_load[0] - EXERTION_2[1])

    # PEM half-life after its peak.
    i_peak = int(np.argmax(pem))
    t_peak = t[i_peak]
    pem_after = pem[i_peak:]
    half_pem = t[i_peak:][pem_after <= 0.5 * pem[i_peak]]
    assert len(half_pem) > 0, "PEM does not recover within the follow-up window"
    t_half_pem = float(half_pem[0] - t_peak)

    assert t_half_pem > 10.0 * t_half_load, (
        f"PEM half-life ({t_half_pem:.0f} s) is not clearly slower than the "
        f"immediate-fatigue load half-life ({t_half_load:.0f} s)"
    )
