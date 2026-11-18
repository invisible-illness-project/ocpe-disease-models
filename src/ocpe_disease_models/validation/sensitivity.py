"""Deterministic sensitivity and assumption-uncertainty analysis.

These are small computational scenario grids, not probability distributions,
synthetic patients, wearable data, or population-level uncertainty estimates.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..config import compose_phenotypes, load_protocol, repository_root

SOLVER_KEYS = {"sample_interval", "max_step", "rtol", "atol", "seed"}
METRICS = (
    "orthostatic_heart_rate_rise_bpm",
    "orthostatic_heart_rate_sustained_rise_bpm",
    "mean_arterial_pressure_final_mmHg",
    "pem_peak",
    "functional_capacity_final",
)
CEREBRAL_METRICS = (
    "cerebral_flow_index_final",
    "cerebral_co2_factor_final",
    "end_tidal_co2_final_mmHg",
)
EXPORT_METRICS = (*METRICS, *CEREBRAL_METRICS)


def _run(
    phenotype_id: str,
    protocol_id: str,
    overrides: dict[str, float],
    root: Path,
) -> tuple[dict[str, Any], Any]:
    patient = compose_phenotypes([phenotype_id], root=root)
    patient.parameters = patient.parameters.replaced(overrides)
    patient._validate_parameters()
    segments, settings = load_protocol(protocol_id, root=root)
    solver = {key: value for key, value in settings.items() if key in SOLVER_KEYS}
    result = patient.simulate(segments, **solver)
    summary = result.summary()
    row: dict[str, Any] = {
        "phenotype_id": phenotype_id,
        "protocol_id": protocol_id,
        "overrides": overrides,
        "configuration_sha256": result.metadata["configuration_sha256"],
        "scenario_interpretation": "deterministic computational scenario; not a patient or population sample",
    }
    for metric in METRICS:
        row[metric] = summary.get(metric)
    row.update(
        {
            "cerebral_flow_index_final": float(result.outputs["cerebral_flow_index"][-1]),
            "cerebral_co2_factor_final": float(result.outputs["cerebral_co2_factor"][-1]),
            "end_tidal_co2_final_mmHg": float(result.outputs["end_tidal_co2_mmHg"][-1]),
        }
    )
    row["heart_rate_baseline_bpm"] = summary.get("heart_rate_baseline_bpm")
    row["heart_rate_final_bpm"] = summary["heart_rate_final_bpm"]
    row["parameters"] = asdict(patient.parameters)
    row["solver"] = result.metadata["solver"]
    row["ocpe_commit"] = result.metadata["ocpe_commit"]
    return row, result


def local_sensitivity(root: Path | None = None) -> list[dict[str, Any]]:
    """Run declared one-at-a-time perturbations around two orthostatic scenarios."""
    root = root or repository_root()
    plans = (
        (
            "pots-neuropathic",
            "head-up-tilt",
            {
                "splanchnic_venous_compliance": (-0.10, 0.10),
                "lower_limb_venous_compliance": (-0.10, 0.10),
                "other_systemic_venous_compliance": (-0.10, 0.10),
                "dependent_venous_stiffening_mmHg_per_mL2": (-0.25, 0.25),
                "splanchnic_venous_resistance": (-0.10, 0.10),
                "lower_limb_venous_resistance": (-0.10, 0.10),
                "other_systemic_venous_resistance": (-0.10, 0.10),
                "splanchnic_resistance_sympathetic_gain": (-0.10, 0.10),
                "lower_limb_resistance_sympathetic_gain": (-0.10, 0.10),
                "other_systemic_resistance_sympathetic_gain": (-0.10, 0.10),
                "splanchnic_hydrostatic_height_cm": (-0.10, 0.10),
                "lower_limb_hydrostatic_height_cm": (-0.10, 0.10),
                "other_systemic_hydrostatic_height_cm": (-0.10, 0.10),
                "carotid_baroreceptor_height_cm": (-0.10, 0.10),
                "brain_hydrostatic_height_cm": (-0.10, 0.10),
                "blood_volume_factor": (-0.10, 0.10),
                "cardiac_sympathetic_time_constant": (-0.25, 0.25),
                "vascular_sympathetic_time_constant": (-0.25, 0.25),
                "vagal_time_constant": (-0.25, 0.25),
                "cerebral_autoregulation_residual_slope": (-0.25, 0.25),
                "cerebral_outflow_pressure_mmHg": (-0.25, 0.25),
            },
        ),
        (
            "healthy-reference",
            "head-up-tilt",
            {
                "splanchnic_venous_compliance": (-0.10, 0.10),
                "lower_limb_venous_compliance": (-0.10, 0.10),
                "other_systemic_venous_compliance": (-0.10, 0.10),
                "dependent_venous_stiffening_mmHg_per_mL2": (-0.25, 0.25),
                "splanchnic_resistance_sympathetic_gain": (-0.10, 0.10),
                "lower_limb_resistance_sympathetic_gain": (-0.10, 0.10),
                "other_systemic_resistance_sympathetic_gain": (-0.10, 0.10),
                "splanchnic_hydrostatic_height_cm": (-0.10, 0.10),
                "lower_limb_hydrostatic_height_cm": (-0.10, 0.10),
                "other_systemic_hydrostatic_height_cm": (-0.10, 0.10),
                "aortic_baroreflex_weight": (-0.10, 0.10),
                "carotid_baroreflex_weight": (-0.10, 0.10),
                "heart_rate_cardiac_sympathetic_gain": (-0.25, 0.25),
                "heart_rate_vagal_gain": (-0.25, 0.25),
                "contractility_sympathetic_gain": (-0.25, 0.25),
                "cerebral_autoregulation_residual_slope": (-0.25, 0.25),
            },
        ),
        (
            "eds-heds-vascular",
            "head-up-tilt",
            {"lower_limb_venous_compliance": (-1 / 7, 1 / 7)},
        ),
        (
            "healthy-reference",
            "co2-reduction",
            {
                "cerebral_co2_reactivity_per_mmHg": (-0.25, 0.25),
                "cerebral_co2_extrapolation_limit_mmHg": (-0.50, 0.50),
            },
        ),
        (
            "healthy-reference",
            "light-rhythmic-activity",
            {
                "muscle_pump_stroke_volume": (-0.25, 0.25),
                "muscle_pump_frequency": (-0.25, 0.25),
                "muscle_pump_effectiveness": (-0.25, 0.25),
                "muscle_pump_half_volume": (-0.25, 0.25),
            },
        ),
        (
            "healthy-reference",
            "sustained-contraction",
            {"sustained_contraction_resistance_gain": (-0.25, 0.25)},
        ),
    )
    rows: list[dict[str, Any]] = []
    for phenotype_id, protocol_id, parameters in plans:
        base_row, base_result = _run(phenotype_id, protocol_id, {}, root)
        rows.append({**base_row, "analysis": "local_sensitivity", "parameter": "baseline", "level": "base"})
        for parameter, fractions in parameters.items():
            nominal = getattr(base_result.parameters, parameter)
            perturbed: dict[str, dict[str, Any]] = {}
            for label, fraction in zip(("low", "high"), fractions, strict=True):
                value = nominal * (1.0 + fraction)
                overrides = {parameter: value}
                # The two baroreflex weights are a bounded pair, not
                # independently variable parameters.
                if parameter == "aortic_baroreflex_weight":
                    overrides["carotid_baroreflex_weight"] = 1.0 - value
                elif parameter == "carotid_baroreflex_weight":
                    overrides["aortic_baroreflex_weight"] = 1.0 - value
                row, _ = _run(phenotype_id, protocol_id, overrides, root)
                row.update(
                    {
                        "analysis": "local_sensitivity",
                        "parameter": parameter,
                        "level": label,
                        "nominal_value": nominal,
                        "perturbed_value": value,
                        "relative_perturbation": fraction,
                    }
                )
                rows.append(row)
                perturbed[label] = row
            for metric in EXPORT_METRICS:
                base_value = base_row.get(metric)
                low = perturbed["low"].get(metric)
                high = perturbed["high"].get(metric)
                if base_value is None or low is None or high is None:
                    sensitivity = None
                else:
                    span = fractions[1] - fractions[0]
                    sensitivity = (high - low) / span
                    if abs(base_value) > 1e-12:
                        sensitivity /= abs(base_value)
                for label in ("low", "high"):
                    perturbed[label].setdefault("normalized_sensitivity", {})[metric] = sensitivity
    return rows


def uncertainty_grid(root: Path | None = None) -> list[dict[str, Any]]:
    """Evaluate two explicit small grids of influential modeling assumptions."""
    root = root or repository_root()
    plans = (
        (
            "eds-heds-vascular",
            "head-up-tilt",
            "lower_limb_venous_compliance",
            (60.0, 70.0, 80.0),
            "lower_limb_hydrostatic_height_cm",
            (
                26.6 - 1.0 / 0.7356,
                26.6,
                26.6 + 1.0 / 0.7356,
            ),
        ),
        (
            "mecfs-pem",
            "single-exertion-recovery",
            "delayed_stress_time_constant",
            (43200.0, 72000.0, 86400.0),
            "pem_onset_time_constant",
            (86400.0, 129600.0, 172800.0),
        ),
        (
            "healthy-reference",
            "co2-reduction",
            "cerebral_co2_reactivity_per_mmHg",
            (0.025, 0.035, 0.045),
            "cerebral_outflow_pressure_mmHg",
            (2.5, 5.0, 7.5),
        ),
    )
    rows: list[dict[str, Any]] = []
    for phenotype_id, protocol_id, first, first_values, second, second_values in plans:
        for first_value in first_values:
            for second_value in second_values:
                overrides = {first: first_value, second: second_value}
                row, _ = _run(phenotype_id, protocol_id, overrides, root)
                row.update(
                    {
                        "analysis": "assumption_uncertainty_grid",
                        "grid_parameters": [first, second],
                        "probability": None,
                        "probability_interpretation": "no probability or prevalence is assigned",
                    }
                )
                rows.append(row)
    return rows


def chronotropic_split_grid(root: Path | None = None) -> list[dict[str, Any]]:
    """Vary the unidentified vagal/cardiac-sympathetic gain split at fixed total."""
    root = root or repository_root()
    phenotype_id = "pots-neuropathic"
    patient = compose_phenotypes([phenotype_id], root=root)
    total = (
        patient.parameters.heart_rate_cardiac_sympathetic_gain
        + patient.parameters.heart_rate_vagal_gain
    )
    rows: list[dict[str, Any]] = []
    for fraction in (0.0, 0.5, 1.0):
        overrides = {
            "heart_rate_cardiac_sympathetic_gain": total * fraction,
            "heart_rate_vagal_gain": total * (1.0 - fraction),
        }
        row, _ = _run(phenotype_id, "head-up-tilt", overrides, root)
        row.update(
            {
                "analysis": "chronotropic_split",
                "cardiac_sympathetic_fraction": fraction,
                "total_chronotropic_gain": total,
                "identifiability": "split is not identified by the current evidence",
            }
        )
        rows.append(row)
    return rows


def _grid_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize scenario ranges and explicitly retain failed physiological regimes."""
    summary: dict[str, Any] = {}
    for phenotype_id in sorted({row["phenotype_id"] for row in rows}):
        selected = [row for row in rows if row["phenotype_id"] == phenotype_id]
        metrics: dict[str, Any] = {}
        for metric in EXPORT_METRICS:
            values = [row[metric] for row in selected if row.get(metric) is not None]
            metrics[metric] = {"min": min(values), "max": max(values)} if values else None
        pressure_failures = [
            {"overrides": row["overrides"], "mean_arterial_pressure_final_mmHg": row["mean_arterial_pressure_final_mmHg"]}
            for row in selected
            if row["mean_arterial_pressure_final_mmHg"] < 70.0
        ]
        summary[phenotype_id] = {
            "scenario_ranges": metrics,
            "physiological_regime_failures": pressure_failures,
            "failure_policy": "All scenarios remain reported; MAP below 70 mmHg is an unacceptable physiological regime for the demonstrated phenotype.",
        }
    return summary


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "analysis",
        "phenotype_id",
        "protocol_id",
        "parameter",
        "level",
        "nominal_value",
        "perturbed_value",
        "overrides",
        "configuration_sha256",
        *EXPORT_METRICS,
        "scenario_interpretation",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "overrides": json.dumps(row["overrides"], sort_keys=True)})


