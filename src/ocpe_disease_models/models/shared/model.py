"""Executable, beat-averaged physiological models.

The cardiovascular equations conserve stressed blood volume across arterial,
central-venous, splanchnic-venous, lower-limb-venous and other-systemic-venous
compartments. Distinct vagal, cardiac-sympathetic and vascular-sympathetic
states control effectors. Rhythmic muscle activity transfers lower-limb venous
volume without creating blood. The PEM equations are an explicitly
phenomenological exertion/delay/recovery approximation, not a claim that the
cellular cause of PEM is known. Time is seconds, volumes are mL, pressures are
mmHg, and flows are mL/s unless stated otherwise.
"""

from __future__ import annotations

import hashlib
import json
import math
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
    "other_systemic_venous_volume",
    "cardiac_sympathetic_state",
    "vascular_sympathetic_state",
    "vagal_state",
    "exertional_load",
    "delayed_stress",
    "pem_severity",
    "cerebral_flow_index",
)

# Indices into the state vector, kept consistent with STATE_NAMES.
_ARTERIAL_VOLUME = STATE_NAMES.index("arterial_volume")
_CENTRAL_VENOUS_VOLUME = STATE_NAMES.index("central_venous_volume")
_SPLANCHNIC_VENOUS_VOLUME = STATE_NAMES.index("splanchnic_venous_volume")
_LOWER_LIMB_VENOUS_VOLUME = STATE_NAMES.index("lower_limb_venous_volume")
_OTHER_SYSTEMIC_VENOUS_VOLUME = STATE_NAMES.index("other_systemic_venous_volume")
_CARDIAC_SYMPATHETIC_STATE = STATE_NAMES.index("cardiac_sympathetic_state")
_VASCULAR_SYMPATHETIC_STATE = STATE_NAMES.index("vascular_sympathetic_state")
_VAGAL_STATE = STATE_NAMES.index("vagal_state")
_EXERTIONAL_LOAD = STATE_NAMES.index("exertional_load")
_DELAYED_STRESS = STATE_NAMES.index("delayed_stress")
_PEM_SEVERITY = STATE_NAMES.index("pem_severity")
_CEREBRAL_FLOW_INDEX = STATE_NAMES.index("cerebral_flow_index")
_VOLUME_STATE_COUNT = 5

# Mercury-column conversion: 1 cm H2O-equivalent blood column per cm of height.
HYDROSTATIC_MMHG_PER_CM = 0.7356

_BAROREFLEX_WEIGHT_TOLERANCE = 1e-6


