#!/usr/bin/env python3
"""Generate the Stage 1.3 deterministic scientific comparison artifacts.

The isolated mechanism experiments start from the reproduced Stage 1.2 healthy
configuration. They are model-specific scenario analyses, not patient cohorts,
independent experimental replication, or clinical validation.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from run_stage1_1_validation import (  # noqa: E402
    CEREBRAL_PROTOCOLS,
    GRADED_PROTOCOLS,
    TILT_PHENOTYPES,
    _cerebral_record,
    _mean,
    _orthostatic_record,
    _point,
)

from ocpe_disease_models.config import load_protocol  # noqa: E402
from ocpe_disease_models.models.shared.model import (  # noqa: E402
    ComputationalPatient,
    ModelParameters,
)

SOLVER_KEYS = {"sample_interval", "max_step", "rtol", "atol", "seed"}
STAGE1_2 = {
    "splanchnic_venous_compliance": 70.0,
    "lower_limb_venous_compliance": 50.0,
    "other_systemic_venous_compliance": 50.0,
    "splanchnic_hydrostatic_height_cm": 7.0,
    "lower_limb_hydrostatic_height_cm": 14.0,
    "other_systemic_hydrostatic_height_cm": 11.0,
    "splanchnic_resistance_sympathetic_gain": 0.8,
    "lower_limb_resistance_sympathetic_gain": 0.8,
    "other_systemic_resistance_sympathetic_gain": 0.8,
    "contractility_sympathetic_gain": 0.25,
    "heart_rate_cardiac_sympathetic_gain": 20.0,
    "heart_rate_vagal_gain": 20.0,
    "aortic_baroreflex_weight": 0.25,
    "carotid_baroreflex_weight": 0.75,
    "cerebral_autoregulation_residual_slope": 0.4,
    "dependent_venous_stiffening_mmHg_per_mL2": 0.0,
}
GROUPS = {
    "compliance_redistribution": {
        "splanchnic_venous_compliance": 90.0,
        "lower_limb_venous_compliance": 60.0,
        "other_systemic_venous_compliance": 20.0,
    },
    "common_anatomical_geometry": {
        "splanchnic_hydrostatic_height_cm": 13.3,
        "lower_limb_hydrostatic_height_cm": 26.6,
        "other_systemic_hydrostatic_height_cm": 4.5,
    },
    "baroreflex_weighting": {
        "aortic_baroreflex_weight": 0.35,
        "carotid_baroreflex_weight": 0.65,
    },
    "vascular_compensation_gains": {
        "splanchnic_resistance_sympathetic_gain": 0.45,
        "lower_limb_resistance_sympathetic_gain": 0.45,
        "other_systemic_resistance_sympathetic_gain": 0.45,
    },
    "cardiac_compensation": {
        "contractility_sympathetic_gain": 0.1,
        "heart_rate_cardiac_sympathetic_gain": 13.6,
        "heart_rate_vagal_gain": 13.6,
    },
    "dependent_venous_elastance": {
        "dependent_venous_stiffening_mmHg_per_mL2": 0.0001,
    },
    "cerebral_autoregulation": {
        "cerebral_autoregulation_residual_slope": 0.25,
    },
}
LINEAR_PROPOSAL = {
    key: value
    for group_name, group in GROUPS.items()
    if group_name != "dependent_venous_elastance"
    for key, value in group.items()
}
STAGE1_3 = {**LINEAR_PROPOSAL, **GROUPS["dependent_venous_elastance"]}


def _simulate_parameters(parameters: dict[str, float], protocol_id: str):
    patient = ComputationalPatient(
        ModelParameters().replaced(parameters), phenotype_id="stage1-3-mechanism-scenario"
    )
    patient._validate_parameters()
    segments, settings = load_protocol(protocol_id, root=ROOT)
    solver = {key: value for key, value in settings.items() if key in SOLVER_KEYS}
    return patient.simulate(segments, **solver)


def _reduction(baseline: float, value: float) -> float:
    return 100.0 * (baseline - value) / baseline


def _experiment_record(name: str, changes: dict[str, float]) -> dict[str, Any]:
    parameters = {**STAGE1_2, **changes}
    result70 = _simulate_parameters(parameters, "passive-tilt-70")
    result60 = _simulate_parameters(parameters, "passive-tilt-60")
    start = next(s.start for s in result70.protocol if s.resolved_tilt_angle_deg() > 0)
    end = max(s.end for s in result70.protocol if s.resolved_tilt_angle_deg() > 0)
    baseline: dict[str, float] = {}
    late: dict[str, float] = {}
    for output in (
        "heart_rate",
        "mean_arterial_pressure",
        "cardiac_output",
        "stroke_volume",
        "cerebral_flow_index",
        "splanchnic_venous_volume",
        "lower_limb_venous_volume",
        "other_systemic_venous_volume",
        "central_venous_volume",
    ):
        baseline[output] = _mean(result70, output, 0.0, start - 2.0)
        late[output] = _mean(result70, output, end - 120.0, end)
    angle_comparisons = {}
    for angle, result in ((60, result60), (70, result70)):
        co0 = _mean(result, "cardiac_output", 0.0, start - 2.0)
        sv0 = _mean(result, "stroke_volume", 0.0, start - 2.0)
        co = _point(result, start + 120.0, "cardiac_output")
        sv = _point(result, start + 120.0, "stroke_volume")
        angle_comparisons[str(angle)] = {
            "cardiac_output_reduction_pct_at_120_s": _reduction(co0, co),
            "stroke_volume_reduction_pct_at_120_s": _reduction(sv0, sv),
        }
    return {
        "experiment": name,
        "changed_parameters": changes,
        "full_parameters": parameters,
        "configuration_sha256": result70.metadata["configuration_sha256"],
        "solver": result70.metadata["solver"],
        "sustained_heart_rate_rise_bpm": late["heart_rate"] - baseline["heart_rate"],
        "end_mean_arterial_pressure_mmHg": _mean(
            result70, "mean_arterial_pressure", end - 10.0, end
        ),
        "caudal_pooling_mL": (
            late["splanchnic_venous_volume"]
            - baseline["splanchnic_venous_volume"]
            + late["lower_limb_venous_volume"]
            - baseline["lower_limb_venous_volume"]
        ),
        "residual_systemic_volume_change_mL": (
            late["other_systemic_venous_volume"] - baseline["other_systemic_venous_volume"]
        ),
        "central_venous_volume_change_mL": late["central_venous_volume"] - baseline["central_venous_volume"],
        "end_cerebral_flow_reduction_pct": _reduction(
            baseline["cerebral_flow_index"],
            _mean(result70, "cerebral_flow_index", end - 10.0, end),
        ),
        "angle_comparisons": angle_comparisons,
        "interpretation": "Deterministic isolated/combined mechanism scenario; not independent experimental replication or patient estimation.",
    }


def _empirical_comparisons(orthostatic: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for record in orthostatic:
        angle = record["protocol_id"].removeprefix("passive-tilt-")
        if record["phenotype_id"] != "healthy-reference" or angle not in {"60", "70"}:
            continue
        for point in record["points"]:
            if point["offset_s"] not in {120.0, 300.0}:
                continue
            for metric, band in (
                ("cardiac_output_change_pct", (-20.0, -17.0)),
                ("stroke_volume_change_pct", (-34.0, -28.0)),
            ):
                value = point[metric]
                direct = angle == "60"
                rows.append(
                    {
                        "reference_id": "REF-ZAIDI-2000",
                        "protocol_id": record["protocol_id"],
                        "offset_s": point["offset_s"],
                        "metric": metric,
                        "model_value_pct": value,
                        "published_group_range_pct": list(band),
                        "status": "WITHIN" if band[0] <= value <= band[1] else "MISS",
                        "comparison_class": (
                            "direct_experimental_angle_replication"
                            if direct
                            else "extrapolated_model_specific_acceptance_criterion"
                        ),
                        "interpretation": (
                            "Direct 60-degree group-level plausibility comparison; not patient fitting or external validation."
                            if direct
                            else "The 60-degree-informed published range is reused at 70 degrees as an explicit model-specific extrapolation, not direct replication of a 70-degree experiment."
                        ),
                    }
                )
    return rows


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 1.3 scientific comparison matrix",
        "",
        "Deterministic research scenarios only. Numerical threshold passage is not scientific or clinical readiness. The 60° rows are direct experimental-angle comparisons; the 70° rows are explicitly extrapolated model-specific acceptance criteria.",
        "",
        "## Isolated and combined healthy mechanism experiments",
        "",
        "Every experiment starts from the reproduced Stage 1.2 healthy configuration. CO and SV values are reductions at 120 s upright.",
        "",
        "| Experiment | Sustained HR rise (bpm) | End MAP (mmHg) | Caudal pooling (mL) | Residual ΔV (mL) | 60° CO (%) | 60° SV (%) | 70° CO (%) | 70° SV (%) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["mechanism_experiments"]:
        angles = row["angle_comparisons"]
        lines.append(
            f"| {row['experiment']} | {row['sustained_heart_rate_rise_bpm']:.3f} "
            f"| {row['end_mean_arterial_pressure_mmHg']:.3f} | {row['caudal_pooling_mL']:.3f} "
            f"| {row['residual_systemic_volume_change_mL']:.3f} "
            f"| {angles['60']['cardiac_output_reduction_pct_at_120_s']:.3f} "
            f"| {angles['60']['stroke_volume_reduction_pct_at_120_s']:.3f} "
            f"| {angles['70']['cardiac_output_reduction_pct_at_120_s']:.3f} "
            f"| {angles['70']['stroke_volume_reduction_pct_at_120_s']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Preserved phenotype criteria",
            "",
            "| Phenotype | Protocol | Sustained HR rise (bpm) | Criterion | Upright-end MAP (mmHg) | End-tilt CFI reduction (%) |",
            "|---|---|---:|---|---:|---:|",
        ]
    )
    for row in payload["orthostatic"]:
        criterion = row.get("sustained_30_bpm_criterion", {}).get("status", "n/a")
        lines.append(
            f"| {row['phenotype_id']} | {row['protocol_id']} | {row['sustained_heart_rate_rise_bpm']:.3f} "
            f"| {criterion} | {row['upright_end_mean_arterial_pressure_mmHg']:.3f} | {row['end_cerebral_flow_reduction_pct']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Protocol-specific empirical comparisons",
            "",
            "| Reference | Protocol | Offset (s) | Metric | Model (%) | Published/reused range (%) | Status | Comparison class |",
            "|---|---|---:|---|---:|---|---|---|",
        ]
    )
    for row in payload["empirical_comparisons"]:
        lines.append(
            f"| {row['reference_id']} | {row['protocol_id']} | {row['offset_s']:.0f} | {row['metric']} "
            f"| {row['model_value_pct']:.3f} | {row['published_group_range_pct'][0]} to {row['published_group_range_pct'][1]} "
            f"| {row['status']} | {row['comparison_class']} |"
        )
    misses = sum(row["status"] == "MISS" for row in payload["empirical_comparisons"])
    failures = sum(
        row.get("sustained_30_bpm_criterion", {}).get("status") == "FAIL"
        for row in payload["orthostatic"]
    )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Preserved CO/SV comparisons outside their bands: **{misses}**.",
            f"- POTS/Long-COVID-autonomic sustained-HR criterion failures: **{failures}**.",
            "- The linear audit proposal and the nonlinear Stage 1.3 combination are separate rows; their numerical differences are retained rather than explaining them away.",
            "- Passing these calibrated scenario checks does not identify patient parameters, validate the quadratic equation form, or establish general-purpose synthetic-data readiness.",
            "",
        ]
    )
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
    experiments = [_experiment_record("stage1_2_reproduced_baseline", {})]
    experiments.extend(_experiment_record(f"{name}_only", changes) for name, changes in GROUPS.items())
    experiments.append(_experiment_record("audit_linear_proposal_combined", LINEAR_PROPOSAL))
    experiments.append(_experiment_record("stage1_3_nonlinear_combined", STAGE1_3))
    for key, value in STAGE1_3.items():
        assert getattr(ModelParameters(), key) == value, (key, value)
    payload = {
        "schema_version": "1.0",
        "stage": "1.3",
        "execution_date": date.today().isoformat(),
        "base_commit": "e48110e",
        "model_version": "0.4.0",
        "clinical_status": "Deterministic research scenarios only; no clinical validity, diagnostic accuracy, treatment efficacy, patient-specific calibration, or general-purpose synthetic-data readiness is established.",
        "baseline_method": "Stage 1.2 numerical results were independently reproduced at base commit e48110e before modification. Stage 1.3 rows are fresh executions. The audit's unavailable Git objects are disclosed in docs/stage1-3/baseline-reproduction.md.",
        "analysis_policy": "Mechanisms were evaluated independently before combination; preserved criteria were not widened; no synthetic cohort, patient fitting, or posture-inferred hypocapnia was introduced.",
        "stage1_2_parameters": STAGE1_2,
        "stage1_3_parameters": STAGE1_3,
        "mechanism_experiments": experiments,
        "orthostatic": orthostatic,
        "empirical_comparisons": _empirical_comparisons(orthostatic),
        "cerebral_experiments": [_cerebral_record(protocol) for protocol in CEREBRAL_PROTOCOLS],
    }
    out_dir = ROOT / "validation" / "stage1-3"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scientific-comparison-matrix.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "scientific-comparison-matrix.md").write_text(
        _markdown(payload), encoding="utf-8"
    )
    print(f"Wrote Stage 1.3 comparison matrix to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