def _markdown(local: list[dict[str, Any]], grid: list[dict[str, Any]]) -> str:
    lines = [
        "# Sensitivity and assumption-uncertainty report",
        "",
        "These deterministic perturbations quantify model-response sensitivity. They are not patient samples, probability distributions, prevalence estimates, or clinical validation.",
        "",
        "## Local orthostatic and cerebral-CO2 sensitivity",
        "",
        "Normalized sensitivity is the centered output change divided by the fractional parameter span and, where defined, the absolute baseline output. Zero-valued outputs have no normalized elasticity.",
        "",
        "| Phenotype | Parameter | Output | Low→high normalized sensitivity |",
        "|---|---|---|---:|",
    ]
    seen: set[tuple[str, str, str]] = set()
    for row in local:
        parameter = row.get("parameter")
        if parameter == "baseline":
            continue
        for metric in EXPORT_METRICS:
            key = (row["phenotype_id"], parameter, metric)
            if key in seen:
                continue
            seen.add(key)
            value = row.get("normalized_sensitivity", {}).get(metric)
            rendered = "n/a" if value is None else f"{value:.4g}"
            lines.append(f"| {row['phenotype_id']} | {parameter} | {metric} | {rendered} |")
    lines.extend(["", "## Deterministic assumption grids", "", "| Phenotype | Overrides | Peak HR rise (bpm) | Sustained HR rise (bpm) | Final MAP (mmHg) | PEM peak | Final capacity |", "|---|---|---:|---:|---:|---:|---:|"])
    for row in grid:
        overrides = ", ".join(f"{key}={value}" for key, value in row["overrides"].items())
        values = [row.get(metric) for metric in METRICS]
        rendered = ["n/a" if value is None else f"{value:.4g}" for value in values]
        lines.append(f"| {row['phenotype_id']} | {overrides} | {rendered[0]} | {rendered[1]} | {rendered[2]} | {rendered[3]} | {rendered[4]} |")
    summary = _grid_summary(grid)
    lines.extend(["", "## Range summary and failed physiological regimes", ""])
    for phenotype_id, record in summary.items():
        lines.append(f"### {phenotype_id}")
        lines.append("")
        for metric, bounds in record["scenario_ranges"].items():
            if bounds is not None:
                lines.append(f"- {metric}: {bounds['min']:.4g} to {bounds['max']:.4g}")
        failures = record["physiological_regime_failures"]
        if failures:
            lines.append(f"- **Unacceptable MAP regimes retained:** {len(failures)} scenario(s) end below 70 mmHg. These combinations fail the physiological demonstration criterion and must not be presented as valid phenotypes.")
        else:
            lines.append("- No scenario in this grid ends below the 70 mmHg MAP screening threshold.")
        lines.append("")
    lines.extend(["## Interpretation limits", "", "- hEDS lower-limb venous compliance includes the healthy reference value and exploratory changes; it is not a measured hEDS coefficient.", "- ME/CFS delay and onset constants are phenomenological and are not probability distributions over patients.", "- CO2 reactivity, clipping, and cerebral-outflow scenarios vary explicit computational assumptions; they do not identify patient-specific reactivity or convert ETCO2 into PaCO2.", "- Configuration hashes and solver settings are retained in JSON; no random seed is used because no stochastic sampling occurs.", "- Sensitivity does not validate equation structure or clinical utility."])
    return "\n".join(lines) + "\n"


