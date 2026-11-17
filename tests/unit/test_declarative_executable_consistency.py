"""Consistency checks between the declarative OCPE model and the executable.

The declarative model in ``ocpe/packages/disease-models/models.yaml`` carries
per-symbol ``x-executable-state`` / ``x-executable-parameter`` /
``x-executable-input`` / ``x-executable-output`` bindings. These tests verify
that the bindings are exact, bijective and numerically faithful to the
executable reference implementation
(``ocpe_disease_models.models.shared.model``), so the declarative and
executable forms cannot silently drift apart.
"""
# ruff: noqa: E402  (sys.path bootstrap for the src layout precedes imports)

import sys
from dataclasses import asdict, fields
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocpe_disease_models.interfaces.observation_mapping.mapping import (  # noqa: E402
    QUANTITY_SPECS,
    SIMULATOR_OUTPUT_ALIASES,
)
from ocpe_disease_models.interfaces.ocpe_adapter import MODEL_CURIE, load_adapter  # noqa: E402
from ocpe_disease_models.models.shared.model import (  # noqa: E402
    STATE_NAMES,
    ComputationalPatient,
    ModelParameters,
    ProtocolSegment,
)

pytestmark = pytest.mark.software

# Dynamic states that are declared with role "output" (not "state") because
# they are also exchanged quantities with registered OCPE semantics.
OUTPUT_ROLE_STATES = {"pem_severity", "cerebral_flow_index"}

PROTOCOL_INPUT_FIELDS = {
    "upright",
    "tilt_angle_deg",
    "end_tidal_co2_mmHg",
    "transition_duration",
    "exertion",
    "rhythmic_muscle_activity",
    "sustained_muscle_contraction",
}

# Inputs whose physical domain is exactly enforced by ProtocolSegment.validate.
EXACT_INPUT_RANGES = {
    "upright": (0.0, 1.0),
    "tilt_angle_deg": (0.0, 90.0),
    "exertion": (0.0, 1.0),
    "rhythmic_muscle_activity": (0.0, 1.0),
    "sustained_muscle_contraction": (0.0, 1.0),
}


@pytest.fixture(scope="module")
def adapter():
    return load_adapter()


@pytest.fixture(scope="module")
def symbols(adapter):
    return adapter.model(MODEL_CURIE).data["symbols"]


@pytest.fixture(scope="module")
def equations(adapter):
    return adapter.model(MODEL_CURIE).data["equations"]


def _bound(symbols, key):
    """Map of executable name -> symbol declaration for one binding kind."""
    out = {}
    for s in symbols:
        name = s.get(key)
        if name is not None:
            assert name not in out, f"duplicate {key} binding {name!r}"
            out[name] = s
    return out


# ----------------------------------------------------------------- parameters
def test_every_executable_parameter_declared_with_matching_nominal(symbols):
    declared = _bound(symbols, "x-executable-parameter")
    defaults = asdict(ModelParameters())
    # Exact bijection: no undeclared field, no dangling binding.
    assert set(declared) == set(defaults)
    for name, sym in declared.items():
        assert sym["role"] == "parameter", f"{name}: bound symbol {sym['symbol']!r} is not a parameter"
        assert "nominal_value" in sym, f"{name}: no nominal_value declared"
        assert sym["nominal_value"] == defaults[name], (
            f"{name}: declared nominal {sym['nominal_value']!r} != executable default {defaults[name]!r}"
        )


def test_declared_parameter_ranges_cover_executable_defaults(symbols):
    defaults = asdict(ModelParameters())
    declared = _bound(symbols, "x-executable-parameter")
    for name, sym in declared.items():
        rng = sym.get("value_range") or {}
        value = defaults[name]
        if "min" in rng:
            assert rng["min"] <= value, f"{name}: default {value} below declared min {rng['min']}"
        if "max" in rng:
            assert value <= rng["max"], f"{name}: default {value} above declared max {rng['max']}"


def test_executable_accepts_declared_nominal_values():
    # The executable's own parameter validation must accept a patient built
    # from exactly the declared nominal values.
    declared_defaults = asdict(ModelParameters())
    patient = ComputationalPatient(ModelParameters.from_mapping(declared_defaults))
    assert patient.parameters == ModelParameters()


# --------------------------------------------------------------------- states
def test_every_executable_state_declared(symbols, equations):
    declared = _bound(symbols, "x-executable-state")
    assert set(declared) == set(STATE_NAMES)
    assert len(STATE_NAMES) == 12
    for name, sym in declared.items():
        expected_role = "output" if name in OUTPUT_ROLE_STATES else "state"
        assert sym["role"] == expected_role, (
            f"{name}: bound symbol {sym['symbol']!r} has role {sym['role']!r}, expected {expected_role!r}"
        )
    # One differential equation per dynamic state, nothing else integrated.
    differential = [eq for eq in equations if eq.get("form") == "differential"]
    diff_outputs = [out for eq in differential for out in eq["outputs"]]
    state_symbols = {declared[name]["symbol"] for name in STATE_NAMES}
    assert len(differential) == len(STATE_NAMES)
    assert set(diff_outputs) == state_symbols


