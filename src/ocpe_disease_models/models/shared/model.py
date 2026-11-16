"""Executable, beat-averaged physiological models.

The cardiovascular equations conserve stressed blood volume across arterial,
central-venous, splanchnic-venous and lower-limb-venous compartments. Distinct
vagal, cardiac-sympathetic and vascular-sympathetic states control effectors.
Rhythmic muscle activity transfers lower-limb venous volume without creating
blood. The PEM equations are an explicitly phenomenological exertion/delay/
recovery approximation, not a claim that the cellular cause of PEM is known.
Time is seconds, volumes are mL, pressures are mmHg, and flows are mL/s unless
stated otherwise.
"""

from __future__ import annotations

import hashlib
import json
import platform
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from ... import OCPE_COMMIT

STATE_NAMES = (
    "arterial_volume",
    "central_venous_volume",
    "splanchnic_venous_volume",
    "lower_limb_venous_volume",
    "cardiac_sympathetic_state",
    "vascular_sympathetic_state",
    "vagal_state",
    "exertional_load",
    "delayed_stress",
    "pem_severity",
    "cerebral_flow_index",
)


@dataclass(frozen=True)
class ModelParameters:
    """Parameters for the shared model; defaults define the healthy reference.

    Values not identified as direct clinical measurements in the parameter
    registry are computational operating-point or calibration assumptions.
    """

    # Regional vascular compliances (mL/mmHg) and resistances (mmHg s/mL).
    arterial_compliance: float = 1.5
    central_venous_compliance: float = 140.0
    splanchnic_venous_compliance: float = 70.0
    lower_limb_venous_compliance: float = 50.0
    splanchnic_arterial_resistance: float = 2.204081632653061
    lower_limb_arterial_resistance: float = 2.204081632653061
    splanchnic_venous_resistance: float = 0.12244897959183673
    lower_limb_venous_resistance: float = 0.12244897959183673
    splanchnic_resistance_sympathetic_gain: float = 0.8
    lower_limb_resistance_sympathetic_gain: float = 0.8
    splanchnic_gravity_pressure_offset: float = 4.0
    lower_limb_gravity_pressure_offset: float = 8.0

    # Initial stressed volumes/pressures; all four volumes conserve their sum.
    arterial_volume_initial: float = 150.0
    central_venous_volume_initial: float = 700.0
    splanchnic_venous_pressure_initial: float = 10.0
    lower_limb_venous_pressure_initial: float = 10.0
    blood_volume_factor: float = 1.0

    # Cardiac and differentiated baroreflex operating point.
    stroke_volume_max: float = 100.0
    stroke_volume_half_volume: float = 300.0
    contractility_sympathetic_gain: float = 0.25
    heart_rate_rest: float = 70.0
    heart_rate_cardiac_sympathetic_gain: float = 20.0
    heart_rate_vagal_gain: float = 20.0
    baroreflex_pressure_setpoint: float = 100.0
    baroreflex_pressure_scale: float = 2.0
    cardiac_sympathetic_time_constant: float = 6.0
    vascular_sympathetic_time_constant: float = 10.0
    vagal_time_constant: float = 1.0
    exercise_heart_rate_gain: float = 70.0
    exercise_resistance_reduction: float = 0.30

    # Skeletal muscle pump and sustained-contraction impediment.
    muscle_pump_stroke_volume: float = 20.0
    muscle_pump_frequency: float = 1.0
    muscle_pump_effectiveness: float = 1.0
    muscle_pump_half_volume: float = 500.0
    sustained_contraction_resistance_gain: float = 3.0

    # Cerebral perfusion-pressure approximation (dimensionless flow index).
    head_hydrostatic_pressure_offset: float = 20.0
    cerebral_reference_perfusion_pressure: float = 95.0
    cerebral_autoregulation_residual_slope: float = 0.2
    cerebral_orthostatic_impairment: float = 0.0
    cerebral_decline_time_constant: float = 5.0
    cerebral_recovery_time_constant: float = 12.0

    # Oxygen use and exertional capacity (dimensionless fractions).
    baseline_metabolic_capacity: float = 1.0
    oxygen_extraction_fraction: float = 0.78
    functional_capacity_reference_extraction: float = 0.78
    pem_capacity_penalty: float = 0.5
    pem_extraction_penalty: float = 0.10

    # Phenomenological PEM dynamics (seconds and dimensionless states).
    exertional_load_time_constant: float = 1800.0
    delayed_stress_time_constant: float = 21600.0
    pem_onset_time_constant: float = 86400.0
    pem_recovery_time_constant: float = 172800.0
    pem_trigger_threshold: float = 0.999
    pem_response_gain: float = 0.0

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any] | None = None) -> ModelParameters:
        allowed = {f.name for f in fields(cls)}
        unknown = set(values or {}) - allowed
        if unknown:
            raise ValueError(f"Unknown model parameters: {sorted(unknown)}")
        return cls(**dict(values or {}))

    def replaced(self, overrides: Mapping[str, Any]) -> ModelParameters:
        values = asdict(self)
        values.update(overrides)
        return self.from_mapping(values)