@dataclass(frozen=True)
class ModelParameters:
    """Parameters for the shared model; defaults define the healthy reference.

    Values not identified as direct clinical measurements in the parameter
    registry are computational operating-point or calibration assumptions.
    """

    # Regional vascular compliances (mL/mmHg) and resistances (mmHg s/mL).
    arterial_compliance: float = 1.5
    central_venous_compliance: float = 140.0
    splanchnic_venous_compliance: float = 90.0
    lower_limb_venous_compliance: float = 60.0
    other_systemic_venous_compliance: float = 20.0
    # Second-order elastance above each dependent bed's supine stressed volume.
    # This represents limited venous distensibility without adding a state or
    # changing the conserved-volume equations.
    dependent_venous_stiffening_mmHg_per_mL2: float = 0.0001
    splanchnic_arterial_resistance: float = 4.408163265306122
    lower_limb_arterial_resistance: float = 4.408163265306122
    other_systemic_arterial_resistance: float = 2.204081632653061
    splanchnic_venous_resistance: float = 0.24489795918367346
    lower_limb_venous_resistance: float = 0.24489795918367346
    other_systemic_venous_resistance: float = 0.12244897959183673
    splanchnic_resistance_sympathetic_gain: float = 0.45
    lower_limb_resistance_sympathetic_gain: float = 0.45
    other_systemic_resistance_sympathetic_gain: float = 0.45
    splanchnic_hydrostatic_height_cm: float = 13.3
    lower_limb_hydrostatic_height_cm: float = 26.6
    other_systemic_hydrostatic_height_cm: float = 4.5

    # Initial stressed volumes/pressures; all five volumes conserve their sum.
    arterial_volume_initial: float = 150.0
    central_venous_volume_initial: float = 700.0
    splanchnic_venous_pressure_initial: float = 10.0
    lower_limb_venous_pressure_initial: float = 10.0
    other_systemic_venous_pressure_initial: float = 10.0
    blood_volume_factor: float = 1.0

    # Cardiac and differentiated baroreflex operating point.
    stroke_volume_max: float = 100.0
    stroke_volume_half_volume: float = 300.0
    contractility_sympathetic_gain: float = 0.1
    heart_rate_rest: float = 70.0
    heart_rate_cardiac_sympathetic_gain: float = 13.6
    heart_rate_vagal_gain: float = 13.6
    aortic_baroreflex_pressure_setpoint: float = 100.0
    carotid_baroreflex_pressure_setpoint: float = 100.0
    aortic_baroreflex_pressure_scale: float = 2.0
    carotid_baroreflex_pressure_scale: float = 2.0
    aortic_baroreflex_weight: float = 0.35
    carotid_baroreflex_weight: float = 0.65
    aortic_baroreceptor_height_cm: float = 0.0
    carotid_baroreceptor_height_cm: float = 25.0
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
    brain_hydrostatic_height_cm: float = 27.0
    cerebral_outflow_pressure_mmHg: float = 5.0
    cerebral_reference_perfusion_pressure: float = 95.0
    cerebral_autoregulation_residual_slope: float = 0.25
    cerebral_orthostatic_impairment: float = 0.0
    cerebral_decline_time_constant: float = 5.0
    cerebral_recovery_time_constant: float = 12.0
    end_tidal_co2_reference_mmHg: float = 40.0
    cerebral_co2_reactivity_per_mmHg: float = 0.035
    cerebral_co2_extrapolation_limit_mmHg: float = 15.0

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
    """A constant-input segment of a simulation protocol.

    Posture is specified either by the legacy ``upright`` fraction (mapped to
    a tilt angle through ``arcsin(upright)``, so 1.0 is 90 degrees) or by an
    explicit ``tilt_angle_deg`` in [0, 90]; specifying both is an error.
    During ``transition_duration`` the posture angle is linearly interpolated
    from the previous segment's angle; all other inputs remain piecewise
    constant. ``end_tidal_co2_mmHg=None`` selects the model reference value.
    """

    start: float
    end: float
    upright: float | None = None
    tilt_angle_deg: float | None = None
    end_tidal_co2_mmHg: float | None = None
    transition_duration: float = 0.0
    exertion: float = 0.0
    rhythmic_muscle_activity: float = 0.0
    sustained_muscle_contraction: float = 0.0
    label: str = "segment"

    def resolved_tilt_angle_deg(self) -> float:
        """Resolve the segment's steady posture angle in degrees."""
        if self.tilt_angle_deg is not None:
            return self.tilt_angle_deg
        if self.upright is not None:
            return math.degrees(math.asin(self.upright))
        return 0.0

    def resolved_end_tidal_co2(self, reference_mmHg: float) -> float:
        """Resolve end-tidal CO2, falling back to the model reference."""
        if self.end_tidal_co2_mmHg is None:
            return reference_mmHg
        return self.end_tidal_co2_mmHg

    def validate(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError(f"Invalid segment bounds: {self}")
        if self.upright is not None and self.tilt_angle_deg is not None:
            raise ValueError(
                "Specify only one of upright or tilt_angle_deg, not both"
            )
        if self.upright is not None and not 0 <= self.upright <= 1:
            raise ValueError("upright must be normalized to [0, 1]")
        if self.tilt_angle_deg is not None and not 0 <= self.tilt_angle_deg <= 90:
            raise ValueError("tilt_angle_deg must be in [0, 90]")
        if not 0 <= self.transition_duration <= self.end - self.start:
            raise ValueError(
                "transition_duration must be nonnegative and no longer than the segment"
            )
        if self.end_tidal_co2_mmHg is not None and (
            not math.isfinite(self.end_tidal_co2_mmHg)
            or self.end_tidal_co2_mmHg <= 0
        ):
            raise ValueError(
                "end_tidal_co2_mmHg must be finite and positive when provided"
            )
        inputs = (
            self.exertion,
            self.rhythmic_muscle_activity,
            self.sustained_muscle_contraction,
        )
        if any(not 0 <= value <= 1 for value in inputs):
            raise ValueError("Protocol inputs must be normalized to [0, 1]")


@dataclass(frozen=True)
class _ResolvedInputs:
    """Protocol inputs resolved at one time point."""

    tilt_angle_deg: float
    tilt_radians: float
    upright: float  # Vertical sine of the tilt angle.
    end_tidal_co2_mmHg: float
    exertion: float
    rhythmic_muscle_activity: float
    sustained_muscle_contraction: float


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
        upright_segments = [s for s in self.protocol if s.resolved_tilt_angle_deg() > 0]
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
            first_upright = upright_segments[0]
            first_index = next(
                index for index, segment in enumerate(self.protocol) if segment is first_upright
            )
            start = first_upright.start
            upright_end = first_upright.end
            # Active standing and sustained quiet standing are distinct input
            # segments but one continuous orthostatic bout.
            for segment in self.protocol[first_index + 1 :]:
                if segment.resolved_tilt_angle_deg() <= 0:
                    break
                upright_end = segment.end
            upright_end = min(float(self.time[-1]), upright_end)
            baseline_end = max(0.0, start - 2.0)
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
            "other_systemic_venous_compliance",
            "splanchnic_arterial_resistance",
            "lower_limb_arterial_resistance",
            "other_systemic_arterial_resistance",
            "splanchnic_venous_resistance",
            "lower_limb_venous_resistance",
            "other_systemic_venous_resistance",
            "arterial_volume_initial",
            "central_venous_volume_initial",
            "splanchnic_venous_pressure_initial",
            "lower_limb_venous_pressure_initial",
            "other_systemic_venous_pressure_initial",
            "blood_volume_factor",
            "stroke_volume_max",
            "stroke_volume_half_volume",
            "heart_rate_rest",
            "aortic_baroreflex_pressure_setpoint",
            "carotid_baroreflex_pressure_setpoint",
            "aortic_baroreflex_pressure_scale",
            "carotid_baroreflex_pressure_scale",
            "cardiac_sympathetic_time_constant",
            "vascular_sympathetic_time_constant",
            "vagal_time_constant",
            "muscle_pump_frequency",
            "muscle_pump_half_volume",
            "cerebral_reference_perfusion_pressure",
            "cerebral_decline_time_constant",
            "cerebral_recovery_time_constant",
            "end_tidal_co2_reference_mmHg",
            "cerebral_co2_extrapolation_limit_mmHg",
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
            "dependent_venous_stiffening_mmHg_per_mL2",
            "splanchnic_resistance_sympathetic_gain",
            "lower_limb_resistance_sympathetic_gain",
            "other_systemic_resistance_sympathetic_gain",
            "splanchnic_hydrostatic_height_cm",
            "lower_limb_hydrostatic_height_cm",
            "other_systemic_hydrostatic_height_cm",
            "aortic_baroreflex_weight",
            "carotid_baroreflex_weight",
            "aortic_baroreceptor_height_cm",
            "carotid_baroreceptor_height_cm",
            "brain_hydrostatic_height_cm",
            "cerebral_outflow_pressure_mmHg",
            "cerebral_co2_reactivity_per_mmHg",
            "contractility_sympathetic_gain",
            "heart_rate_cardiac_sympathetic_gain",
            "heart_rate_vagal_gain",
            "exercise_heart_rate_gain",
            "muscle_pump_stroke_volume",
            "muscle_pump_effectiveness",
            "sustained_contraction_resistance_gain",
            "pem_response_gain",
        )
        for name in nonnegative_names:
            if getattr(p, name) < 0:
                raise ValueError(f"{name} must be nonnegative")
        for name in (
            "splanchnic_resistance_sympathetic_gain",
            "lower_limb_resistance_sympathetic_gain",
            "other_systemic_resistance_sympathetic_gain",
        ):
            if getattr(p, name) >= 2:
                raise ValueError(f"{name} must be below 2 to keep resistance positive")
        weight_sum = p.aortic_baroreflex_weight + p.carotid_baroreflex_weight
        if abs(weight_sum - 1.0) > _BAROREFLEX_WEIGHT_TOLERANCE:
            raise ValueError(
                "aortic_baroreflex_weight and carotid_baroreflex_weight must sum to 1"
            )
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
        if not 0 < p.cerebral_autoregulation_residual_slope < 1:
            raise ValueError("cerebral_autoregulation_residual_slope must be in (0, 1)")
        if not 0 <= p.pem_trigger_threshold < 1:
            raise ValueError("pem_trigger_threshold must be in [0, 1)")

    def _cerebral_pressure_target(self, cerebral_perfusion_pressure: float) -> float:
        """Bounded autoregulation pressure curve shared by init and dynamics."""
        p = self.parameters
        ratio = cerebral_perfusion_pressure / p.cerebral_reference_perfusion_pressure
        slope = p.cerebral_autoregulation_residual_slope
        return ratio / (slope + (1.0 - slope) * ratio)

    def initial_state(self) -> np.ndarray:
        p = self.parameters
        factor = p.blood_volume_factor
        arterial = p.arterial_volume_initial * factor
        central = p.central_venous_volume_initial * factor
        splanchnic = p.splanchnic_venous_pressure_initial * p.splanchnic_venous_compliance * factor
        lower_limb = p.lower_limb_venous_pressure_initial * p.lower_limb_venous_compliance * factor
        other = p.other_systemic_venous_pressure_initial * p.other_systemic_venous_compliance * factor
        arterial_pressure = arterial / p.arterial_compliance
        # Supine posture and reference CO2: the hydrostatic term is zero and
        # the CO2 factor is one, so the initial index matches the steady state.
        cerebral_perfusion_pressure = max(
            0.0, arterial_pressure - p.cerebral_outflow_pressure_mmHg
        )
        cerebral_initial = self._cerebral_pressure_target(cerebral_perfusion_pressure)
        state = np.zeros(len(STATE_NAMES), dtype=float)
        state[_ARTERIAL_VOLUME] = arterial
        state[_CENTRAL_VENOUS_VOLUME] = central
        state[_SPLANCHNIC_VENOUS_VOLUME] = splanchnic
        state[_LOWER_LIMB_VENOUS_VOLUME] = lower_limb
        state[_OTHER_SYSTEMIC_VENOUS_VOLUME] = other
        state[_CARDIAC_SYMPATHETIC_STATE] = 0.5
        state[_VASCULAR_SYMPATHETIC_STATE] = 0.5
        state[_VAGAL_STATE] = 0.5
        state[_CEREBRAL_FLOW_INDEX] = cerebral_initial
        return state

    @staticmethod
    def _inputs(
        t: float,
        protocol: Sequence[ProtocolSegment],
        end_tidal_co2_reference_mmHg: float,
    ) -> _ResolvedInputs:
        previous_angle_deg = 0.0
        for segment in protocol:
            in_segment = segment.start <= t < segment.end
            at_final_end = segment is protocol[-1] and t == segment.end
            if in_segment or at_final_end:
                angle_deg = segment.resolved_tilt_angle_deg()
                transition_end = segment.start + segment.transition_duration
                if segment.transition_duration > 0 and t < transition_end:
                    fraction = (t - segment.start) / segment.transition_duration
                    angle_deg = previous_angle_deg + (angle_deg - previous_angle_deg) * fraction
                tilt_radians = math.radians(angle_deg)
                return _ResolvedInputs(
                    tilt_angle_deg=angle_deg,
                    tilt_radians=tilt_radians,
                    upright=math.sin(tilt_radians),
                    end_tidal_co2_mmHg=segment.resolved_end_tidal_co2(
                        end_tidal_co2_reference_mmHg
                    ),
                    exertion=segment.exertion,
                    rhythmic_muscle_activity=segment.rhythmic_muscle_activity,
                    sustained_muscle_contraction=segment.sustained_muscle_contraction,
                )
            previous_angle_deg = segment.resolved_tilt_angle_deg()
        raise ValueError(f"Time {t} is outside the protocol")

    @staticmethod
    def _hydrostatic_pressure(height_cm: float, sin_tilt: float) -> float:
        return HYDROSTATIC_MMHG_PER_CM * height_cm * sin_tilt

    def _derived(
        self, t: float, y: np.ndarray, protocol: Sequence[ProtocolSegment]
    ) -> dict[str, float]:
        p = self.parameters
        if not np.all(np.isfinite(y)):
            raise FloatingPointError("Non-finite state passed to physiological equations")
        va = y[_ARTERIAL_VOLUME]
        vc = y[_CENTRAL_VENOUS_VOLUME]
        vs = y[_SPLANCHNIC_VENOUS_VOLUME]
        vl = y[_LOWER_LIMB_VENOUS_VOLUME]
        vo = y[_OTHER_SYSTEMIC_VENOUS_VOLUME]
        cardiac_sym = y[_CARDIAC_SYMPATHETIC_STATE]
        vascular_sym = y[_VASCULAR_SYMPATHETIC_STATE]
        vagal = y[_VAGAL_STATE]
        pem = min(1.0, y[_PEM_SEVERITY])
        inputs = self._inputs(t, protocol, p.end_tidal_co2_reference_mmHg)
        sin_tilt = inputs.upright
        pa = va / p.arterial_compliance
        pc = vc / p.central_venous_compliance
        splanchnic_supine_volume = (
            p.splanchnic_venous_pressure_initial
            * p.splanchnic_venous_compliance
            * p.blood_volume_factor
        )
        lower_limb_supine_volume = (
            p.lower_limb_venous_pressure_initial
            * p.lower_limb_venous_compliance
            * p.blood_volume_factor
        )
        stiffening = p.dependent_venous_stiffening_mmHg_per_mL2
        ps = vs / p.splanchnic_venous_compliance + stiffening * max(
            0.0, vs - splanchnic_supine_volume
        ) ** 2
        pl = vl / p.lower_limb_venous_compliance + stiffening * max(
            0.0, vl - lower_limb_supine_volume
        ) ** 2
        po = vo / p.other_systemic_venous_compliance
        capacity = max(0.05, p.baseline_metabolic_capacity * (1.0 - p.pem_capacity_penalty * pem))
        splanchnic_arterial_resistance = p.splanchnic_arterial_resistance * (
            1.0 + p.splanchnic_resistance_sympathetic_gain * (vascular_sym - 0.5)
        )
        lower_limb_arterial_resistance = (
            p.lower_limb_arterial_resistance
            * (1.0 + p.lower_limb_resistance_sympathetic_gain * (vascular_sym - 0.5))
            * (1.0 - p.exercise_resistance_reduction * inputs.exertion)
        )
        other_systemic_arterial_resistance = p.other_systemic_arterial_resistance * (
            1.0 + p.other_systemic_resistance_sympathetic_gain * (vascular_sym - 0.5)
        )
        lower_limb_venous_resistance = p.lower_limb_venous_resistance * (
            1.0 + p.sustained_contraction_resistance_gain * inputs.sustained_muscle_contraction
        )
        contractility = max(0.2, 1.0 + p.contractility_sympathetic_gain * (cardiac_sym - 0.5))
        stroke_volume = (
            p.stroke_volume_max * contractility * vc / (vc + p.stroke_volume_half_volume)
        )
        heart_rate = np.clip(
            p.heart_rate_rest
            + p.heart_rate_cardiac_sympathetic_gain * (cardiac_sym - 0.5)
            + p.heart_rate_vagal_gain * (0.5 - vagal)
            + p.exercise_heart_rate_gain * inputs.exertion * capacity,
            30.0,
            220.0,
        )
        cardiac_output = heart_rate / 60.0 * stroke_volume
        splanchnic_arterial_flow = max(0.0, (pa - ps) / splanchnic_arterial_resistance)
        lower_limb_arterial_flow = max(0.0, (pa - pl) / lower_limb_arterial_resistance)
        other_systemic_arterial_flow = max(
            0.0, (pa - po) / other_systemic_arterial_resistance
        )
        splanchnic_venous_return = max(
            0.0,
            (
                ps
                - pc
                - self._hydrostatic_pressure(p.splanchnic_hydrostatic_height_cm, sin_tilt)
            )
            / p.splanchnic_venous_resistance,
        )
        muscle_pump_flow = (
            p.muscle_pump_frequency
            * p.muscle_pump_stroke_volume
            * p.muscle_pump_effectiveness
            * inputs.rhythmic_muscle_activity
            * vl
            / (vl + p.muscle_pump_half_volume)
        )
        lower_limb_venous_return = (
            max(
                0.0,
                (
                    pl
                    - pc
                    - self._hydrostatic_pressure(p.lower_limb_hydrostatic_height_cm, sin_tilt)
                )
                / lower_limb_venous_resistance,
            )
            + muscle_pump_flow
        )
        other_systemic_venous_return = max(
            0.0,
            (
                po
                - pc
                - self._hydrostatic_pressure(p.other_systemic_hydrostatic_height_cm, sin_tilt)
            )
            / p.other_systemic_venous_resistance,
        )
        aortic_baroreceptor_pressure = max(
            0.0, pa - self._hydrostatic_pressure(p.aortic_baroreceptor_height_cm, sin_tilt)
        )
        carotid_sinus_pressure = max(
            0.0, pa - self._hydrostatic_pressure(p.carotid_baroreceptor_height_cm, sin_tilt)
        )
        aortic_error = (
            p.aortic_baroreflex_pressure_setpoint - aortic_baroreceptor_pressure
        ) / p.aortic_baroreflex_pressure_scale
        carotid_error = (
            p.carotid_baroreflex_pressure_setpoint - carotid_sinus_pressure
        ) / p.carotid_baroreflex_pressure_scale
        integrated_baroreflex_input = (
            p.aortic_baroreflex_weight * aortic_error
            + p.carotid_baroreflex_weight * carotid_error
        )
        baroreflex_target = 1.0 / (
            1.0 + math.exp(-float(np.clip(integrated_baroreflex_input, -40.0, 40.0)))
        )
        brain_arterial_pressure = max(
            0.0, pa - self._hydrostatic_pressure(p.brain_hydrostatic_height_cm, sin_tilt)
        )
        # Fixed effective downstream pressure approximation: explicitly NOT
        # thoracic central venous pressure or a separately resolved ICP.
        cerebral_outflow_pressure = p.cerebral_outflow_pressure_mmHg
        cerebral_perfusion_pressure = max(
            0.0, brain_arterial_pressure - cerebral_outflow_pressure
        )
        cerebral_pressure_target = self._cerebral_pressure_target(
            cerebral_perfusion_pressure
        )
        co2_deviation = float(
            np.clip(
                inputs.end_tidal_co2_mmHg - p.end_tidal_co2_reference_mmHg,
                -p.cerebral_co2_extrapolation_limit_mmHg,
                p.cerebral_co2_extrapolation_limit_mmHg,
            )
        )
        cerebral_co2_factor = math.exp(p.cerebral_co2_reactivity_per_mmHg * co2_deviation)
        cerebral_impairment_factor = max(
            0.0, 1.0 - p.cerebral_orthostatic_impairment * sin_tilt
        )
        cerebral_target = (
            cerebral_pressure_target * cerebral_co2_factor * cerebral_impairment_factor
        )
        extraction = np.clip(
            p.oxygen_extraction_fraction * (1.0 - p.pem_extraction_penalty * pem), 0.0, 0.99
        )
        systemic_flow = (
            splanchnic_arterial_flow + lower_limb_arterial_flow + other_systemic_arterial_flow
        )
        parallel_resistance = 1.0 / (
            1.0 / splanchnic_arterial_resistance
            + 1.0 / lower_limb_arterial_resistance
            + 1.0 / other_systemic_arterial_resistance
        )
        return {
            "arterial_pressure": pa,
            "central_venous_pressure": pc,
            "splanchnic_venous_pressure": ps,
            "lower_limb_venous_pressure": pl,
            "other_systemic_venous_pressure": po,
            "heart_level_mean_arterial_pressure": pa,
            "aortic_baroreceptor_pressure": aortic_baroreceptor_pressure,
            "carotid_sinus_pressure": carotid_sinus_pressure,
            "brain_arterial_pressure": brain_arterial_pressure,
            "integrated_baroreflex_input": integrated_baroreflex_input,
            "baroreflex_target": baroreflex_target,
            "cerebral_outflow_pressure": cerebral_outflow_pressure,
            "cerebral_perfusion_pressure": cerebral_perfusion_pressure,
            "end_tidal_co2_mmHg": inputs.end_tidal_co2_mmHg,
            "cerebral_co2_factor": cerebral_co2_factor,
            "cerebral_impairment_factor": cerebral_impairment_factor,
            "tilt_angle_deg": inputs.tilt_angle_deg,
            "upright": sin_tilt,
            "heart_rate": float(heart_rate),
            "stroke_volume": stroke_volume,
            "cardiac_output": cardiac_output,
            "cardiac_output_l_min": cardiac_output * 60.0 / 1000.0,
            "mean_arterial_pressure": pa,
            "systemic_flow": systemic_flow,
            "splanchnic_arterial_flow": splanchnic_arterial_flow,
            "lower_limb_arterial_flow": lower_limb_arterial_flow,
            "other_systemic_arterial_flow": other_systemic_arterial_flow,
            "splanchnic_venous_return": splanchnic_venous_return,
            "lower_limb_venous_return": lower_limb_venous_return,
            "other_systemic_venous_return": other_systemic_venous_return,
            "muscle_pump_flow": muscle_pump_flow,
            "venous_return": splanchnic_venous_return
            + lower_limb_venous_return
            + other_systemic_venous_return,
            "systemic_resistance_effective": parallel_resistance,
            "splanchnic_arterial_resistance_effective": splanchnic_arterial_resistance,
            "lower_limb_arterial_resistance_effective": lower_limb_arterial_resistance,
            "other_systemic_arterial_resistance_effective": other_systemic_arterial_resistance,
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
        cardiac_sym = y[_CARDIAC_SYMPATHETIC_STATE]
        vascular_sym = y[_VASCULAR_SYMPATHETIC_STATE]
        vagal = y[_VAGAL_STATE]
        load = y[_EXERTIONAL_LOAD]
        delayed = y[_DELAYED_STRESS]
        pem = y[_PEM_SEVERITY]
        cerebral = y[_CEREBRAL_FLOW_INDEX]
        inputs = self._inputs(t, protocol, p.end_tidal_co2_reference_mmHg)
        baroreflex_target = d["baroreflex_target"]
        d_cardiac_sympathetic = (
            baroreflex_target - cardiac_sym
        ) / p.cardiac_sympathetic_time_constant
        d_vascular_sympathetic = (
            baroreflex_target - vascular_sym
        ) / p.vascular_sympathetic_time_constant
        d_vagal = (1.0 - baroreflex_target - vagal) / p.vagal_time_constant

        # Volume conservation: all five volume derivatives telescope exactly.
        d_arterial = d["cardiac_output"] - d["systemic_flow"]
        d_central = d["venous_return"] - d["cardiac_output"]
        d_splanchnic = d["splanchnic_arterial_flow"] - d["splanchnic_venous_return"]
        d_lower_limb = d["lower_limb_arterial_flow"] - d["lower_limb_venous_return"]
        d_other = d["other_systemic_arterial_flow"] - d["other_systemic_venous_return"]

        # Phenomenological PEM cascade with asymmetric onset/recovery.
        load_target = inputs.exertion / d["metabolic_capacity"]
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
        derivative = np.zeros(len(STATE_NAMES), dtype=float)
        derivative[_ARTERIAL_VOLUME] = d_arterial
        derivative[_CENTRAL_VENOUS_VOLUME] = d_central
        derivative[_SPLANCHNIC_VENOUS_VOLUME] = d_splanchnic
        derivative[_LOWER_LIMB_VENOUS_VOLUME] = d_lower_limb
        derivative[_OTHER_SYSTEMIC_VENOUS_VOLUME] = d_other
        derivative[_CARDIAC_SYMPATHETIC_STATE] = d_cardiac_sympathetic
        derivative[_VASCULAR_SYMPATHETIC_STATE] = d_vascular_sympathetic
        derivative[_VAGAL_STATE] = d_vagal
        derivative[_EXERTIONAL_LOAD] = d_load
        derivative[_DELAYED_STRESS] = d_delayed
        derivative[_PEM_SEVERITY] = d_pem
        derivative[_CEREBRAL_FLOW_INDEX] = d_cerebral
        return derivative

    def _cerebral_flow_index_upper_bound(self) -> float:
        """Upper bound from the pressure asymptote times the CO2 bound."""
        p = self.parameters
        pressure_asymptote = 1.0 / (1.0 - p.cerebral_autoregulation_residual_slope)
        co2_bound = math.exp(
            p.cerebral_co2_reactivity_per_mmHg * p.cerebral_co2_extrapolation_limit_mmHg
        )
        return pressure_asymptote * co2_bound

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
        if any(b.start != a.end for a, b in zip(protocol, protocol[1:], strict=False)):
            raise ValueError("Protocol segments must be ordered, contiguous, and non-overlapping")
        if protocol[0].start != 0:
            raise ValueError("Protocol must start at t=0")
        if not math.isfinite(sample_interval) or sample_interval <= 0:
            raise ValueError("sample_interval must be positive and finite")
        if not math.isfinite(max_step) or max_step <= 0:
            raise ValueError("max_step must be positive and finite")
        if not 0 < rtol < 1 or not 0 < atol:
            raise ValueError("rtol must be in (0, 1) and atol must be positive")
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
        if np.min(solution.y[:_VOLUME_STATE_COUNT]) < -1e-6:
            raise RuntimeError("Simulation produced a negative stressed-blood-volume state")
        autonomic = solution.y[_CARDIAC_SYMPATHETIC_STATE : _VAGAL_STATE + 1]
        if np.min(autonomic) < -1e-8 or np.max(autonomic) > 1.0 + 1e-8:
            raise RuntimeError("Simulation produced an autonomic state outside [0, 1]")
        cerebral_upper_bound = self._cerebral_flow_index_upper_bound()
        cerebral = solution.y[_CEREBRAL_FLOW_INDEX]
        if np.min(cerebral) < -1e-8 or np.max(cerebral) > cerebral_upper_bound + 1e-8:
            raise RuntimeError(
                "Simulation produced a cerebral-flow index outside its declared bounds"
            )
        derived = [
            self._derived(t, y, protocol) for t, y in zip(solution.t, solution.y.T, strict=True)
        ]
        output_names = [
            "heart_rate",
            "arterial_pressure",
            "mean_arterial_pressure",
            "heart_level_mean_arterial_pressure",
            "central_venous_pressure",
            "splanchnic_venous_pressure",
            "lower_limb_venous_pressure",
            "other_systemic_venous_pressure",
            "aortic_baroreceptor_pressure",
            "carotid_sinus_pressure",
            "brain_arterial_pressure",
            "integrated_baroreflex_input",
            "baroreflex_target",
            "cerebral_outflow_pressure",
            "cerebral_perfusion_pressure",
            "end_tidal_co2_mmHg",
            "cerebral_co2_factor",
            "cerebral_impairment_factor",
            "tilt_angle_deg",
            "upright",
            "stroke_volume",
            "cardiac_output",
            "cardiac_output_l_min",
            "systemic_flow",
            "splanchnic_arterial_flow",
            "lower_limb_arterial_flow",
            "other_systemic_arterial_flow",
            "splanchnic_venous_return",
            "lower_limb_venous_return",
            "other_systemic_venous_return",
            "muscle_pump_flow",
            "venous_return",
            "systemic_resistance_effective",
            "splanchnic_arterial_resistance_effective",
            "lower_limb_arterial_resistance_effective",
            "other_systemic_arterial_resistance_effective",
            "lower_limb_venous_resistance_effective",
            "metabolic_capacity",
            "oxygen_extraction",
            "functional_capacity",
            "cerebral_pressure_target",
            "cerebral_flow_target",
        ]
        outputs = {name: np.array([d[name] for d in derived]) for name in output_names}
        outputs["cerebral_flow_index"] = solution.y[_CEREBRAL_FLOW_INDEX].copy()
        outputs["pem_severity"] = solution.y[_PEM_SEVERITY].copy()
        outputs["exertional_load"] = solution.y[_EXERTIONAL_LOAD].copy()
        outputs["delayed_stress"] = solution.y[_DELAYED_STRESS].copy()
        outputs["cardiac_sympathetic_state"] = solution.y[_CARDIAC_SYMPATHETIC_STATE].copy()
        outputs["vascular_sympathetic_state"] = solution.y[_VASCULAR_SYMPATHETIC_STATE].copy()
        outputs["vagal_state"] = solution.y[_VAGAL_STATE].copy()
        outputs["sympathetic_state"] = 0.5 * (
            solution.y[_CARDIAC_SYMPATHETIC_STATE] + solution.y[_VASCULAR_SYMPATHETIC_STATE]
        )
        outputs["arterial_volume"] = solution.y[_ARTERIAL_VOLUME].copy()
        outputs["central_venous_volume"] = solution.y[_CENTRAL_VENOUS_VOLUME].copy()
        outputs["splanchnic_venous_volume"] = solution.y[_SPLANCHNIC_VENOUS_VOLUME].copy()
        outputs["lower_limb_venous_volume"] = solution.y[_LOWER_LIMB_VENOUS_VOLUME].copy()
        outputs["other_systemic_venous_volume"] = solution.y[_OTHER_SYSTEMIC_VENOUS_VOLUME].copy()
        protocol_payload = [asdict(s) for s in protocol]
        config_hash = hashlib.sha256(
            json.dumps(
                {"parameters": asdict(self.parameters), "protocol": protocol_payload},
                sort_keys=True,
            ).encode()
        ).hexdigest()
        metadata = {
            "model": "ocpe:disease-models/shared-physiology",
            "model_version": "0.4.0",
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
