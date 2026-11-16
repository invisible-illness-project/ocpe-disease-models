"""Unit tests for the scientific traceability audit subsystem.

All tests build temporary registries under ``tmp_path``; the repository's
real registries are never touched.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocpe_disease_models.validation.traceability import (  # noqa: E402
    REGISTRY_SPECS,
    collect_metadata,
    load_registry,
    run_audit,
)
from ocpe_disease_models.validation.traceability.report import (  # noqa: E402
    render_markdown,
)
from ocpe_disease_models.validation.traceability.runner import main  # noqa: E402
from ocpe_disease_models.validation.traceability.schema_validation import (  # noqa: E402
    schema_available,
)

pytestmark = pytest.mark.scientific_traceability

SCRIPT = REPO_ROOT / "scripts" / "audit_traceability.py"
SCHEMAS_DIR = REPO_ROOT / "validation" / "traceability" / "schemas"

# Map registry name -> (relative file path, canonical top-level key).
REGISTRY_FILES = {
    "references": ("literature/references.yaml", "references"),
    "evidence": ("evidence_registry.yaml", "evidence_claims"),
    "mechanisms": ("mechanism_registry.yaml", "mechanisms"),
    "equations": ("equation_registry.yaml", "equations"),
    "parameters": ("parameter_registry.yaml", "parameters"),
    "validation_tests": ("validation/validation_registry.yaml", "validation_tests"),
    "simulations": ("simulations/simulation_registry.yaml", "simulations"),
}


def write_registry(root: Path, name: str, entries, bare_list: bool = False) -> Path:
    """Write a registry file under ``root`` and return its path."""
    rel_path, key = REGISTRY_FILES[name]
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    document = entries if bare_list else {key: entries}
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def clean_entries():
    """A fully cross-linked, zero-error registry set."""
    return {
        "references": [
            {"id": "REF-0001", "title": "A foundational study", "year": 2020},
        ],
        "evidence": [
            {
                "id": "CLM-0001",
                "statement": "Baroreflex sensitivity is reduced.",
                "references": ["REF-0001"],
            },
        ],
        "mechanisms": [
            {
                "id": "MEC-0001",
                "name": "Impaired baroreflex",
                "claims": ["CLM-0001"],
                "status": "implemented",
                "equations": ["EQ-0001"],
                "parameters": ["PAR-0001"],
            },
        ],
        "equations": [
            {
                "id": "EQ-0001",
                "expression": "dHR/dt = k * (P_set - P)",
                "assumptions": ["Linear response regime"],
                "provenance": "Derived from REF-0001",
            },
        ],
        "parameters": [
            {
                "id": "PAR-0001",
                "name": "baroreflex gain",
                "source": "REF-0001",
                "estimation_method": "literature meta-analysis",
                "provenance": "curated 2024",
            },
        ],
        "validation_tests": [
            {
                "id": "VAL-0001",
                "mechanisms": ["MEC-0001"],
                "expected_behavior": "HR rises on tilt",
                "acceptance_criteria": "HR increase within 15-40 bpm",
                "justification": "Matches clinical tilt-table data",
            },
        ],
        "simulations": [
            {
                "id": "SIM-0001",
                "config": "simulations/orthostatic/tilt.yaml",
                "model": "ocpe-disease-models@abc123",
                "mechanisms": ["MEC-0001"],
            },
        ],
    }


def write_clean_repo(root: Path) -> None:
    for name, entries in clean_entries().items():
        write_registry(root, name, entries)


def findings_by_check(result, check):
    return [f for f in result.ctx.findings if f.check == check]


def errors(result):
    return [f for f in result.ctx.findings if f.severity == "error"]


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------


def test_load_registry_documented_key(tmp_path):
    write_registry(tmp_path, "references", [{"id": "REF-0001", "title": "T"}])
    spec = next(s for s in REGISTRY_SPECS if s.name == "references")
    registry = load_registry(tmp_path, spec)
    assert registry.found
    assert registry.load_errors == []
    assert registry.ids == {"REF-0001"}


def test_load_registry_bare_list(tmp_path):
    write_registry(tmp_path, "references", [{"id": "REF-0002", "title": "T"}], bare_list=True)
    spec = next(s for s in REGISTRY_SPECS if s.name == "references")
    registry = load_registry(tmp_path, spec)
    assert registry.found
    assert registry.load_errors == []
    assert registry.ids == {"REF-0002"}


def test_load_registry_missing_is_tolerated(tmp_path):
    result = run_audit(tmp_path, deterministic=True)
    not_found = findings_by_check(result, "registry-not-found")
    assert {f.registry for f in not_found} == set(REGISTRY_FILES)
    assert all(f.severity == "info" for f in not_found)
    assert errors(result) == []


def test_load_registry_invalid_yaml(tmp_path):
    path = tmp_path / "literature"
    path.mkdir(parents=True)
    (path / "references.yaml").write_text(":\n  - [unclosed\n", encoding="utf-8")
    spec = next(s for s in REGISTRY_SPECS if s.name == "references")
    registry = load_registry(tmp_path, spec)
    assert registry.found
    assert registry.load_errors
    assert "YAML parse error" in registry.load_errors[0]


def test_load_registry_wrong_top_level_key(tmp_path):
    path = tmp_path / "literature"
    path.mkdir(parents=True)
    (path / "references.yaml").write_text(yaml.safe_dump({"wrong_key": []}), encoding="utf-8")
    spec = next(s for s in REGISTRY_SPECS if s.name == "references")
    registry = load_registry(tmp_path, spec)
    assert any("documented list keys" in e for e in registry.load_errors)


def test_load_registry_non_mapping_entry(tmp_path):
    write_registry(
        tmp_path,
        "references",
        [{"id": "REF-0001", "title": "ok"}, "not-a-mapping"],
    )
    spec = next(s for s in REGISTRY_SPECS if s.name == "references")
    registry = load_registry(tmp_path, spec)
    assert len(registry.entries) == 1
    assert any("not a mapping" in e for e in registry.load_errors)


def test_load_errors_surface_as_error_findings(tmp_path):
    path = tmp_path / "literature"
    path.mkdir(parents=True)
    (path / "references.yaml").write_text(":\n  - [unclosed\n", encoding="utf-8")
    result = run_audit(tmp_path, deterministic=True)
    assert any(f.check == "registry-load-error" for f in errors(result))


# ---------------------------------------------------------------------------
# Audit checks
# ---------------------------------------------------------------------------


def test_claim_without_references_is_error(tmp_path):
    write_registry(tmp_path, "evidence", [{"id": "CLM-0001", "statement": "X"}])
    result = run_audit(tmp_path, deterministic=True)
    found = findings_by_check(result, "claim-without-references")
    assert len(found) == 1
    assert found[0].severity == "error"
    assert found[0].entry_id == "CLM-0001"


def test_broken_cross_registry_link_is_error(tmp_path):
    write_registry(
        tmp_path,
        "evidence",
        [{"id": "CLM-0001", "statement": "X", "references": ["REF-9999"]}],
    )
    result = run_audit(tmp_path, deterministic=True)
    found = findings_by_check(result, "broken-cross-registry-link")
    assert len(found) == 1
    assert "REF-9999" in found[0].message
    assert found[0].severity == "error"


def test_mechanism_without_claims_error_unless_exploratory(tmp_path):
    write_registry(tmp_path, "mechanisms", [{"id": "MEC-0001", "name": "m"}])
    result = run_audit(tmp_path, deterministic=True)
    assert len(findings_by_check(result, "mechanism-without-claims")) == 1

    # Exploratory mechanisms are exempt (info only, no error).
    root2 = tmp_path / "exploratory"
    write_registry(
        root2,
        "mechanisms",
        [{"id": "MEC-0002", "name": "m2", "status": "exploratory"}],
    )
    result2 = run_audit(root2, deterministic=True)
    assert findings_by_check(result2, "mechanism-without-claims") == []
    info = findings_by_check(result2, "exploratory-mechanism-without-claims")
    assert len(info) == 1 and info[0].severity == "info"


def test_implemented_mechanism_without_tests_is_error(tmp_path):
    write_registry(
        tmp_path,
        "mechanisms",
        [
            {
                "id": "MEC-0001",
                "name": "m",
                "claims": [],
                "status": "implemented",
                "exploratory": True,
            }
        ],
    )
    result = run_audit(tmp_path, deterministic=True)
    found = findings_by_check(result, "implemented-mechanism-without-tests")
    assert len(found) == 1
    assert found[0].severity == "error"


def test_implemented_mechanism_with_test_passes(tmp_path):
    write_registry(
        tmp_path,
        "mechanisms",
        [
            {
                "id": "MEC-0001",
                "name": "m",
                "exploratory": True,
                "status": "implemented",
            }
        ],
    )
    write_registry(
        tmp_path,
        "validation_tests",
        [
            {
                "id": "VAL-0001",
                "mechanisms": ["MEC-0001"],
                "expected_behavior": "b",
                "acceptance_criteria": "c",
                "justification": "j",
            }
        ],
    )
    result = run_audit(tmp_path, deterministic=True)
    assert findings_by_check(result, "implemented-mechanism-without-tests") == []


def test_equation_missing_fields_are_errors(tmp_path):
    write_registry(tmp_path, "equations", [{"id": "EQ-0001"}])
    result = run_audit(tmp_path, deterministic=True)
    for check in (
        "equation-missing-expression",
        "equation-missing-assumptions",
        "equation-missing-provenance",
    ):
        assert len(findings_by_check(result, check)) == 1, check


def test_parameter_missing_fields_are_errors(tmp_path):
    write_registry(tmp_path, "parameters", [{"id": "PAR-0001"}])
    result = run_audit(tmp_path, deterministic=True)
    for check in (
        "parameter-missing-source",
        "parameter-missing-estimation-method",
        "parameter-missing-provenance",
    ):
        assert len(findings_by_check(result, check)) == 1, check


def test_validation_test_missing_fields_are_errors(tmp_path):
    write_registry(tmp_path, "validation_tests", [{"id": "VAL-0001"}])
    result = run_audit(tmp_path, deterministic=True)
    for check in (
        "test-missing-expected-behavior",
        "test-missing-acceptance-criteria",
        "test-missing-justification",
    ):
        assert len(findings_by_check(result, check)) == 1, check


def test_simulation_missing_provenance_is_error(tmp_path):
    write_registry(tmp_path, "simulations", [{"id": "SIM-0001"}])
    result = run_audit(tmp_path, deterministic=True)
    assert len(findings_by_check(result, "simulation-missing-config")) == 1
    assert len(findings_by_check(result, "simulation-missing-model-provenance")) == 1


def test_orphan_evidence_claim_is_warning(tmp_path):
    write_registry(
        tmp_path,
        "evidence",
        [{"id": "CLM-0001", "statement": "X", "references": []}],
    )
    result = run_audit(tmp_path, deterministic=True)
    found = findings_by_check(result, "orphan-evidence-claim")
    assert len(found) == 1
    assert found[0].severity == "warning"


def test_uncited_reference_is_warning(tmp_path):
    write_registry(tmp_path, "references", [{"id": "REF-0001", "title": "T"}])
    result = run_audit(tmp_path, deterministic=True)
    found = findings_by_check(result, "uncited-reference")
    assert len(found) == 1
    assert found[0].severity == "warning"


def test_unused_equation_is_warning(tmp_path):
    write_registry(
        tmp_path,
        "equations",
        [
            {
                "id": "EQ-0001",
                "expression": "x = 1",
                "assumptions": ["a"],
                "provenance": "p",
            }
        ],
    )
    result = run_audit(tmp_path, deterministic=True)
    assert len(findings_by_check(result, "unused-equation")) == 1


def test_id_prefix_mismatch_is_warning(tmp_path):
    write_registry(tmp_path, "references", [{"id": "WRONG-1", "title": "T"}])
    result = run_audit(tmp_path, deterministic=True)
    assert len(findings_by_check(result, "id-prefix-mismatch")) == 1


def test_duplicate_id_is_error(tmp_path):
    write_registry(
        tmp_path,
        "references",
        [{"id": "REF-0001", "title": "a"}, {"id": "REF-0001", "title": "b"}],
    )
    result = run_audit(tmp_path, deterministic=True)
    assert len(findings_by_check(result, "duplicate-id")) == 1


# ---------------------------------------------------------------------------
# Completeness, clean run, reports
# ---------------------------------------------------------------------------


def test_completeness_counts_and_rates(tmp_path):
    write_registry(
        tmp_path,
        "evidence",
        [
            {"id": "CLM-0001", "statement": "a", "references": ["REF-0001"]},
            {"id": "CLM-0002", "statement": "b"},
        ],
    )
    write_registry(tmp_path, "references", [{"id": "REF-0001", "title": "T"}])
    result = run_audit(tmp_path, deterministic=True)
    metric = result.report["completeness"]["evidence"]["claims_with_references"]
    assert metric == {"passed": 1, "total": 2, "rate": 0.5}


def test_clean_registries_have_no_errors(tmp_path):
    write_clean_repo(tmp_path)
    result = run_audit(tmp_path, deterministic=True)
    assert errors(result) == []
    assert result.report["summary"]["status"] == "pass"
    assert result.exit_code(strict=True) == 0


def test_report_is_deterministic(tmp_path):
    write_clean_repo(tmp_path)
    r1 = run_audit(tmp_path, deterministic=True)
    r2 = run_audit(tmp_path, deterministic=True)
    assert r1.report == r2.report
    assert r1.report["generated_at"] is None
    assert r1.report["deterministic"] is True
    assert json.dumps(r1.report) == json.dumps(r2.report)


def test_metadata_from_env(tmp_path):
    env = {
        "GIT_SHA": "abc123",
        "OCPE_COMMIT": "def456",
        "TRACEABILITY_DETERMINISTIC": "1",
    }
    meta = collect_metadata(tmp_path, env=env)
    assert meta["git_sha"] == "abc123"
    assert meta["ocpe_commit"] == "def456"
    assert meta["generated_at"] is None
    assert meta["deterministic"] is True


def test_markdown_report_renders(tmp_path):
    write_clean_repo(tmp_path)
    result = run_audit(tmp_path, deterministic=True)
    markdown = render_markdown(result.report)
    assert "# Scientific Traceability Audit Report" in markdown
    assert "## Completeness" in markdown
    assert "PASS" in markdown


# ---------------------------------------------------------------------------
# Optional JSON Schema validation
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not schema_available(), reason="jsonschema not installed")
def test_schema_validation_flags_invalid_entries(tmp_path):
    import shutil

    dest = tmp_path / "validation" / "traceability" / "schemas"
    dest.mkdir(parents=True)
    for schema in SCHEMAS_DIR.glob("*.schema.json"):
        shutil.copy(schema, dest)
    write_registry(
        tmp_path,
        "parameters",
        [
            {
                "id": "PAR-0001",
                "source": "s",
                # estimation_method intentionally wrong type
                "estimation_method": 42,
                "provenance": "p",
            }
        ],
    )
    result = run_audit(tmp_path, deterministic=True)
    found = findings_by_check(result, "schema-violation")
    assert found, "expected a schema violation finding"
    assert any(f.entry_id == "PAR-0001" for f in found)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def run_cli(root: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(root),
            "--deterministic",
            *extra,
        ],
        capture_output=True,
        text=True,
    )


def test_cli_strict_exit_nonzero_on_errors(tmp_path):
    write_registry(tmp_path, "equations", [{"id": "EQ-0001"}])
    proc = run_cli(tmp_path, "--strict")
    assert proc.returncode == 1, proc.stderr
    assert "FAIL" in proc.stdout


def test_cli_strict_exit_zero_when_clean(tmp_path):
    write_clean_repo(tmp_path)
    out_dir = tmp_path / "out"
    proc = run_cli(tmp_path, "--strict", "--out-dir", str(out_dir))
    assert proc.returncode == 0, proc.stderr
    assert "PASS" in proc.stdout
    report = json.loads((out_dir / "traceability_report.json").read_text())
    assert report["summary"]["status"] == "pass"
    assert report["generated_at"] is None
    markdown = (out_dir / "traceability_report.md").read_text()
    assert "Traceability Audit" in markdown


def test_cli_non_strict_exit_zero_despite_errors(tmp_path):
    write_registry(tmp_path, "equations", [{"id": "EQ-0001"}])
    proc = run_cli(tmp_path)
    assert proc.returncode == 0, proc.stderr
    # Default output directory was used.
    assert (
        tmp_path / "validation" / "traceability" / "audit" / "traceability_report.json"
    ).is_file()


def test_cli_bad_root_is_usage_error(tmp_path):
    proc = run_cli(tmp_path / "does-not-exist")
    assert proc.returncode == 2


def test_main_in_process(tmp_path, capsys):
    write_clean_repo(tmp_path)
    code = main(
        [
            "--root",
            str(tmp_path),
            "--strict",
            "--deterministic",
            "--out-dir",
            str(tmp_path / "o"),
        ]
    )
    assert code == 0
    assert "PASS" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# VAL-TRACEABILITY: strict audit of the real repository registries
# ---------------------------------------------------------------------------
# Layer: scientific_traceability (pytest marker ``software`` per pyproject).
# Acceptance: strict schema and cross-registry audit has zero errors and zero
# warnings; all seven registries are present; all simulations have
# configuration and model provenance.


@pytest.mark.software
def test_real_repository_audit_has_zero_errors_and_warnings():
    from ocpe_disease_models.validation.traceability import run_audit

    result = run_audit(REPO_ROOT, deterministic=True)
    findings = result.ctx.findings
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    assert errors == [], f"audit errors: {[f.message for f in errors]}"
    assert warnings == [], f"audit warnings: {[f.message for f in warnings]}"
    assert result.report["summary"]["status"] == "pass"


@pytest.mark.software
def test_all_seven_registries_present_in_real_repository():
    from ocpe_disease_models.validation.traceability import (
        load_all_registries,
    )

    registries = load_all_registries(REPO_ROOT)
    assert len(registries) == 7
    for registry in registries.values():
        assert registry.found, f"registry {registry.spec.name} missing"
        assert registry.load_errors == []
        assert registry.ids, f"registry {registry.spec.name} is empty"


@pytest.mark.software
def test_all_simulations_have_configuration_and_model_provenance():
    registry_path = REPO_ROOT / "simulations" / "simulation_registry.yaml"
    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    assert raw["simulations"]
    for simulation in raw["simulations"]:
        assert simulation.get("config"), f"{simulation['id']} lacks config provenance"
        model = simulation.get("model") or {}
        assert model.get("id"), f"{simulation['id']} lacks model id"
        assert model.get("implementation"), f"{simulation['id']} lacks model implementation"
        assert model.get("ocpe_commit"), f"{simulation['id']} lacks OCPE commit"
        assert simulation.get("mechanisms"), f"{simulation['id']} lacks mechanisms"
        assert simulation.get("validation"), f"{simulation['id']} lacks validation links"


@pytest.mark.software
def test_registry_validation_test_ids_resolve_to_validation_registry():
    """Every validation id used by simulations exists in the validation registry."""
    validation = yaml.safe_load(
        (REPO_ROOT / "validation" / "validation_registry.yaml").read_text()
    )
    valid_ids = {entry["id"] for entry in validation["validation_tests"]}
    simulations = yaml.safe_load(
        (REPO_ROOT / "simulations" / "simulation_registry.yaml").read_text()
    )
    for simulation in simulations["simulations"]:
        missing = set(simulation["validation"]) - valid_ids
        assert not missing, f"{simulation['id']} references unknown validations {missing}"


@pytest.mark.scientific_traceability
def test_every_implemented_mechanism_has_a_complete_scientific_chain():
    """Implemented mechanisms must link claims, equations, parameters, code, and tests."""
    mechanisms = yaml.safe_load(
        (REPO_ROOT / "literature" / "mechanism_registry.yaml").read_text()
    )["mechanisms"]
    for mechanism in mechanisms:
        if mechanism.get("status") != "implemented":
            continue
        assert mechanism.get("claims"), f"{mechanism['id']} lacks evidence claims"
        assert mechanism.get("equations"), f"{mechanism['id']} lacks equation links"
        assert mechanism.get("parameters"), f"{mechanism['id']} lacks parameter links"
        assert mechanism.get("implementation"), f"{mechanism['id']} lacks an implementation path"
        assert mechanism.get("tests"), f"{mechanism['id']} lacks validation links"


@pytest.mark.scientific_traceability
def test_mechanism_validation_records_expose_claim_equation_and_parameter_links():
    """Validation is the terminal executable link in the scientific chain."""
    records = yaml.safe_load(
        (REPO_ROOT / "validation" / "validation_registry.yaml").read_text()
    )["validation_tests"]
    for record in records:
        if not record.get("mechanisms"):
            continue
        assert record.get("evidence_claims"), f"{record['id']} lacks evidence links"
        if record["id"] != "VAL-SCOPE-FUTURE":
            assert record.get("equation_ids"), f"{record['id']} lacks equation links"
            assert record.get("parameter_ids"), f"{record['id']} lacks parameter links"
