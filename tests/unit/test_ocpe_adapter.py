"""Unit tests for the OCPE adapter interface (interfaces.ocpe_adapter)."""
# ruff: noqa: E402  (sys.path bootstrap for the src layout precedes imports)

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import ocpe  # noqa: E402
from ocpe_disease_models.interfaces.ocpe_adapter import (  # noqa: E402
    MODEL_CURIE,
    PACKAGE_ID,
    PACKAGE_VERSION,
    DiseaseModelsOCPEAdapter,
    OCPERegistryError,
    default_package_dir,
    load_adapter,
)
from ocpe_disease_models.interfaces.ocpe_adapter.adapter import (  # noqa: E402
    UPSTREAM_COMMIT,
    UPSTREAM_REPOSITORY,
)

pytestmark = pytest.mark.software

PINNED_COMMIT = "3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d"
UPSTREAM_CHECKOUT = Path("/mnt/agents/output/open-computational-physiology-engine")

EXPECTED_QUANTITIES = {
    "ocpe:disease-models/heart-rate",
    "ocpe:disease-models/mean-arterial-pressure",
    "ocpe:disease-models/stroke-volume",
    "ocpe:disease-models/cardiac-output",
    "ocpe:disease-models/cerebral-flow-index",
    "ocpe:disease-models/metabolic-capacity",
    "ocpe:disease-models/pem-severity",
}

# The declarative model also exposes the mean sympathetic state as an output.
EXPECTED_OUTPUT_QUANTITIES = EXPECTED_QUANTITIES | {
    "ocpe:disease-models/sympathetic-activation",
}

# Role-"state" symbols of the 12-state executable model; the remaining two
# dynamic states (PEM severity, cerebral flow index) are declared with role
# "output" because they are also exchanged quantities.
EXPECTED_STATE_SYMBOLS = {
    "V_a",
    "V_cv",
    "V_sv",
    "V_lv",
    "V_ov",
    "S_c",
    "S_v",
    "S_vag",
    "L_ex",
    "D",
}


# --------------------------------------------------------------------- pins
def test_upstream_commit_is_pinned_full_sha():
    assert UPSTREAM_COMMIT == PINNED_COMMIT
    assert re.fullmatch(r"[0-9a-f]{40}", UPSTREAM_COMMIT)


