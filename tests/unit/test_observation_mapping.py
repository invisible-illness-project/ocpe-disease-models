"""Unit tests for the simulated-output -> OCPE observation mapping."""
# ruff: noqa: E402  (sys.path bootstrap for the src layout precedes imports)

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import ocpe  # noqa: E402
from ocpe_disease_models.interfaces.observation_mapping import (  # noqa: E402
    MODEL_CURIE,
    QUANTITY_SPECS,
    SIMULATED_VALUE_KIND,
    SIMULATOR_OUTPUT_ALIASES,
    OCPEObservationError,
    build_observation,
    get_spec,
    map_simulation_outputs,
    validate_observation_record,
)
from ocpe_disease_models.interfaces.observation_mapping.mapping import (  # noqa: E402
    SIMULATION_PROVENANCE,
)
from ocpe_disease_models.interfaces.ocpe_adapter import UPSTREAM_COMMIT  # noqa: E402

pytestmark = pytest.mark.software

EXPECTED_NAMES = {
    "heart_rate",
    "mean_arterial_pressure",
    "stroke_volume",
    "cardiac_output",
    "cerebral_flow_index",
    "metabolic_capacity",
    "pem_severity",
}

EXPECTED_UNITS = {
    "heart_rate": "/min",
    "mean_arterial_pressure": "mm[Hg]",
    "stroke_volume": "mL",
    "cardiac_output": "L/min",
    "cerebral_flow_index": "1",
    "metabolic_capacity": "1",
    "pem_severity": "1",
}

NOMINAL_OUTPUTS = {
    "heart_rate": 66.0,
    "mean_arterial_pressure": 90.0,
    "stroke_volume": 63.6,
    "cardiac_output": 4.2,
    "cerebral_flow_index": 0.94,
    "metabolic_capacity": 0.9,
    "pem_severity": 0.0,
}


# ----------------------------------------------------------------- structure
def test_mapping_covers_all_seven_simulated_quantities():
    assert set(QUANTITY_SPECS) == EXPECTED_NAMES
    for name, spec in QUANTITY_SPECS.items():
        assert spec.name == name
        assert spec.curie.startswith("ocpe:disease-models/")
        assert spec.unit == EXPECTED_UNITS[name]
        assert spec.symbol


def test_get_spec_unknown_name_raises():
    with pytest.raises(KeyError):
        get_spec("blood_pressure")


# ------------------------------------------------------- simulator aliases
def test_simulator_aliases_target_registered_specs_with_compatible_units():
    # Aliases adapt simulator-native output names to mapping entries; the
    # aliased unit must already match the entry's explicit UCUM unit (no
    # conversion is performed).
    for alias, canonical in SIMULATOR_OUTPUT_ALIASES.items():
        assert canonical in QUANTITY_SPECS
        assert alias != canonical
    assert SIMULATOR_OUTPUT_ALIASES["cardiac_output_l_min"] == "cardiac_output"
    assert QUANTITY_SPECS["cardiac_output"].unit == "L/min"


def test_get_spec_resolves_cardiac_output_l_min_alias():
    spec = get_spec("cardiac_output_l_min")
    assert spec is QUANTITY_SPECS["cardiac_output"]
    assert spec.curie == "ocpe:disease-models/cardiac-output"


def test_build_observation_via_alias_uses_canonical_quantity_and_unit():
    record = build_observation("cardiac_output_l_min", 5.1)
    assert record["quantity"] == "ocpe:disease-models/cardiac-output"
    assert record["unit"] == "L/min"
    validate_observation_record(record)


def test_map_simulation_outputs_accepts_simulator_native_keys():
    outputs = dict(NOMINAL_OUTPUTS)
    outputs["cardiac_output_l_min"] = outputs.pop("cardiac_output")
    records = map_simulation_outputs(outputs)
    assert set(records) == set(outputs)  # keyed by the simulator-native names
    co = records["cardiac_output_l_min"]
    assert co["quantity"] == "ocpe:disease-models/cardiac-output"
    assert co["unit"] == "L/min"
    assert co["value"] == 4.2
    validate_observation_record(co)


# ------------------------------------------------------------------- records
def test_build_observation_semantics():
    record = build_observation("heart_rate", 72.0)
    assert record["quantity"] == "ocpe:disease-models/heart-rate"
    assert record["value"] == 72.0
    assert record["unit"] == "/min"  # explicit UCUM unit
    assert record["value_kind"] == SIMULATED_VALUE_KIND == "simulated"
    assert record["model"] == MODEL_CURIE
    # provenance present and tied to the pinned upstream commit
    assert record["provenance"]["derived_from"][0]["legacy_id"] == MODEL_CURIE
    assert UPSTREAM_COMMIT in record["provenance"]["derived_from"][0]["transformation"]
    assert "not a physiological measurement" in record["provenance"]["notes"]


def test_build_observation_optional_fields():
    record = build_observation(
        "cardiac_output",
        5.1,
        time="2026-01-01T00:00:00Z",
        uncertainty=0.2,
        uncertainty_type="sd",
        subject="sim-001",
        observation_id="obs-1",
    )
    assert record["time"] == "2026-01-01T00:00:00Z"
    assert record["uncertainty"] == 0.2
    assert record["uncertainty_type"] == "sd"
    assert record["subject"] == "sim-001"
    assert record["observation_id"] == "obs-1"
    validate_observation_record(record)


def test_build_observation_unknown_quantity_raises():
    with pytest.raises(KeyError):
        build_observation("nope", 1.0)


# ----------------------------------------------------------------- validation
def test_all_mapped_records_validate_with_ocpe():
    records = map_simulation_outputs(NOMINAL_OUTPUTS)
    assert set(records) == EXPECTED_NAMES
    for record in records.values():
        validate_observation_record(record)  # raises on any issue


def test_map_simulation_outputs_schema_validates_against_engine():
    records = map_simulation_outputs(NOMINAL_OUTPUTS)
    for record in records.values():
        # Schema-level validation directly through the engine, without registry.
        assert ocpe.validate_observation(record).ok


def test_unknown_output_key_raises():
    with pytest.raises(KeyError):
        map_simulation_outputs({"heart_rate": 70.0, "mystery": 1.0})


def test_validate_rejects_wrong_unit():
    record = build_observation("heart_rate", 72.0)
    record["unit"] = "mm[Hg]"  # pressure unit on an event-rate quantity
    with pytest.raises(OCPEObservationError):
        validate_observation_record(record)


def test_validate_rejects_non_numeric_value():
    record = build_observation("heart_rate", "fast")
    with pytest.raises(OCPEObservationError):
        validate_observation_record(record)


def test_validate_rejects_missing_model_for_simulated():
    record = build_observation("stroke_volume", 65.0)
    del record["model"]
    with pytest.raises(OCPEObservationError):
        validate_observation_record(record)


def test_validate_rejects_measured_value_kind_for_latent_construct():
    record = build_observation("metabolic_capacity", 0.8)
    record["value_kind"] = "measured"
    del record["model"]
    with pytest.raises(OCPEObservationError):
        validate_observation_record(record)


def test_provenance_is_copied_not_shared():
    r1 = build_observation("heart_rate", 70.0)
    r2 = build_observation("heart_rate", 71.0)
    r1["provenance"]["notes"] = "mutated"
    assert r2["provenance"]["notes"] == SIMULATION_PROVENANCE["notes"]