def _plot(local: list[dict[str, Any]], path: Path) -> None:
    records = []
    for row in local:
        if row.get("parameter") == "baseline":
            continue
        value = row.get("normalized_sensitivity", {}).get("orthostatic_heart_rate_rise_bpm")
        if value is not None:
            records.append((f"{row['phenotype_id']}:{row['parameter']}", value))
    unique = list(dict.fromkeys(records))
    fig, ax = plt.subplots(figsize=(10, max(3, 0.5 * len(unique))))
    labels = [item[0] for item in unique]
    values = [item[1] for item in unique]
    ax.barh(labels, values)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Normalized sensitivity of orthostatic HR rise")
    ax.set_title("Deterministic one-at-a-time sensitivity")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def run_analysis(root: Path | None = None, out_dir: Path | None = None) -> dict[str, Any]:
    root = root or repository_root()
    out_dir = out_dir or root / "validation" / "sensitivity"
    out_dir.mkdir(parents=True, exist_ok=True)
    local = local_sensitivity(root)
    grid = uncertainty_grid(root)
    split = chronotropic_split_grid(root)
    for name, rows in (
        ("local_sensitivity", local),
        ("uncertainty_grid", grid),
        ("chronotropic_split", split),
    ):
        payload: dict[str, Any] = {"schema_version": "1.0", "rows": rows}
        if name == "uncertainty_grid":
            payload["summary"] = _grid_summary(rows)
        (out_dir / f"{name}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        _write_csv(out_dir / f"{name}.csv", rows)
    report = _markdown(local, grid)
    report += "\n## Unidentified chronotropic split\n\n"
    report += "Total chronotropic gain is fixed; only the cardiac-sympathetic fraction changes. These scenarios demonstrate structural non-identifiability rather than alternative patients.\n\n"
    report += "| Cardiac-sympathetic fraction | Peak HR rise (bpm) | Sustained HR rise (bpm) | Final MAP (mmHg) |\n|---:|---:|---:|---:|\n"
    for row in split:
        report += (
            f"| {row['cardiac_sympathetic_fraction']:.1f} "
            f"| {row['orthostatic_heart_rate_rise_bpm']:.4g} "
            f"| {row['orthostatic_heart_rate_sustained_rise_bpm']:.4g} "
            f"| {row['mean_arterial_pressure_final_mmHg']:.4g} |\n"
        )
    (out_dir / "sensitivity-report.md").write_text(report, encoding="utf-8")
    _plot(local, out_dir / "figure.png")
    return {
        "local_scenarios": len(local),
        "grid_scenarios": len(grid),
        "chronotropic_split_scenarios": len(split),
        "output_directory": str(out_dir),
    }