def test_state_nominals_match_executable_initial_state(symbols):
    declared = _bound(symbols, "x-executable-state")
    y0 = ComputationalPatient().initial_state()
    for index, name in enumerate(STATE_NAMES):
        nominal = declared[name].get("nominal_value")
        assert nominal is not None, f"{name}: no nominal_value declared"
        assert nominal == pytest.approx(float(y0[index]), rel=1e-9), (
            f"{name}: declared nominal {nominal} != executable initial state {y0[index]}"
        )


# --------------------------------------------------------------------- inputs
def test_protocol_inputs_declared(symbols):
    declared = _bound(symbols, "x-executable-input")
    assert set(declared) == PROTOCOL_INPUT_FIELDS
    segment_fields = {f.name for f in fields(ProtocolSegment)}
    assert PROTOCOL_INPUT_FIELDS <= segment_fields
    for name, sym in declared.items():
        assert sym["role"] == "input"
        rng = sym.get("value_range") or {}
        if name in EXACT_INPUT_RANGES:
            # The declared range must equal the exact executable domain.
            lo, hi = EXACT_INPUT_RANGES[name]
            assert rng.get("min") == lo and rng.get("max") == hi, (
                f"{name}: declared range {rng} != executable domain [{lo}, {hi}]"
            )
        elif name == "transition_duration":
            # Nonnegative; bounded above only by the enclosing segment duration.
            assert rng.get("min") == 0.0
            assert rng.get("max") is None
        elif name == "end_tidal_co2_mmHg":
            # The executable domain is (0, inf) with no finite bound, so the
            # declared range must be finite and strictly inside it.
            assert rng.get("min") is not None and rng["min"] > 0.0
            assert rng.get("max") is not None and np.isfinite(rng["max"])
            assert rng["min"] < rng["max"]
        else:  # pragma: no cover - guarded by the PROTOCOL_INPUT_FIELDS check
            raise AssertionError(f"unhandled declared input {name!r}")


# -------------------------------------------------------------------- outputs
def test_mapped_quantities_match_declared_outputs(symbols):
    """Every observation-mapping entry resolves to a declared output symbol
    whose ``represents`` and ``unit`` agree with the mapping."""
    by_symbol = {s["symbol"]: s for s in symbols}
    for spec in QUANTITY_SPECS.values():
        sym = by_symbol.get(spec.symbol)
        assert sym is not None, f"mapping symbol {spec.symbol!r} not declared"
        assert sym["role"] == "output"
        assert sym.get("represents") == spec.curie
        assert sym.get("unit") == spec.unit
    for alias, canonical in SIMULATOR_OUTPUT_ALIASES.items():
        assert canonical in QUANTITY_SPECS, f"dangling alias {alias!r} -> {canonical!r}"


def test_declared_output_bindings_exist_in_simulation(symbols):
    """Every symbol bound to an executable output is actually produced by a
    real (short, deterministic) simulation run."""
    declared = _bound(symbols, "x-executable-output")
    patient = ComputationalPatient()
    result = patient.simulate([ProtocolSegment(start=0.0, end=10.0)])
    missing = set(declared) - set(result.outputs)
    assert not missing, f"bound outputs not produced by the executable: {sorted(missing)}"
    for name in declared:
        assert np.all(np.isfinite(result.outputs[name])), f"output {name!r} not finite"


def test_declared_nominals_reproduce_executable_operating_point(symbols):
    """The declared nominal operating point matches the executable's resting
    initial condition numerically (not just structurally)."""
    declared_params = _bound(symbols, "x-executable-parameter")
    nominal = {name: s["nominal_value"] for name, s in declared_params.items()}
    patient = ComputationalPatient()
    y0 = patient.initial_state()
    derived = patient._derived(0.0, y0, [ProtocolSegment(start=0.0, end=10.0)])
    # Resting heart rate equals the declared resting heart rate.
    assert derived["heart_rate"] == pytest.approx(nominal["heart_rate_rest"])
    # Arterial pressure follows the declared linear compartment law.
    assert derived["arterial_pressure"] == pytest.approx(
        nominal["arterial_volume_initial"] / nominal["arterial_compliance"]
    )
    # Cerebral flow index starts at its declared normalized nominal.
    assert y0[STATE_NAMES.index("cerebral_flow_index")] == pytest.approx(1.0)
    # Metabolic capacity starts at the declared baseline.
    assert derived["metabolic_capacity"] == pytest.approx(nominal["baseline_metabolic_capacity"])
