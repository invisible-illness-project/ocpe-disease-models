"""VAL-UNCERTAINTY: assumption uncertainty propagation.

Registry layer ``sensitivity_uncertainty`` (pytest marker
``sensitivity_uncertainty`` per pyproject.toml). A small deterministic parameter grid reports output ranges
and scenario ranking stability. Every sampled point is a deterministic
scenario, not a patient; no population probabilities are implied.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pytest

TESTS_DIR = Path(__file__).resolve().parents[1]
SRC = TESTS_DIR.parent / "src"
for _p in (str(TESTS_DIR), str(SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from conftest import orthostatic_metrics  # noqa: E402

from ocpe_disease_models.config import load_protocol  # noqa: E402
from ocpe_disease_models.models.shared.model import (  # noqa: E402
    ComputationalPatient,
    ModelParameters,
    ProtocolSegment,
)

pytestmark = pytest.mark.sensitivity_uncertainty

SCENARIO_LABEL = "deterministic_scenario_not_a_patient"

# Heights corresponding to the former 8-10 mmHg upright gravity-offset range
# (mmHg = 0.7356 * height_cm at 90 degrees).
TILT_GRID = {
    "lower_limb_hydrostatic_height_cm": (8.0 / 0.7356, 10.0 / 0.7356),
    "lower_limb_resistance_sympathetic_gain": (0.35, 0.8),
}
PEM_GRID_VALUES = (0.0, 12.0, 16.0, 20.0)  # includes the explicit no-PEM bound

# Shortened deterministic exertion scenario: 1 h baseline, 20 min exertion,
# 47 h recovery (PEM peak occurs near 12 h, well inside the horizon).
PEM_PROTOCOL = [
    ProtocolSegment(start=0.0, end=3600.0, upright=0.0, exertion=0.0, label="baseline"),
    ProtocolSegment(start=3600.0, end=4800.0, upright=0.0, exertion=0.8, label="exertion"),
    ProtocolSegment(start=4800.0, end=172800.0, upright=0.0, exertion=0.0, label="recovery"),
]


def _tilt_grid_records():
    segments, _ = load_protocol("head-up-tilt")
    records = []
    for height in TILT_GRID["lower_limb_hydrostatic_height_cm"]:
        for gain in TILT_GRID["lower_limb_resistance_sympathetic_gain"]:
            overrides = {
                "lower_limb_hydrostatic_height_cm": height,
                "lower_limb_resistance_sympathetic_gain": gain,
            }
            patient = ComputationalPatient(
                ModelParameters().replaced(overrides), phenotype_id="uncertainty-scenario"
            )
            result = patient.simulate(segments, sample_interval=2.0, max_step=2.0)
            metrics = orthostatic_metrics(result)
            records.append(
                {
                    "label": SCENARIO_LABEL,
                    "parameters": overrides,
                    "configuration_sha256": result.metadata["configuration_sha256"],
                    "orthostatic_heart_rate_rise_bpm": metrics["hr_rise"],
                    "mean_arterial_pressure_final_mmHg": metrics["map_final"],
                }
            )
    return records


def _pem_grid_records():
    from ocpe_disease_models.config import load_phenotype

    mecfs_overrides = dict(load_phenotype("mecfs-pem").parameter_overrides)
    records = []
    for gain in PEM_GRID_VALUES:
        parameters = ModelParameters().replaced(
            {**mecfs_overrides, "pem_response_gain": gain}
        )
        patient = ComputationalPatient(parameters, phenotype_id="uncertainty-scenario")
        result = patient.simulate(PEM_PROTOCOL, sample_interval=600.0, max_step=300.0)
        records.append(
            {
                "label": SCENARIO_LABEL,
                "parameters": {"pem_response_gain": gain},
                "configuration_sha256": result.metadata["configuration_sha256"],
                "pem_peak": float(np.max(result.outputs["pem_severity"])),
                "functional_capacity_min": float(
                    np.min(result.outputs["functional_capacity"])
                ),
            }
        )
    return records


@pytest.fixture(scope="module")
def tilt_records():
    return _tilt_grid_records()


@pytest.fixture(scope="module")
def pem_records():
    return _pem_grid_records()


def _check_records(records, output_names):
    assert len(records) >= 3
    hashes = set()
    for record in records:
        # Every sampled point is explicitly a deterministic scenario.
        assert record["label"] == SCENARIO_LABEL
        assert "patient" not in record["label"].replace("not_a_patient", "")
        assert re.fullmatch(r"[0-9a-f]{64}", record["configuration_sha256"])
        hashes.add(record["configuration_sha256"])
        for name in output_names:
            assert np.isfinite(record[name])
    assert len(hashes) == len(records), "grid points must have distinct configurations"


def test_tilt_grid_reports_ranges_with_configuration_hashes(tilt_records):
    _check_records(
        tilt_records,
        ["orthostatic_heart_rate_rise_bpm", "mean_arterial_pressure_final_mmHg"],
    )
    rises = [r["orthostatic_heart_rate_rise_bpm"] for r in tilt_records]
    maps = [r["mean_arterial_pressure_final_mmHg"] for r in tilt_records]
    ranges = {
        "hr_rise_bpm": {"min": min(rises), "max": max(rises)},
        "map_mmHg": {"min": min(maps), "max": max(maps)},
    }
    assert ranges["hr_rise_bpm"]["max"] > ranges["hr_rise_bpm"]["min"]
    assert ranges["map_mmHg"]["max"] >= ranges["map_mmHg"]["min"]


def test_tilt_grid_scenario_ranking_is_stable(tilt_records):
    """Stronger pooling (greater hydrostatic height) ranks above weaker pooling
    at every sampled compensation level; stronger compensation ranks lower."""
    def rise(height, gain):
        return next(
            r["orthostatic_heart_rate_rise_bpm"]
            for r in tilt_records
            if r["parameters"]["lower_limb_hydrostatic_height_cm"] == height
            and r["parameters"]["lower_limb_resistance_sympathetic_gain"] == gain
        )

    lo_height, hi_height = TILT_GRID["lower_limb_hydrostatic_height_cm"]
    for gain in TILT_GRID["lower_limb_resistance_sympathetic_gain"]:
        assert rise(hi_height, gain) > rise(lo_height, gain)
    for height in TILT_GRID["lower_limb_hydrostatic_height_cm"]:
        assert rise(height, 0.8) < rise(height, 0.35)


def test_pem_grid_reports_ranges_with_configuration_hashes(pem_records):
    _check_records(pem_records, ["pem_peak", "functional_capacity_min"])
    peaks = [r["pem_peak"] for r in pem_records]
    capacities = [r["functional_capacity_min"] for r in pem_records]
    assert max(peaks) > min(peaks)
    assert min(capacities) < max(capacities)


def test_pem_grid_scenario_ranking_is_stable(pem_records):
    """PEM peak increases and minimum capacity decreases monotonically with the
    declared response-gain assumption."""
    ordered = sorted(pem_records, key=lambda r: r["parameters"]["pem_response_gain"])
    peaks = [r["pem_peak"] for r in ordered]
    capacities = [r["functional_capacity_min"] for r in ordered]
    assert peaks == sorted(peaks)
    assert capacities == sorted(capacities, reverse=True)
    # A zero-gain scenario is the no-PEM bound of the assumption range.
    assert ordered[0]["parameters"]["pem_response_gain"] == 0.0
    assert ordered[0]["pem_peak"] == 0.0
    assert all(r["pem_peak"] > 0.0 for r in ordered[1:])
