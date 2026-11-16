"""Six required small computational demonstrations (not dataset generation)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import compose_phenotypes, load_protocol, repository_root
from .interfaces.observation_mapping import map_simulation_outputs
from .interfaces.ocpe_adapter import load_adapter

# SimulationResult.outputs names mapped to OCPE observation records
# (cardiac_output_l_min is the simulator-native L/min name for cardiac output).
MAPPED_OUTPUT_NAMES = (
    "heart_rate",
    "mean_arterial_pressure",
    "stroke_volume",
    "cardiac_output_l_min",
    "cerebral_flow_index",
    "metabolic_capacity",
    "pem_severity",
)


def _save_result(result, directory: Path, adapter) -> None:
    """Save the simulation trace plus a compact validated observation JSON."""
    result.save(directory)
    final = {name: float(result.outputs[name][-1]) for name in MAPPED_OUTPUT_NAMES}
    records = map_simulation_outputs(final, adapter=adapter, subject=result.phenotype_id)
    payload = {
        "phenotype_id": result.phenotype_id,
        "time_s": float(result.time[-1]),
        "observations": records,
    }
    (directory / "observations.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )


def _simulate(phenotype: str, protocol: str):
    patient = compose_phenotypes([phenotype])
    segments, settings = load_protocol(protocol)
    solver = {k: v for k, v in settings.items() if k in {"sample_interval", "max_step", "rtol", "atol", "seed"}}
    return patient.simulate(segments, **solver), settings


def _plot_orthostatic(results, labels, path: Path, title: str) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(9, 10), sharex=True)
    for result, label in zip(results, labels, strict=True):
        axes[0].plot(result.time, result.outputs["heart_rate"], label=label)
        axes[1].plot(result.time, result.outputs["mean_arterial_pressure"], label=label)
        axes[2].plot(result.time, result.outputs["cerebral_flow_index"], label=label)
    axes[0].set_ylabel("Heart rate (bpm)")
    axes[1].set_ylabel("MAP (mmHg)")
    axes[2].set_ylabel("Cerebral flow index")
    axes[2].set_xlabel("Time (s)")
    axes[0].set_title(title)
    axes[0].legend()
    for axis in axes:
        axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def run_example(name: str, root: Path | None = None) -> dict[str, object]:
    root = root or repository_root()
    output = root / "examples" / name / "output"
    output.mkdir(parents=True, exist_ok=True)
    adapter = load_adapter()
    if name == "healthy_baseline":
        result, settings = _simulate("healthy-reference", "resting-baseline")
        _save_result(result, output, adapter)
        _plot_orthostatic([result], ["Healthy reference"], output / "figure.png", "Stable resting baseline")
        results = [result]
    elif name == "pots_orthostatic_response":
        ids = ["healthy-reference", "pots-neuropathic", "pots-hyperadrenergic", "pots-hypovolemic"]
        results = [_simulate(pid, "head-up-tilt")[0] for pid in ids]
        for pid, result in zip(ids, results, strict=True):
            _save_result(result, output / pid, adapter)
        _plot_orthostatic(results, ids, output / "figure.png", "POTS orthostatic phenotypes")
        settings = {"protocol_id": "head-up-tilt"}
    elif name == "eds_vascular_mechanics":
        ids = ["healthy-reference", "eds-heds-vascular"]
        results = [_simulate(pid, "head-up-tilt")[0] for pid in ids]
        for pid, result in zip(ids, results, strict=True):
            _save_result(result, output / pid, adapter)
        _plot_orthostatic(results, ids, output / "figure.png", "Exploratory hEDS vascular mechanics")
        settings = {"protocol_id": "head-up-tilt"}
    elif name == "mecfs_post_exertional_recovery":
        ids = ["healthy-reference", "mecfs-pem"]
        results = [_simulate(pid, "repeated-exertion-recovery")[0] for pid in ids]
        for pid, result in zip(ids, results, strict=True):
            _save_result(result, output / pid, adapter)
        fig, axes = plt.subplots(3, 1, figsize=(9, 10), sharex=True)
        for result, label in zip(results, ids, strict=True):
            hours = result.time / 3600
            axes[0].plot(hours, result.outputs["functional_capacity"], label=label)
            axes[1].plot(hours, result.outputs["delayed_stress"], label=label)
            axes[2].plot(hours, result.outputs["pem_severity"], label=label)
        axes[0].set_ylabel("Functional capacity")
        axes[1].set_ylabel("Delayed stress")
        axes[2].set_ylabel("PEM severity")
        axes[2].set_xlabel("Time (h)")
        axes[0].legend()
        for axis in axes:
            axis.grid(alpha=0.25)
        fig.suptitle("Delayed PEM and reduced subsequent exertional capacity")
        fig.tight_layout()
        fig.savefig(output / "figure.png", dpi=140)
        plt.close(fig)
        settings = {"protocol_id": "repeated-exertion-recovery"}
    elif name == "long_covid_autonomic_phenotype":
        ids = ["healthy-reference", "long-covid-autonomic"]
        results = [_simulate(pid, "head-up-tilt")[0] for pid in ids]
        for pid, result in zip(ids, results, strict=True):
            _save_result(result, output / pid, adapter)
        _plot_orthostatic(results, ids, output / "figure.png", "Long COVID autonomic subgroup")
        settings = {"protocol_id": "head-up-tilt"}
    elif name == "cross_disease_comparison":
        ids = ["healthy-reference", "pots-neuropathic", "eds-heds-vascular", "mecfs-pem", "long-covid-autonomic"]
        results = [_simulate(pid, "head-up-tilt")[0] for pid in ids]
        for pid, result in zip(ids, results, strict=True):
            _save_result(result, output / pid, adapter)
        _plot_orthostatic(results, ids, output / "figure.png", "Cross-disease orthostatic comparison")
        settings = {"protocol_id": "head-up-tilt"}
    else:
        raise ValueError(f"Unknown example {name!r}")
    return {
        "example": name,
        "protocol": settings["protocol_id"],
        "summaries": {r.phenotype_id: r.summary() for r in results},
    }


EXAMPLES = (
    "healthy_baseline",
    "pots_orthostatic_response",
    "eds_vascular_mechanics",
    "mecfs_post_exertional_recovery",
    "long_covid_autonomic_phenotype",
    "cross_disease_comparison",
)
