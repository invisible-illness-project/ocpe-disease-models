"""Executable, beat-averaged physiological models.

The cardiovascular equations conserve stressed blood volume across arterial,
central-venous and peripheral-venous compartments. The PEM equations are an
explicitly phenomenological exertion/delay/recovery approximation, not a claim
that the cellular cause of PEM is known. Time is seconds, volumes are mL,
pressures are mmHg, and flows are mL/s unless stated otherwise.
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
    "peripheral_venous_volume",
    "sympathetic_state",
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

    # Vascular compliances (mL/mmHg) and resistances (mmHg s/mL).
    arterial_compliance: float = 1.5
    central_venous_compliance: float = 140.0
    peripheral_venous_compliance: float = 120.0
    systemic_resistance: float = 1.1020408163265305
    venous_return_resistance: float = 0.061224489795918366
    resistance_sympathetic_gain: float = 0.8
    gravity_pressure_offset: float = 8.0

    # Initial stressed volumes (mL); their sum is conserved by the equations.
    arterial_volume_initial: float = 150.0
    central_venous_volume_initial: float = 700.0
    peripheral_venous_volume_initial: float = 1200.0
    blood_volume_factor: float = 1.0

    # Cardiac and baroreflex operating point.
    stroke_volume_max: float = 100.0
    stroke_volume_half_volume: float = 300.0
    contractility_sympathetic_gain: float = 0.25
    heart_rate_base: float = 50.0
    heart_rate_sympathetic_gain: float = 40.0
    baroreflex_pressure_setpoint: float = 100.0
    baroreflex_pressure_scale: float = 2.0
    sympathetic_time_constant: float = 4.0
    exercise_heart_rate_gain: float = 70.0
    exercise_resistance_reduction: float = 0.30

    # Cerebral flow approximation (dimensionless index).
    cerebral_pressure_exponent: float = 0.8
    cerebral_orthostatic_impairment: float = 0.0
    cerebral_decline_time_constant: float = 5.0
    cerebral_recovery_time_constant: float = 12.0

    # Oxygen use and exertional capacity (dimensionless fractions).
    baseline_metabolic_capacity: float = 1.0
    oxygen_extraction_fraction: float = 0.78
    pem_capacity_penalty: float = 0.5
    pem_extraction_penalty: float = 0.10

    # Phenomenological PEM dynamics (seconds and dimensionless states).
    exertional_load_time_constant: float = 1800.0
    delayed_stress_time_constant: float = 21600.0
    pem_onset_time_constant: float = 86400.0
    pem_recovery_time_constant: float = 172800.0
    pem_trigger_threshold: float = 99.0
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
    label: str = "segment"

    def validate(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError(f"Invalid segment bounds: {self}")
        if not 0 <= self.upright <= 1 or not 0 <= self.exertion <= 1:
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
        upright_starts = [s.start for s in self.protocol if s.upright > 0]
        result: dict[str, Any] = {
            "phenotype_id": self.phenotype_id,
            "duration_s": float(self.time[-1]),
            "samples": len(self.time),
            "heart_rate_final_bpm": float(self.outputs["heart_rate"][-1]),
            "mean_arterial_pressure_final_mmHg": float(
                self.outputs["mean_arterial_pressure"][-1]
            ),
            "pem_peak": float(np.max(self.outputs["pem_severity"])),
            "functional_capacity_final": float(self.outputs["functional_capacity"][-1]),
        }
        if upright_starts:
            start = upright_starts[0]
            baseline_end = max(0.0, start - 1.0)
            baseline = self.metric("heart_rate", 0.0, baseline_end)
            standing = self.metric(
                "heart_rate", start, min(start + 300.0, float(self.time[-1])), "max"
            )
            result.update(
                {
                    "heart_rate_baseline_bpm": baseline,
                    "heart_rate_upright_peak_bpm": standing,
                    "orthostatic_heart_rate_rise_bpm": standing - baseline,
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
        positive = {
            "arterial_compliance": p.arterial_compliance,
            "central_venous_compliance": p.central_venous_compliance,
            "peripheral_venous_compliance": p.peripheral_venous_compliance,
            "systemic_resistance": p.systemic_resistance,
            "venous_return_resistance": p.venous_return_resistance,
            "stroke_volume_max": p.stroke_volume_max,
            "stroke_volume_half_volume": p.stroke_volume_half_volume,
            "sympathetic_time_constant": p.sympathetic_time_constant,
            "exertional_load_time_constant": p.exertional_load_time_constant,
            "delayed_stress_time_constant": p.delayed_stress_time_constant,
            "pem_onset_time_constant": p.pem_onset_time_constant,
            "pem_recovery_time_constant": p.pem_recovery_time_constant,
        }
        for name, value in positive.items():
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if p.blood_volume_factor <= 0:
            raise ValueError("blood_volume_factor must be positive")
        if not 0 < p.oxygen_extraction_fraction < 1:
            raise ValueError("oxygen_extraction_fraction must be in (0, 1)")

    def initial_state(self) -> np.ndarray:
        p = self.parameters
        factor = p.blood_volume_factor
        arterial = p.arterial_volume_initial * factor
        central = p.central_venous_volume_initial * factor
        peripheral = p.peripheral_venous_volume_initial * factor
        pressure = arterial / p.arterial_compliance
        cerebral = max(0.05, pressure / p.baroreflex_pressure_setpoint) ** p.cerebral_pressure_exponent
        return np.array(
            [arterial, central, peripheral, 0.5, 0.0, 0.0, 0.0, cerebral], dtype=float
        )

    @staticmethod
    def _inputs(t: float, protocol: Sequence[ProtocolSegment]) -> tuple[float, float]:
        for segment in protocol:
            if segment.start <= t < segment.end:
                return segment.upright, segment.exertion
        if t == protocol[-1].end:
            return protocol[-1].upright, protocol[-1].exertion
        raise ValueError(f"Time {t} is outside the protocol")

    def _derived(self, t: float, y: np.ndarray, protocol: Sequence[ProtocolSegment]) -> dict[str, float]:
        p = self.parameters
        va, vc, vp, sympathetic, _, _, pem, _ = np.maximum(y, 0.0)
        upright, exertion = self._inputs(t, protocol)
        pa = va / p.arterial_compliance
        pc = vc / p.central_venous_compliance
        pp = vp / p.peripheral_venous_compliance
        pem = min(1.0, pem)
        capacity = max(
            0.05, p.baseline_metabolic_capacity * (1.0 - p.pem_capacity_penalty * pem)
        )
        resistance = max(
            0.1,
            p.systemic_resistance
            * (1.0 + p.resistance_sympathetic_gain * (sympathetic - 0.5))
            * (1.0 - p.exercise_resistance_reduction * exertion),
        )
        contractility = max(0.2, 1.0 + p.contractility_sympathetic_gain * (sympathetic - 0.5))
        stroke_volume = p.stroke_volume_max * contractility * vc / (vc + p.stroke_volume_half_volume)
        heart_rate = np.clip(
            p.heart_rate_base
            + p.heart_rate_sympathetic_gain * sympathetic
            + p.exercise_heart_rate_gain * exertion * capacity,
            30.0,
            220.0,
        )
        cardiac_output = heart_rate / 60.0 * stroke_volume
        systemic_flow = max(0.0, (pa - pp) / resistance)
        venous_return = max(
            0.0,
            (pp - pc - p.gravity_pressure_offset * upright) / p.venous_return_resistance,
        )
        cerebral_target = max(0.0, pa / p.baroreflex_pressure_setpoint) ** p.cerebral_pressure_exponent
        cerebral_target *= max(0.0, 1.0 - p.cerebral_orthostatic_impairment * upright)
        extraction = np.clip(p.oxygen_extraction_fraction * (1.0 - p.pem_extraction_penalty * pem), 0.0, 0.99)
        return {
            "arterial_pressure": pa,
            "central_venous_pressure": pc,
            "peripheral_venous_pressure": pp,
            "heart_rate": float(heart_rate),
            "stroke_volume": stroke_volume,
            "cardiac_output": cardiac_output,
            "cardiac_output_l_min": cardiac_output * 60.0 / 1000.0,
            "mean_arterial_pressure": pa,
            "systemic_flow": systemic_flow,
            "venous_return": venous_return,
            "systemic_resistance_effective": resistance,
            "cerebral_flow_target": cerebral_target,
            "metabolic_capacity": capacity,
            "oxygen_extraction": float(extraction),
            "functional_capacity": capacity * extraction / 0.78,
        }

    def rhs(self, t: float, y: np.ndarray, protocol: Sequence[ProtocolSegment]) -> np.ndarray:
        """Governing equations EQ-CV-001 through EQ-RCV-004."""
        p = self.parameters
        d = self._derived(t, y, protocol)
        _, _, _, sympathetic, load, delayed, pem, cerebral = y
        _, exertion = self._inputs(t, protocol)
        pressure_error = (
            p.baroreflex_pressure_setpoint - d["arterial_pressure"]
        ) / p.baroreflex_pressure_scale
        pressure_error = float(np.clip(pressure_error, -40.0, 40.0))
        sympathetic_target = 1.0 / (1.0 + np.exp(-pressure_error))
        d_sympathetic = (sympathetic_target - sympathetic) / p.sympathetic_time_constant

        # Volume conservation: dVa + dVc + dVp = 0 exactly.
        d_arterial = d["cardiac_output"] - d["systemic_flow"]
        d_peripheral = d["systemic_flow"] - d["venous_return"]
        d_central = d["venous_return"] - d["cardiac_output"]

        # Phenomenological PEM cascade with asymmetric onset/recovery.
        load_target = exertion / d["metabolic_capacity"]
        d_load = (load_target - load) / p.exertional_load_time_constant
        d_delayed = (load - delayed) / p.delayed_stress_time_constant
        pem_target = p.pem_response_gain * max(
            0.0, (delayed - p.pem_trigger_threshold) / max(1e-9, 1.0 - p.pem_trigger_threshold)
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
                d_peripheral,
                d_sympathetic,
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
        derived = [self._derived(t, y, protocol) for t, y in zip(solution.t, solution.y.T, strict=True)]
        output_names = [
            "heart_rate",
            "mean_arterial_pressure",
            "central_venous_pressure",
            "peripheral_venous_pressure",
            "stroke_volume",
            "cardiac_output_l_min",
            "venous_return",
            "systemic_resistance_effective",
            "metabolic_capacity",
            "oxygen_extraction",
            "functional_capacity",
            "cerebral_flow_target",
        ]
        outputs = {name: np.array([d[name] for d in derived]) for name in output_names}
        outputs["cerebral_flow_index"] = solution.y[7].copy()
        outputs["pem_severity"] = solution.y[6].copy()
        outputs["exertional_load"] = solution.y[4].copy()
        outputs["delayed_stress"] = solution.y[5].copy()
        outputs["sympathetic_state"] = solution.y[3].copy()
        protocol_payload = [asdict(s) for s in protocol]
        config_hash = hashlib.sha256(
            json.dumps(
                {"parameters": asdict(self.parameters), "protocol": protocol_payload},
                sort_keys=True,
            ).encode()
        ).hexdigest()
        metadata = {
            "model": "ocpe:disease-models/shared-physiology",
            "model_version": "0.1.0",
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
