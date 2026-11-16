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
    "mean_arterial_pressure_final_mmHg",
    "pem_peak",
    "functional_capacity_final",
)


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
            {
                "gravity_pressure_offset": (-0.10, 0.10),
                "venous_return_resistance": (-0.10, 0.10),
                "resistance_sympathetic_gain": (-0.10, 0.10),
                "blood_volume_factor": (-0.10, 0.10),
                "heart_rate_sympathetic_gain": (-0.10, 0.10),
            },
        ),
        ("eds-heds-vascular", {"peripheral_venous_compliance": (-1 / 7, 1 / 7)}),
    )
    rows: list[dict[str, Any]] = []
    for phenotype_id, parameters in plans:
        protocol_id = "head-up-tilt"
        base_row, base_result = _run(phenotype_id, protocol_id, {}, root)
        base_summary = base_result.summary()
        rows.append({**base_row, "analysis": "local_sensitivity", "parameter": "baseline", "level": "base"})
        for parameter, fractions in parameters.items():
            nominal = getattr(base_result.parameters, parameter)
            perturbed: dict[str, dict[str, Any]] = {}
            for label, fraction in zip(("low", "high"), fractions, strict=True):
                value = nominal * (1.0 + fraction)
                row, _ = _run(phenotype_id, protocol_id, {parameter: value}, root)
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
            for metric in METRICS:
                base_value = base_summary.get(metric)
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
            "peripheral_venous_compliance",
            (120.0, 140.0, 160.0),
            "gravity_pressure_offset",
            (7.0, 9.0, 11.0),
        ),
        (
            "mecfs-pem",
            "single-exertion-recovery",
            "delayed_stress_time_constant",
            (14400.0, 21600.0, 43200.0),
            "pem_onset_time_constant",
            (43200.0, 86400.0, 172800.0),
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


def _grid_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize scenario ranges and explicitly retain failed physiological regimes."""
    summary: dict[str, Any] = {}
    for phenotype_id in sorted({row["phenotype_id"] for row in rows}):
        selected = [row for row in rows if row["phenotype_id"] == phenotype_id]
        metrics: dict[str, Any] = {}
        for metric in METRICS:
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
        *METRICS,
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
        "## Local orthostatic sensitivity",
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
        for metric in METRICS:
            key = (row["phenotype_id"], parameter, metric)
            if key in seen:
                continue
            seen.add(key)
            value = row.get("normalized_sensitivity", {}).get(metric)
            rendered = "n/a" if value is None else f"{value:.4g}"
            lines.append(f"| {row['phenotype_id']} | {parameter} | {metric} | {rendered} |")
    lines.extend(["", "## Deterministic assumption grids", "", "| Phenotype | Overrides | HR rise (bpm) | Final MAP (mmHg) | PEM peak | Final capacity |", "|---|---|---:|---:|---:|---:|"])
    for row in grid:
        overrides = ", ".join(f"{key}={value}" for key, value in row["overrides"].items())
        values = [row.get(metric) for metric in METRICS]
        rendered = ["n/a" if value is None else f"{value:.4g}" for value in values]
        lines.append(f"| {row['phenotype_id']} | {overrides} | {rendered[0]} | {rendered[1]} | {rendered[2]} | {rendered[3]} |")
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
    lines.extend(["## Interpretation limits", "", "- hEDS peripheral venous compliance includes the healthy reference value and both exploratory increases; it is not a measured hEDS coefficient.", "- ME/CFS delay and onset constants are phenomenological and are not probability distributions over patients.", "- Configuration hashes and solver settings are retained in JSON; no random seed is used because no stochastic sampling occurs.", "- Sensitivity does not validate equation structure or clinical utility."])
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
    for name, rows in (("local_sensitivity", local), ("uncertainty_grid", grid)):
        payload: dict[str, Any] = {"schema_version": "1.0", "rows": rows}
        if name == "uncertainty_grid":
            payload["summary"] = _grid_summary(rows)
        (out_dir / f"{name}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        _write_csv(out_dir / f"{name}.csv", rows)
    (out_dir / "sensitivity-report.md").write_text(_markdown(local, grid), encoding="utf-8")
    _plot(local, out_dir / "figure.png")
    return {"local_scenarios": len(local), "grid_scenarios": len(grid), "output_directory": str(out_dir)}
