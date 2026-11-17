#!/usr/bin/env python3
"""Generate the Stage 1.1 time-resolved scientific comparison matrix.

The report is a deterministic research-scenario comparison, not a synthetic
cohort, fitted patient dataset, or clinical validation. Threshold misses are
reported as misses; this script never changes model parameters or criteria.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocpe_disease_models.config import compose_phenotypes, load_protocol  # noqa: E402

SOLVER_KEYS = {"sample_interval", "max_step", "rtol", "atol", "seed"}
OFFSETS_S = (0.0, 10.0, 30.0, 60.0, 120.0, 300.0)
GRADED_PROTOCOLS = (
    "passive-tilt-30",
    "passive-tilt-45",
    "passive-tilt-60",
    "passive-tilt-70",
)
TILT_PHENOTYPES = (
    "healthy-reference",
    "pots-neuropathic",
    "pots-hyperadrenergic",
    "pots-hypovolemic",
    "pots-mixed",
    "long-covid-autonomic",
    "long-covid-exertional",
    "eds-heds-vascular",
    "mecfs-pem",
)
CEREBRAL_PROTOCOLS = (
    "pressure-reduction",
    "co2-reduction",
    "combined-pressure-co2-reduction",
    "pressure-recovery-persistent-hypocapnia",
    "co2-recovery-persistent-pressure-reduction",
)


def _run(phenotype_id: str, protocol_id: str):
    patient = compose_phenotypes([phenotype_id], root=ROOT)
    segments, settings = load_protocol(protocol_id, root=ROOT)
    solver = {key: value for key, value in settings.items() if key in SOLVER_KEYS}
    return patient.simulate(segments, **solver)


def _mean(result, name: str, start: float, end: float) -> float:
    mask = (result.time >= start) & (result.time <= end)
    if not np.any(mask):
        raise ValueError(f"No samples for {name} in [{start}, {end}]")
    return float(np.mean(result.outputs[name][mask]))


def _point(result, time_s: float, name: str) -> float:
    index = int(np.argmin(np.abs(result.time - time_s)))
    return float(result.outputs[name][index])


def _orthostatic_record(phenotype_id: str, protocol_id: str) -> dict[str, Any]:
    result = _run(phenotype_id, protocol_id)
    first_upright = next(
        segment for segment in result.protocol if segment.resolved_tilt_angle_deg() > 0
    )
    first_index = next(
        index for index, segment in enumerate(result.protocol) if segment is first_upright
    )
    start = first_upright.start
    upright_end = first_upright.end
    for segment in result.protocol[first_index + 1 :]:
        if segment.resolved_tilt_angle_deg() <= 0:
            break
        upright_end = segment.end
    end = min(upright_end, float(result.time[-1]))
    baseline: dict[str, float] = {}
    for name in (
        "heart_rate",
        "stroke_volume",
        "cardiac_output",
        "mean_arterial_pressure",
        "cerebral_flow_index",
        "venous_return",
    ):
        baseline[name] = _mean(result, name, 0.0, max(0.0, start - 2.0))
    points = []
    for offset in OFFSETS_S:
        if start + offset > end:
            continue
        time_s = start + offset
        hr = _point(result, time_s, "heart_rate")
        sv = _point(result, time_s, "stroke_volume")
        co = _point(result, time_s, "cardiac_output")
        points.append(
            {
                "offset_s": offset,
                "time_s": time_s,
                "heart_rate_bpm": hr,
                "heart_rate_rise_bpm": hr - baseline["heart_rate"],
                "stroke_volume_change_pct": 100.0 * (sv / baseline["stroke_volume"] - 1.0),
                "cardiac_output_change_pct": 100.0 * (co / baseline["cardiac_output"] - 1.0),
                "mean_arterial_pressure_mmHg": _point(result, time_s, "mean_arterial_pressure"),
                "brain_arterial_pressure_mmHg": _point(result, time_s, "brain_arterial_pressure"),
                "cerebral_flow_index": _point(result, time_s, "cerebral_flow_index"),
                "end_tidal_co2_mmHg": _point(result, time_s, "end_tidal_co2_mmHg"),
                "tilt_angle_deg": _point(result, time_s, "tilt_angle_deg"),
            }
        )
    early_end = min(start + 30.0, end)
    peak_end = min(start + 300.0, end)
    early_co = result.metric("cardiac_output", start, early_end, "min")
    early_sv = result.metric("stroke_volume", start, early_end, "min")
    sustained_start = max(start, end - 120.0)
    sustained_hr = _mean(result, "heart_rate", sustained_start, end)
    total = result.states[:5].sum(axis=0)
    record = {
        "phenotype_id": phenotype_id,
        "protocol_id": protocol_id,
        "configuration_sha256": result.metadata["configuration_sha256"],
        "solver": result.metadata["solver"],
        "baseline_window_s": [0.0, max(0.0, start - 2.0)],
        "baseline": baseline,
        "points": points,
        "early_upright_window_s": [start, early_end],
        "early_min_cardiac_output_change_pct": 100.0
        * (early_co / baseline["cardiac_output"] - 1.0),
        "early_min_stroke_volume_change_pct": 100.0
        * (early_sv / baseline["stroke_volume"] - 1.0),
        "early_min_venous_return_mL_s": result.metric("venous_return", start, early_end, "min"),
        "peak_window_s": [start, peak_end],
        "peak_heart_rate_rise_bpm": result.metric("heart_rate", start, peak_end, "max")
        - baseline["heart_rate"],
        "sustained_window_s": [sustained_start, end],
        "sustained_heart_rate_rise_bpm": sustained_hr - baseline["heart_rate"],
        "upright_end_mean_arterial_pressure_mmHg": _mean(
            result, "mean_arterial_pressure", max(start, end - 10.0), end
        ),
        "end_cerebral_flow_reduction_pct": 100.0
        * (1.0 - _mean(result, "cerebral_flow_index", end - 10.0, end) / baseline["cerebral_flow_index"]),
        "maximum_five_volume_drift_mL": float(np.max(np.abs(total - total[0]))),
    }
    if any(
        segment.start >= upright_end and segment.resolved_tilt_angle_deg() == 0
        for segment in result.protocol
    ):
        recovery_points = []
        for offset in OFFSETS_S:
            time_s = upright_end + offset
            if time_s > float(result.time[-1]):
                continue
            hr = _point(result, time_s, "heart_rate")
            sv = _point(result, time_s, "stroke_volume")
            co = _point(result, time_s, "cardiac_output")
            recovery_points.append(
                {
                    "offset_s": offset,
                    "time_s": time_s,
                    "heart_rate_rise_bpm": hr - baseline["heart_rate"],
                    "stroke_volume_change_pct": 100.0 * (sv / baseline["stroke_volume"] - 1.0),
                    "cardiac_output_change_pct": 100.0 * (co / baseline["cardiac_output"] - 1.0),
                    "cerebral_flow_index": _point(result, time_s, "cerebral_flow_index"),
                    "tilt_angle_deg": _point(result, time_s, "tilt_angle_deg"),
                }
            )
        record["tilt_back_recovery_points"] = recovery_points
    if phenotype_id.startswith("pots-") or phenotype_id == "long-covid-autonomic":
        record["sustained_30_bpm_criterion"] = {
            "threshold_bpm": 30.0,
            "status": "PASS" if record["sustained_heart_rate_rise_bpm"] >= 30.0 else "FAIL",
            "interpretation": "Unchanged scenario criterion; failure is retained without gain recalibration.",
        }
    return record


def _cerebral_record(protocol_id: str) -> dict[str, Any]:
    result = _run("healthy-reference", protocol_id)
    final = {name: float(result.outputs[name][-1]) for name in (
        "mean_arterial_pressure",
        "brain_arterial_pressure",
        "cerebral_perfusion_pressure",
        "end_tidal_co2_mmHg",
        "cerebral_pressure_target",
        "cerebral_co2_factor",
        "cerebral_flow_target",
        "cerebral_flow_index",
    )}
    total = result.states[:5].sum(axis=0)
    return {
        "protocol_id": protocol_id,
        "configuration_sha256": result.metadata["configuration_sha256"],
        "segments": [
            {
                "start": segment.start,
                "end": segment.end,
                "label": segment.label,
                "tilt_angle_deg": segment.resolved_tilt_angle_deg(),
                "end_tidal_co2_mmHg": segment.end_tidal_co2_mmHg,
            }
            for segment in result.protocol
        ],
        "final": final,
        "maximum_five_volume_drift_mL": float(np.max(np.abs(total - total[0]))),
    }


def _empirical_comparisons(orthostatic: list[dict[str, Any]]) -> list[dict[str, Any]]:
    comparisons = []
    for record in orthostatic:
        if record["phenotype_id"] != "healthy-reference" or record["protocol_id"] not in {
            "passive-tilt-60",
            "passive-tilt-70",
        }:
            continue
        for point in record["points"]:
            if point["offset_s"] not in {120.0, 300.0}:
                continue
            for metric, band in (
                ("cardiac_output_change_pct", (-20.0, -17.0)),
                ("stroke_volume_change_pct", (-34.0, -28.0)),
            ):
                value = point[metric]
                comparisons.append(
                    {
                        "reference_id": "REF-ZAIDI-2000",
                        "protocol_id": record["protocol_id"],
                        "offset_s": point["offset_s"],
                        "metric": metric,
                        "model_value_pct": value,
                        "published_group_range_pct": list(band),
                        "status": "WITHIN" if band[0] <= value <= band[1] else "MISS",
                        "interpretation": "Protocol-specific healthy group plausibility comparison, not a fitted target or external validation.",
                    }
                )
    return comparisons


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 1.1 time-resolved scientific comparison matrix",
        "",
        "Deterministic research scenarios only. Published group ranges are heterogeneous plausibility anchors, not fitted patient data or clinical validation. No parameter was adjusted to manufacture agreement.",
        "",
        "## Preserved criterion outcomes",
        "",
        "| Phenotype | Protocol | Sustained HR rise (bpm) | Criterion | Upright-end MAP (mmHg) | End-tilt CFI reduction (%) |",
        "|---|---|---:|---|---:|---:|",
    ]
    for row in payload["orthostatic"]:
        criterion = row.get("sustained_30_bpm_criterion", {}).get("status", "n/a")
        lines.append(
            f"| {row['phenotype_id']} | {row['protocol_id']} | {row['sustained_heart_rate_rise_bpm']:.3f} "
            f"| {criterion} | {row['upright_end_mean_arterial_pressure_mmHg']:.3f} | {row['end_cerebral_flow_reduction_pct']:.3f} |"
        )
    lines.extend([
        "",
        "## Predeclared healthy window summaries",
        "",
        "Baseline is [0, t0−2 s]; early minima use [t0, t0+30 s]; peak HR uses [t0, t0+300 s], clipped to the continuous upright bout.",
        "",
        "| Protocol | Early minimum CO change (%) | Early minimum SV change (%) | Peak HR rise (bpm) | Sustained HR rise (bpm) |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in payload["orthostatic"]:
        if row["phenotype_id"] == "healthy-reference":
            lines.append(
                f"| {row['protocol_id']} | {row['early_min_cardiac_output_change_pct']:.3f} "
                f"| {row['early_min_stroke_volume_change_pct']:.3f} | {row['peak_heart_rate_rise_bpm']:.3f} "
                f"| {row['sustained_heart_rate_rise_bpm']:.3f} |"
            )
    lines.extend([
        "",
        "## Time-resolved healthy responses",
        "",
        "Offsets are measured from the upright segment start; posture during the declared transition is explicitly reported in JSON.",
        "",
        "| Protocol | Offset (s) | HR rise (bpm) | CO change (%) | SV change (%) | MAP (mmHg) | CFI |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in payload["orthostatic"]:
        if row["phenotype_id"] != "healthy-reference":
            continue
        for point in row["points"]:
            lines.append(
                f"| {row['protocol_id']} | {point['offset_s']:.0f} | {point['heart_rate_rise_bpm']:.3f} "
                f"| {point['cardiac_output_change_pct']:.3f} | {point['stroke_volume_change_pct']:.3f} "
                f"| {point['mean_arterial_pressure_mmHg']:.3f} | {point['cerebral_flow_index']:.5f} |"
            )
    recovery_rows = [
        (row, point)
        for row in payload["orthostatic"]
        for point in row.get("tilt_back_recovery_points", [])
    ]
    if recovery_rows:
        lines.extend([
            "",
            "## Tilt-back recovery",
            "",
            "Offsets are measured from the start of the supine recovery segment; the declared 30-second return transition is included.",
            "",
            "| Protocol | Offset (s) | HR rise vs supine baseline (bpm) | CO change (%) | SV change (%) | CFI | Tilt (deg) |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row, point in recovery_rows:
            lines.append(
                f"| {row['protocol_id']} | {point['offset_s']:.0f} | {point['heart_rate_rise_bpm']:.3f} "
                f"| {point['cardiac_output_change_pct']:.3f} | {point['stroke_volume_change_pct']:.3f} "
                f"| {point['cerebral_flow_index']:.5f} | {point['tilt_angle_deg']:.2f} |"
            )
    lines.extend([
        "",
        "## Protocol-specific empirical comparisons",
        "",
        "| Reference | Protocol | Offset (s) | Metric | Model (%) | Published range (%) | Status |",
        "|---|---|---:|---|---:|---|---|",
    ])
    for row in payload["empirical_comparisons"]:
        lines.append(
            f"| {row['reference_id']} | {row['protocol_id']} | {row['offset_s']:.0f} | {row['metric']} "
            f"| {row['model_value_pct']:.3f} | {row['published_group_range_pct'][0]} to {row['published_group_range_pct'][1]} | {row['status']} |"
        )
    lines.extend([
        "",
        "## Cerebral isolation experiments",
        "",
        "| Protocol | Final brain arterial pressure (mmHg) | Final ETCO2 (mmHg) | Pressure target | CO2 factor | CFI |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in payload["cerebral_experiments"]:
        final = row["final"]
        lines.append(
            f"| {row['protocol_id']} | {final['brain_arterial_pressure']:.3f} | {final['end_tidal_co2_mmHg']:.1f} "
            f"| {final['cerebral_pressure_target']:.5f} | {final['cerebral_co2_factor']:.5f} | {final['cerebral_flow_index']:.5f} |"
        )
    misses = sum(row["status"] == "MISS" for row in payload["empirical_comparisons"])
    criterion_failures = sum(
        row.get("sustained_30_bpm_criterion", {}).get("status") == "FAIL"
        for row in payload["orthostatic"]
    )
    lines.extend([
        "",
        "## Readiness interpretation",
        "",
        f"- Empirical CO/SV comparisons outside their preserved published ranges: **{misses}**.",
        f"- POTS/Long-COVID-autonomic sustained-HR criterion failures: **{criterion_failures}**.",
        "- Software execution and exact volume conservation do not resolve these physiological discrepancies.",
        "- Stage 1.1 readiness therefore remains limited even when mathematical and traceability checks pass.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    protocols = [
        *GRADED_PROTOCOLS,
        "head-up-tilt",
        "active-standing",
        "inactive-standing",
        "tilt-recovery",
    ]
    orthostatic = [_orthostatic_record("healthy-reference", protocol) for protocol in protocols]
    orthostatic.extend(
        _orthostatic_record(phenotype, "head-up-tilt")
        for phenotype in TILT_PHENOTYPES
        if phenotype != "healthy-reference"
    )
    payload = {
        "schema_version": "1.0",
        "model_version": "0.3.0",
        "clinical_status": "Research scenario comparisons only; not clinical validation.",
        "analysis_policy": "No gain recalibration, threshold widening, synthetic cohort, or posture-inferred hypocapnia.",
        "orthostatic": orthostatic,
        "empirical_comparisons": _empirical_comparisons(orthostatic),
        "cerebral_experiments": [_cerebral_record(protocol) for protocol in CEREBRAL_PROTOCOLS],
    }
    out_dir = ROOT / "validation" / "stage1-1"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scientific-comparison-matrix.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    (out_dir / "scientific-comparison-matrix.md").write_text(
        _markdown(payload), encoding="utf-8"
    )
    print(f"Wrote Stage 1.1 comparison matrix to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
