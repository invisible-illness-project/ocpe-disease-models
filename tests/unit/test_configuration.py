"""VAL-SW-CONFIG: configuration and phenotype composition (layer: software).

Registry expectations:
- YAML configurations load deterministically.
- Unknown parameters, invalid protocols, and conflicting comorbidity overrides
  fail explicitly.
- All healthy and disease configurations round-trip without silent changes.
- Conflicting parameter values raise ValueError.
- Mixed non-conflicting mechanisms compose deterministically.
"""

from __future__ import annotations

from dataclasses import asdict

import pytest
import yaml

from ocpe_disease_models.config import (
    compose_phenotypes,
    load_phenotype,
    load_protocol,
    repository_root,
)
from ocpe_disease_models.models.shared import ModelParameters

pytestmark = pytest.mark.software

ALL_PHENOTYPE_IDS = (
    "healthy-reference",
    "pots-neuropathic",
    "pots-hyperadrenergic",
    "pots-hypovolemic",
    "pots-mixed",
    "eds-heds-vascular",
    "eds-heds-mecfs-comorbid",
    "mecfs-pem",
    "long-covid-autonomic",
    "long-covid-exertional",
)

ALL_PROTOCOL_IDS = (
    "resting-baseline",
    "head-up-tilt",
    "tilt-recovery",
    "single-exertion-recovery",
    "repeated-exertion-recovery",
)


# --------------------------------------------------------------------- loading
@pytest.mark.parametrize("phenotype_id", ALL_PHENOTYPE_IDS)
def test_phenotype_loads_deterministically(phenotype_id):
    first = load_phenotype(phenotype_id)
    second = load_phenotype(phenotype_id)
    assert first == second  # frozen dataclass equality: identical every load
    assert first.phenotype_id == phenotype_id
    assert first.source_path.endswith(f"{phenotype_id}.yaml")


@pytest.mark.parametrize("protocol_id", ALL_PROTOCOL_IDS)
def test_protocol_loads_deterministically(protocol_id):
    segments_a, settings_a = load_protocol(protocol_id)
    segments_b, settings_b = load_protocol(protocol_id)
    assert segments_a == segments_b
    assert settings_a == settings_b
    assert segments_a[0].start == 0.0
    for segment in segments_a:
        segment.validate()  # configured protocols must be valid
    assert settings_a["protocol_id"] == protocol_id


# ----------------------------------------------------------------- round-trip
@pytest.mark.parametrize("phenotype_id", ALL_PHENOTYPE_IDS)
def test_phenotype_round_trips_without_silent_changes(phenotype_id):
    """Loading and composing must reproduce exactly the declared overrides."""
    root = repository_root()
    phenotype = load_phenotype(phenotype_id, root)
    raw_path = root / phenotype.source_path
    raw = yaml.safe_load(raw_path.read_text(encoding="utf-8"))
    # The loaded phenotype matches the on-disk YAML exactly (no silent mutation).
    assert dict(phenotype.parameter_overrides) == dict(raw["parameter_overrides"])
    assert tuple(phenotype.mechanisms) == tuple(raw["mechanisms"])
    # Composition applies exactly the declared overrides onto the defaults.
    patient = compose_phenotypes([phenotype_id])
    defaults = asdict(ModelParameters())
    for name, default_value in defaults.items():
        expected = phenotype.parameter_overrides.get(name, default_value)
        assert getattr(patient.parameters, name) == expected, (
            f"{phenotype_id}: parameter {name} silently changed "
            f"(expected {expected}, got {getattr(patient.parameters, name)})"
        )
    # Serializing the composed parameters is stable.
    assert asdict(patient.parameters) == asdict(patient.parameters.replaced({}))


# --------------------------------------------------------------- failure modes
def test_unknown_parameter_fails_explicitly():
    with pytest.raises(ValueError, match="Unknown model parameters"):
        ModelParameters.from_mapping({"not_a_parameter": 1.0})


def test_unknown_parameter_in_replacement_fails_explicitly():
    with pytest.raises(ValueError, match="Unknown model parameters"):
        ModelParameters().replaced({"heart_rate_base": 55.0, "bogus": 2.0})


def test_unknown_phenotype_fails_explicitly():
    with pytest.raises(ValueError, match="Expected one phenotype"):
        load_phenotype("no-such-phenotype")


def test_unknown_protocol_fails_explicitly():
    with pytest.raises(ValueError, match="Expected one protocol"):
        load_protocol("no-such-protocol")


def test_empty_composition_fails_explicitly():
    with pytest.raises(ValueError, match="At least one phenotype"):
        compose_phenotypes([])


# ------------------------------------------------------------------ composition
def test_conflicting_comorbidity_overrides_raise_value_error():
    """pots-hyperadrenergic and pots-hypovolemic disagree on shared parameters;
    ad hoc composition must fail rather than silently pick an order."""
    with pytest.raises(ValueError, match="Parameter conflict"):
        compose_phenotypes(["pots-hyperadrenergic", "pots-hypovolemic"])


def test_conflict_detection_is_order_independent():
    with pytest.raises(ValueError, match="Parameter conflict"):
        compose_phenotypes(["pots-hypovolemic", "pots-hyperadrenergic"])


def test_non_conflicting_mechanisms_compose_deterministically():
    """Disjoint mechanism sets compose; repeated composition is identical."""
    ids = ["eds-heds-vascular", "long-covid-exertional"]
    first = compose_phenotypes(ids)
    second = compose_phenotypes(list(reversed(ids)))
    third = compose_phenotypes(ids)
    assert asdict(first.parameters) == asdict(third.parameters)
    # Order of non-conflicting composition must not change any value.
    assert asdict(first.parameters) == asdict(second.parameters)
    # Provenance records the contributing phenotypes and mechanisms explicitly.
    assert set(first.provenance["phenotypes"]) == {
        "phenotypes/eds/eds-heds-vascular.yaml",
        "phenotypes/long_covid/long-covid-exertional.yaml",
    }
    assert "MEC-VASC-COMPLIANCE" in first.provenance["mechanisms"]
    assert "MEC-MET-EXTRACTION" in first.provenance["mechanisms"]


def test_named_comorbidity_configuration_resolves_joint_choice():
    """The curated comorbidity YAML is the explicit joint configuration that
    ad hoc composition of its parents refuses to guess at."""
    patient = compose_phenotypes(["eds-heds-mecfs-comorbid"])
    phenotype = load_phenotype("eds-heds-mecfs-comorbid")
    assert set(patient.provenance["phenotypes"]) == {phenotype.source_path}
    assert patient.parameters.oxygen_extraction_fraction == pytest.approx(0.74)
    assert phenotype.classification == "exploratory_comorbidity"


def test_mixed_pots_has_explicit_mechanism_provenance():
    patient = compose_phenotypes(["pots-mixed"])
    expected = {
        "MEC-VOL-HYPOVOLEMIA",
        "MEC-VASC-POOLING",
        "MEC-VASC-CONSTRICTION",
        "MEC-AUT-HYPERADRENERGIC",
    }
    assert expected <= set(patient.provenance["mechanisms"])
    assert patient.provenance["phenotypes"] == ["phenotypes/pots/pots-mixed.yaml"]