@dataclass(frozen=True)
class ProtocolSegment:
    """A constant-input segment of a simulation protocol."""

    start: float
    end: float
    upright: float = 0.0
    exertion: float = 0.0
    rhythmic_muscle_activity: float = 0.0
    sustained_muscle_contraction: float = 0.0
    label: str = "segment"

    def validate(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError(f"Invalid segment bounds: {self}")
        inputs = (
            self.upright,
            self.exertion,
            self.rhythmic_muscle_activity,
            self.sustained_muscle_contraction,
        )
        if any(not 0 <= value <= 1 for value in inputs):
            raise ValueError("Protocol inputs must be normalized to [0, 1]")


@dataclass
class SimulationResult:
    """A small validation trace with reproducibility metadata, not a dataset."""

    time: np.ndarray
    states: np.ndarray
    outputs: dict[str, np.ndarray]
    parameters: ModelParameters
    phenotype_id: str
    protocol: Sequence[ProtocolSegment]
    metadata: dict[str, Any]

    def metric(self, name: str, start: float, end: float, statistic: str = "mean") -> float:
        if name not in self.outputs:
            raise KeyError(f"Unknown output {name!r}")
        mask = (self.time >= start) & (self.time <= end)
        if not np.any(mask):
            raise ValueError(f"No samples in window [{start}, {end}]")
        values = self.outputs[name][mask]
        return float(getattr(np, statistic)(values))

    def summary(self) -> dict[str, Any]:
        upright_segments = [s for s in self.protocol if s.upright > 0]
        result: dict[str, Any] = {
            "phenotype_id": self.phenotype_id,
            "duration_s": float(self.time[-1]),
            "samples": len(self.time),
            "heart_rate_final_bpm": float(self.outputs["heart_rate"][-1]),
            "mean_arterial_pressure_final_mmHg": float(self.outputs["mean_arterial_pressure"][-1]),
            "pem_peak": float(np.max(self.outputs["pem_severity"])),
            "functional_capacity_final": float(self.outputs["functional_capacity"][-1]),
        }
        if upright_segments:
            start = upright_segments[0].start
            upright_end = min(float(self.time[-1]), upright_segments[0].end)
            baseline_end = max(0.0, start - 1.0)
            baseline = self.metric("heart_rate", 0.0, baseline_end)
            standing = self.metric(
                "heart_rate", start, min(start + 300.0, upright_end), "max"
            )
            sustained_start = max(start, upright_end - 120.0)
            sustained = self.metric("heart_rate", sustained_start, upright_end)
            result.update(
                {
                    "heart_rate_baseline_bpm": baseline,
                    "heart_rate_upright_peak_bpm": standing,
                    "orthostatic_heart_rate_rise_bpm": standing - baseline,
                    "orthostatic_heart_rate_sustained_rise_bpm": sustained - baseline,
                }
            )
        return result

    def save(self, directory: str | Path) -> None:
        """Save a compact NPZ trace and JSON metadata for reproducible validation."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        arrays = {"time": self.time, "states": self.states, **self.outputs}
        np.savez_compressed(directory / "trace.npz", **arrays)
        payload = {
            "metadata": self.metadata,
            "parameters": asdict(self.parameters),
            "state_names": STATE_NAMES,
            "protocol": [asdict(s) for s in self.protocol],
            "summary": self.summary(),
        }
        (directory / "result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


class ComputationalPatient:
    """Composable disease phenotype executed with the shared physiological equations."""

    def __init__(
        self,
        parameters: ModelParameters | None = None,
        phenotype_id: str = "healthy-reference",
        provenance: Mapping[str, Any] | None = None,
    ) -> None:
        self.parameters = parameters or ModelParameters()
        self.phenotype_id = phenotype_id
        self.provenance = dict(provenance or {})
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        p = self.parameters
        positive_names = (
            "arterial_compliance",
            "central_venous_compliance",
            "splanchnic_venous_compliance",
            "lower_limb_venous_compliance",
            "splanchnic_arterial_resistance",
            "lower_limb_arterial_resistance",
            "splanchnic_venous_resistance",
            "lower_limb_venous_resistance",
            "arterial_volume_initial",
            "central_venous_volume_initial",
            "splanchnic_venous_pressure_initial",
            "lower_limb_venous_pressure_initial",
            "blood_volume_factor",
            "stroke_volume_max",
            "stroke_volume_half_volume",
            "heart_rate_rest",
            "baroreflex_pressure_setpoint",
            "baroreflex_pressure_scale",
            "cardiac_sympathetic_time_constant",
            "vascular_sympathetic_time_constant",
            "vagal_time_constant",
            "muscle_pump_frequency",
            "muscle_pump_half_volume",
            "cerebral_reference_perfusion_pressure",
            "cerebral_decline_time_constant",
            "cerebral_recovery_time_constant",
            "baseline_metabolic_capacity",
            "exertional_load_time_constant",
            "delayed_stress_time_constant",
            "pem_onset_time_constant",
            "pem_recovery_time_constant",
        )
        for name in positive_names:
            if getattr(p, name) <= 0:
                raise ValueError(f"{name} must be positive")
        nonnegative_names = (
            "splanchnic_resistance_sympathetic_gain",
            "lower_limb_resistance_sympathetic_gain",
            "splanchnic_gravity_pressure_offset",
            "lower_limb_gravity_pressure_offset",
            "contractility_sympathetic_gain",
            "heart_rate_cardiac_sympathetic_gain",
            "heart_rate_vagal_gain",
            "exercise_heart_rate_gain",
            "muscle_pump_stroke_volume",
            "muscle_pump_effectiveness",
            "sustained_contraction_resistance_gain",
            "head_hydrostatic_pressure_offset",
            "pem_response_gain",
        )
        for name in nonnegative_names:
            if getattr(p, name) < 0:
                raise ValueError(f"{name} must be nonnegative")
        for name in (
            "splanchnic_resistance_sympathetic_gain",
            "lower_limb_resistance_sympathetic_gain",
        ):
            if getattr(p, name) >= 2:
                raise ValueError(f"{name} must be below 2 to keep resistance positive")
        for name in (
            "oxygen_extraction_fraction",
            "functional_capacity_reference_extraction",
        ):
            if not 0 < getattr(p, name) < 1:
                raise ValueError(f"{name} must be in (0, 1)")
        for name in (
            "exercise_resistance_reduction",
            "cerebral_orthostatic_impairment",
            "pem_capacity_penalty",
            "pem_extraction_penalty",
        ):
            if not 0 <= getattr(p, name) <= 1:
                raise ValueError(f"{name} must be in [0, 1]")
        if not 0 < p.cerebral_autoregulation_residual_slope <= 1:
            raise ValueError("cerebral_autoregulation_residual_slope must be in (0, 1]")
        if not 0 <= p.pem_trigger_threshold < 1:
            raise ValueError("pem_trigger_threshold must be in [0, 1)")

    def initial_state(self) -> np.ndarray:
        p = self.parameters
        factor = p.blood_volume_factor
        arterial = p.arterial_volume_initial * factor
        central = p.central_venous_volume_initial * factor
        splanchnic = p.splanchnic_venous_pressure_initial * p.splanchnic_venous_compliance * factor
        lower_limb = p.lower_limb_venous_pressure_initial * p.lower_limb_venous_compliance * factor
        arterial_pressure = arterial / p.arterial_compliance
        central_pressure = central / p.central_venous_compliance
        cerebral_ratio = max(0.0, arterial_pressure - central_pressure) / (
            p.cerebral_reference_perfusion_pressure
        )
        slope = p.cerebral_autoregulation_residual_slope
        cerebral_initial = cerebral_ratio / (slope + (1.0 - slope) * cerebral_ratio)
        return np.array(
            [
                arterial,
                central,
                splanchnic,
                lower_limb,
                0.5,
                0.5,
                0.5,
                0.0,
                0.0,
                0.0,
                cerebral_initial,
            ],
            dtype=float,
        )

    @staticmethod
    def _inputs(t: float, protocol: Sequence[ProtocolSegment]) -> tuple[float, float, float, float]:
        for segment in protocol:
            if segment.start <= t < segment.end:
                return (
                    segment.upright,
                    segment.exertion,
                    segment.rhythmic_muscle_activity,
                    segment.sustained_muscle_contraction,
                )
        if t == protocol[-1].end:
            last = protocol[-1]
            return (
                last.upright,
                last.exertion,
                last.rhythmic_muscle_activity,
                last.sustained_muscle_contraction,
            )
        raise ValueError(f"Time {t} is outside the protocol")

    def _derived(
        self, t: float, y: np.ndarray, protocol: Sequence[ProtocolSegment]
    ) -> dict[str, float]:
        p = self.parameters
        if not np.all(np.isfinite(y)):
            raise FloatingPointError("Non-finite state passed to physiological equations")
        va, vc, vs, vl, cardiac_sym, vascular_sym, vagal, _, _, pem, _ = y
        upright, exertion, rhythmic, sustained = self._inputs(t, protocol)
        pa = va / p.arterial_compliance
        pc = vc / p.central_venous_compliance
        ps = vs / p.splanchnic_venous_compliance
        pl = vl / p.lower_limb_venous_compliance
        pem = min(1.0, pem)
        capacity = max(0.05, p.baseline_metabolic_capacity * (1.0 - p.pem_capacity_penalty * pem))
        splanchnic_arterial_resistance = p.splanchnic_arterial_resistance * (
            1.0 + p.splanchnic_resistance_sympathetic_gain * (vascular_sym - 0.5)
        )
        lower_limb_arterial_resistance = (
            p.lower_limb_arterial_resistance
            * (1.0 + p.lower_limb_resistance_sympathetic_gain * (vascular_sym - 0.5))
            * (1.0 - p.exercise_resistance_reduction * exertion)
        )
        lower_limb_venous_resistance = p.lower_limb_venous_resistance * (
            1.0 + p.sustained_contraction_resistance_gain * sustained
        )
        contractility = max(0.2, 1.0 + p.contractility_sympathetic_gain * (cardiac_sym - 0.5))
        stroke_volume = (
            p.stroke_volume_max * contractility * vc / (vc + p.stroke_volume_half_volume)
        )
        heart_rate = np.clip(
            p.heart_rate_rest
            + p.heart_rate_cardiac_sympathetic_gain * (cardiac_sym - 0.5)
            + p.heart_rate_vagal_gain * (0.5 - vagal)
            + p.exercise_heart_rate_gain * exertion * capacity,
            30.0,
            220.0,
        )
        cardiac_output = heart_rate / 60.0 * stroke_volume
        splanchnic_arterial_flow = max(0.0, (pa - ps) / splanchnic_arterial_resistance)
        lower_limb_arterial_flow = max(0.0, (pa - pl) / lower_limb_arterial_resistance)
        splanchnic_venous_return = max(
            0.0,
            (ps - pc - p.splanchnic_gravity_pressure_offset * upright)
            / p.splanchnic_venous_resistance,
        )
        muscle_pump_flow = (
            p.muscle_pump_frequency
            * p.muscle_pump_stroke_volume
            * p.muscle_pump_effectiveness
            * rhythmic
            * vl
            / (vl + p.muscle_pump_half_volume)
        )
        lower_limb_venous_return = (
            max(
                0.0,
                (pl - pc - p.lower_limb_gravity_pressure_offset * upright)
                / lower_limb_venous_resistance,
            )
            + muscle_pump_flow
        )
        head_pressure = max(0.0, pa - p.head_hydrostatic_pressure_offset * upright)
        cerebral_perfusion_pressure = max(0.0, head_pressure - pc)
        cerebral_ratio = cerebral_perfusion_pressure / p.cerebral_reference_perfusion_pressure
        slope = p.cerebral_autoregulation_residual_slope
        cerebral_pressure_target = cerebral_ratio / (slope + (1.0 - slope) * cerebral_ratio)
        cerebral_target = cerebral_pressure_target * max(
            0.0, 1.0 - p.cerebral_orthostatic_impairment * upright
        )
        extraction = np.clip(
            p.oxygen_extraction_fraction * (1.0 - p.pem_extraction_penalty * pem), 0.0, 0.99
        )
        systemic_flow = splanchnic_arterial_flow + lower_limb_arterial_flow
        parallel_resistance = 1.0 / (
            1.0 / splanchnic_arterial_resistance + 1.0 / lower_limb_arterial_resistance
        )
        return {
            "arterial_pressure": pa,
            "central_venous_pressure": pc,
            "splanchnic_venous_pressure": ps,
            "lower_limb_venous_pressure": pl,
            "baroreflex_pressure": head_pressure,
            "cerebral_perfusion_pressure": cerebral_perfusion_pressure,
            "heart_rate": float(heart_rate),
            "stroke_volume": stroke_volume,
            "cardiac_output": cardiac_output,
            "cardiac_output_l_min": cardiac_output * 60.0 / 1000.0,
            "mean_arterial_pressure": pa,
            "systemic_flow": systemic_flow,
            "splanchnic_arterial_flow": splanchnic_arterial_flow,
            "lower_limb_arterial_flow": lower_limb_arterial_flow,
            "splanchnic_venous_return": splanchnic_venous_return,
            "lower_limb_venous_return": lower_limb_venous_return,
            "muscle_pump_flow": muscle_pump_flow,
            "venous_return": splanchnic_venous_return + lower_limb_venous_return,
            "systemic_resistance_effective": parallel_resistance,
            "splanchnic_arterial_resistance_effective": splanchnic_arterial_resistance,
            "lower_limb_arterial_resistance_effective": lower_limb_arterial_resistance,
            "lower_limb_venous_resistance_effective": lower_limb_venous_resistance,
            "cerebral_pressure_target": cerebral_pressure_target,
            "cerebral_flow_target": cerebral_target,
            "metabolic_capacity": capacity,
            "oxygen_extraction": float(extraction),
            "functional_capacity": capacity
            * extraction
            / p.functional_capacity_reference_extraction,
        }

    def rhs(self, t: float, y: np.ndarray, protocol: Sequence[ProtocolSegment]) -> np.ndarray:
        """Governing equations EQ-CV-001 through EQ-RCV-004."""
        p = self.parameters
        d = self._derived(t, y, protocol)
        _, _, _, _, cardiac_sym, vascular_sym, vagal, load, delayed, pem, cerebral = y
        _, exertion, _, _ = self._inputs(t, protocol)
        pressure_error = (
            p.baroreflex_pressure_setpoint - d["baroreflex_pressure"]
        ) / p.baroreflex_pressure_scale
        pressure_error = float(np.clip(pressure_error, -40.0, 40.0))
        baroreflex_target = 1.0 / (1.0 + np.exp(-pressure_error))
        d_cardiac_sympathetic = (
            baroreflex_target - cardiac_sym
        ) / p.cardiac_sympathetic_time_constant
        d_vascular_sympathetic = (
            baroreflex_target - vascular_sym
        ) / p.vascular_sympathetic_time_constant
        d_vagal = (1.0 - baroreflex_target - vagal) / p.vagal_time_constant

        # Volume conservation: all four volume derivatives telescope exactly.
        d_arterial = d["cardiac_output"] - d["systemic_flow"]
        d_central = d["venous_return"] - d["cardiac_output"]
        d_splanchnic = d["splanchnic_arterial_flow"] - d["splanchnic_venous_return"]
        d_lower_limb = d["lower_limb_arterial_flow"] - d["lower_limb_venous_return"]

        # Phenomenological PEM cascade with asymmetric onset/recovery.
        load_target = exertion / d["metabolic_capacity"]
        d_load = (load_target - load) / p.exertional_load_time_constant
        d_delayed = (load - delayed) / p.delayed_stress_time_constant
        pem_target = p.pem_response_gain * max(
            0.0, (delayed - p.pem_trigger_threshold) / (1.0 - p.pem_trigger_threshold)
        )
        pem_target = min(1.0, pem_target)
        tau_pem = p.pem_onset_time_constant if pem_target > pem else p.pem_recovery_time_constant
        d_pem = (pem_target - pem) / tau_pem

        tau_cerebral = (
            p.cerebral_decline_time_constant
            if d["cerebral_flow_target"] < cerebral
            else p.cerebral_recovery_time_constant
        )
        d_cerebral = (d["cerebral_flow_target"] - cerebral) / tau_cerebral
        return np.array(
            [
                d_arterial,
                d_central,
                d_splanchnic,
                d_lower_limb,
                d_cardiac_sympathetic,
                d_vascular_sympathetic,
                d_vagal,
                d_load,
                d_delayed,
                d_pem,
                d_cerebral,
            ]
        )

    def simulate(
        self,
        protocol: Sequence[ProtocolSegment],
        sample_interval: float = 1.0,
        max_step: float = 2.0,
        rtol: float = 1e-7,
        atol: float = 1e-8,
        seed: int = 0,
    ) -> SimulationResult:
        if not protocol:
            raise ValueError("At least one protocol segment is required")
        for segment in protocol:
            segment.validate()
        if any(b.start < a.end for a, b in zip(protocol, protocol[1:], strict=False)):
            raise ValueError("Protocol segments must be ordered and non-overlapping")
        if protocol[0].start != 0:
            raise ValueError("Protocol must start at t=0")
        duration = protocol[-1].end
        t_eval = np.arange(0.0, duration + sample_interval * 0.5, sample_interval)
        if t_eval[-1] > duration:
            t_eval = t_eval[t_eval <= duration]
        if t_eval[-1] != duration:
            t_eval = np.append(t_eval, duration)
        y0 = self.initial_state()
        solution = solve_ivp(
            lambda t, y: self.rhs(t, y, protocol),
            (0.0, duration),
            y0,
            method="DOP853",
            t_eval=t_eval,
            max_step=max_step,
            rtol=rtol,
            atol=atol,
        )
        if not solution.success:
            raise RuntimeError(f"Simulation failed: {solution.message}")
        if not np.all(np.isfinite(solution.y)):
            raise RuntimeError("Simulation produced non-finite states")
        if np.min(solution.y[:4]) < -1e-6:
            raise RuntimeError("Simulation produced a negative stressed-blood-volume state")
        if np.min(solution.y[4:7]) < -1e-8 or np.max(solution.y[4:7]) > 1.0 + 1e-8:
            raise RuntimeError("Simulation produced an autonomic state outside [0, 1]")
        if np.min(solution.y[10]) < -1e-8 or np.max(solution.y[10]) > 1.25 + 1e-8:
            raise RuntimeError(
                "Simulation produced a cerebral-flow index outside its declared bounds"
            )
        derived = [
            self._derived(t, y, protocol) for t, y in zip(solution.t, solution.y.T, strict=True)
        ]
        output_names = [
            "heart_rate",
            "mean_arterial_pressure",
            "central_venous_pressure",
            "splanchnic_venous_pressure",
            "lower_limb_venous_pressure",
            "baroreflex_pressure",
            "cerebral_perfusion_pressure",
            "stroke_volume",
            "cardiac_output",
            "cardiac_output_l_min",
            "systemic_flow",
            "splanchnic_arterial_flow",
            "lower_limb_arterial_flow",
            "splanchnic_venous_return",
            "lower_limb_venous_return",
            "muscle_pump_flow",
            "venous_return",
            "systemic_resistance_effective",
            "splanchnic_arterial_resistance_effective",
            "lower_limb_arterial_resistance_effective",
            "lower_limb_venous_resistance_effective",
            "metabolic_capacity",
            "oxygen_extraction",
            "functional_capacity",
            "cerebral_pressure_target",
            "cerebral_flow_target",
        ]
        outputs = {name: np.array([d[name] for d in derived]) for name in output_names}
        outputs["cerebral_flow_index"] = solution.y[10].copy()
        outputs["pem_severity"] = solution.y[9].copy()
        outputs["exertional_load"] = solution.y[7].copy()
        outputs["delayed_stress"] = solution.y[8].copy()
        outputs["cardiac_sympathetic_state"] = solution.y[4].copy()
        outputs["vascular_sympathetic_state"] = solution.y[5].copy()
        outputs["vagal_state"] = solution.y[6].copy()
        outputs["sympathetic_state"] = 0.5 * (solution.y[4] + solution.y[5])
        outputs["arterial_volume"] = solution.y[0].copy()
        outputs["central_venous_volume"] = solution.y[1].copy()
        outputs["splanchnic_venous_volume"] = solution.y[2].copy()
        outputs["lower_limb_venous_volume"] = solution.y[3].copy()
        protocol_payload = [asdict(s) for s in protocol]
        config_hash = hashlib.sha256(
            json.dumps(
                {"parameters": asdict(self.parameters), "protocol": protocol_payload},
                sort_keys=True,
            ).encode()
        ).hexdigest()
        metadata = {
            "model": "ocpe:disease-models/shared-physiology",
            "model_version": "0.2.0",
            "phenotype_id": self.phenotype_id,
            "provenance": self.provenance,
            "configuration_sha256": config_hash,
            "ocpe_commit": OCPE_COMMIT,
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "scipy_version": scipy.__version__,
            "seed": seed,
            "solver": {
                "method": "DOP853",
                "sample_interval": sample_interval,
                "max_step": max_step,
                "rtol": rtol,
                "atol": atol,
                "seed": seed,
            },
            "scientific_status": "research demonstration; not clinically validated",
        }
        return SimulationResult(
            time=solution.t,
            states=solution.y,
            outputs=outputs,
            parameters=self.parameters,
            phenotype_id=self.phenotype_id,
            protocol=protocol,
            metadata=metadata,
        )