@pytest.mark.skipif(
    not (UPSTREAM_CHECKOUT / ".git").exists(), reason="upstream checkout not available"
)
def test_upstream_commit_matches_checkout():
    out = subprocess.run(
        ["git", "-C", str(UPSTREAM_CHECKOUT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert UPSTREAM_COMMIT == out


def test_pyproject_dependency_pin_matches():
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f"{UPSTREAM_REPOSITORY}.git@{UPSTREAM_COMMIT}" in pyproject


# ------------------------------------------------------------------ loading
def test_default_package_dir_exists_and_matches_scope():
    d = default_package_dir()
    assert (d / "package.yaml").is_file()
    assert d == REPO_ROOT / "ocpe" / "packages" / PACKAGE_ID


def test_adapter_loads_and_validates_strictly():
    adapter = load_adapter()
    assert isinstance(adapter, DiseaseModelsOCPEAdapter)
    assert adapter.report.ok
    assert adapter.report.warnings == []
    assert adapter.package.id == PACKAGE_ID


def test_engine_is_ocpe_01():
    assert ocpe.__version__.startswith("0.1")
    assert ocpe.spec_version().startswith("0.1")


def test_missing_package_dir_raises():
    with pytest.raises(OCPERegistryError):
        load_adapter(REPO_ROOT / "ocpe" / "packages" / "does-not-exist")


def test_invalid_package_raises_with_report(tmp_path):
    bad = tmp_path / PACKAGE_ID
    bad.mkdir()
    (bad / "package.yaml").write_text(
        "id: disease-models\nname: bad\nversion: 0.1.0\n"
        "ocpe_spec: '>=0.1.0 <0.2.0'\ndescription: bad fixture\n"
        "contents: [entities.yaml]\n",
        encoding="utf-8",
    )
    (bad / "entities.yaml").write_text(
        "ocpe: '0.1'\npackage: disease-models\n"
        "entities:\n"
        "  - id: ocpe:disease-models/bogus\n"
        "    kind: variable\n"
        "    label: Bogus\n"
        "    dimension: pressure\n"
        "    canonical_unit: furlong\n",
        encoding="utf-8",
    )
    with pytest.raises(OCPERegistryError) as excinfo:
        load_adapter(bad)
    assert excinfo.value.report is not None
    assert not excinfo.value.report.ok


# ----------------------------------------------------------------- registry
def test_all_seven_simulated_quantities_registered():
    adapter = load_adapter()
    registered = {e.id for e in adapter.quantities()}
    assert EXPECTED_QUANTITIES <= registered
    cfi = adapter.get("ocpe:disease-models/cerebral-flow-index")
    assert cfi.data["derived_from"] == ["ocpe:disease-models/cerebral-perfusion-pressure"]
    assert "g_{cvr}" not in cfi.data["computation"]["formula"]


def test_model_structure():
    adapter = load_adapter()
    model = adapter.model(MODEL_CURIE)
    assert model.data["formalism"] == "ode"
    states = {s["symbol"] for s in model.data["symbols"] if s["role"] == "state"}
    assert states == EXPECTED_STATE_SYMBOLS
    outputs = adapter.output_quantities()
    assert {"HR", "MAP", "SV", "CO", "CFI", "MC", "PEM", "S_sym"} <= set(outputs)
    # Every model output accounts for a registered quantity.
    assert set(outputs.values()) <= EXPECTED_OUTPUT_QUANTITIES
    # One differential equation per dynamic state of the executable model:
    # the ten role-"state" symbols plus PEM and CFI (role "output").
    differential = [eq for eq in model.data["equations"] if eq.get("form") == "differential"]
    diff_outputs = {out for eq in differential for out in eq["outputs"]}
    assert diff_outputs == EXPECTED_STATE_SYMBOLS | {"PEM", "CFI"}
    # Equations carry formal LaTeX expressions.
    assert model.data["equations"]
    for eq in model.data["equations"]:
        assert eq["expression_latex"]


def test_get_unknown_curie_raises():
    adapter = load_adapter()
    with pytest.raises(KeyError):
        adapter.get("ocpe:disease-models/no-such-entity")


def test_summary_reports_pin_and_package():
    adapter = load_adapter()
    summary = adapter.summary()
    assert summary["upstream_commit"] == UPSTREAM_COMMIT
    assert summary["packages"][PACKAGE_ID] == PACKAGE_VERSION
    assert "core" in summary["packages"]


def test_assert_observation_valid_roundtrip():
    adapter = load_adapter()
    record = {
        "quantity": "ocpe:disease-models/heart-rate",
        "value": 72.0,
        "unit": "/min",
        "value_kind": "simulated",
        "model": MODEL_CURIE,
    }
    report = adapter.assert_observation_valid(record)
    assert report.ok


def test_assert_observation_rejects_wrong_dimension():
    adapter = load_adapter()
    record = {
        "quantity": "ocpe:disease-models/heart-rate",
        "value": 72.0,
        "unit": "mL",
        "value_kind": "simulated",
        "model": MODEL_CURIE,
    }
    with pytest.raises(OCPERegistryError):
        adapter.assert_observation_valid(record)


def test_assert_observation_rejects_unaccounted_simulated_quantity():
    adapter = load_adapter()
    # mecfs is a concept, not a quantity, and no model output represents it.
    record = {
        "quantity": "ocpe:disease-models/mecfs",
        "value": 1.0,
        "unit": "1",
        "value_kind": "simulated",
        "model": MODEL_CURIE,
    }
    with pytest.raises(OCPERegistryError):
        adapter.assert_observation_valid(record)
