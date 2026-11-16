"""Audit checks for the scientific traceability subsystem.

The audit consumes the loaded registries and produces :class:`Finding`
objects plus per-registry completeness metrics.

Documented field conventions (checked flexibly -- the first present alias
wins):

* evidence claims (``CLM-``): references via ``references`` |
  ``reference_ids`` | ``citations``.
* mechanisms (``MEC-``): supporting claims via ``claims`` | ``claim_ids`` |
  ``evidence_claims`` | ``evidence``. A mechanism is *exploratory* when
  ``exploratory: true`` or its ``status``/``maturity``/``classification`` is
  one of ``exploratory``, ``hypothesis``, ``hypothetical``, ``speculative``.
  A mechanism is *implemented* when ``implemented: true``, its status is
  ``implemented``/``coded``/``deployed``, or it carries ``implementation`` /
  ``code_path``. Tests covering a mechanism are declared on the mechanism
  via ``tests`` | ``test_ids`` | ``validation_tests`` | ``validated_by`` or
  on validation tests via ``mechanisms`` | ``mechanism_ids`` |
  ``covers_mechanisms`` | ``targets``.
* equations (``EQ-``): ``expression`` (alias ``equation``/``formula``/
  ``latex``), ``assumptions``, ``provenance`` (alias ``source``/
  ``derived_from``/``origin``).
* parameters (``PAR-``): ``source``, ``estimation_method`` (alias
  ``estimation``/``method``), ``provenance`` (alias ``derived_from``).
* validation tests (``VAL-``): ``expected_behavior`` (alias ``expected``/
  ``expected_result``), ``acceptance_criteria`` (alias ``acceptance``/
  ``criteria``), ``justification`` (alias ``rationale``/``purpose``).
* simulations (``SIM-``): config via ``config`` | ``config_path`` |
  ``configuration`` | ``config_file``; model provenance via ``model`` |
  ``model_id`` | ``model_version`` | ``model_commit`` | ``model_provenance``.

Cross-registry links are recognised generically: any string anywhere in an
entry (except its own ``id`` field) matching ``REF-``, ``CLM-``, ``MEC-``,
``EQ-``, ``PAR-``, ``VAL-`` or ``SIM-`` followed by an identifier is treated
as a link and must resolve to an existing registry entry.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .registries import (
    Registry,
    RegistryEntry,
    first_present,
    is_nonempty,
    iter_strings,
)

# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"
SEVERITIES = (SEVERITY_ERROR, SEVERITY_WARNING, SEVERITY_INFO)


@dataclass(frozen=True)
class Finding:
    """A single audit finding."""

    check: str
    severity: str
    message: str
    registry: str | None = None
    entry_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "check": self.check,
            "severity": self.severity,
            "registry": self.registry,
            "entry_id": self.entry_id,
            "message": self.message,
        }


# ---------------------------------------------------------------------------
# Completeness metrics
# ---------------------------------------------------------------------------


@dataclass
class Metric:
    """A completeness counter: how many entries satisfy a requirement."""

    passed: int = 0
    total: int = 0

    def record(self, ok: bool) -> None:
        self.total += 1
        if ok:
            self.passed += 1

    @property
    def rate(self) -> float | None:
        if self.total == 0:
            return None
        return round(self.passed / self.total, 4)

    def as_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "total": self.total, "rate": self.rate}


# ---------------------------------------------------------------------------
# Audit context
# ---------------------------------------------------------------------------

#: Recognised cross-registry ID references, e.g. ``CLM-0001``.
ID_REF_RE = re.compile(
    r"\b(?:REF|CLM|MEC|EQ|PAR|VAL|SIM)-[A-Za-z0-9](?:[A-Za-z0-9_.\-]*[A-Za-z0-9])?"
)

EXPLORATORY_STATUSES = frozenset({"exploratory", "hypothesis", "hypothetical", "speculative"})
IMPLEMENTED_STATUSES = frozenset({"implemented", "coded", "deployed"})


@dataclass
class AuditContext:
    """Everything the checks need: registries plus a global ID/link index."""

    root: Path
    registries: dict[str, Registry]
    findings: list[Finding] = field(default_factory=list)
    completeness: dict[str, dict[str, Metric]] = field(default_factory=dict)
    id_index: dict[str, str] = field(default_factory=dict)  # id -> registry name
    # referenced id -> set of (registry, entry label) that reference it
    referenced_by: dict[str, set[tuple[str, str]]] = field(default_factory=dict)

    # -- helpers ---------------------------------------------------------

    def add(
        self,
        check: str,
        severity: str,
        message: str,
        entry: RegistryEntry | None = None,
        registry: str | None = None,
    ) -> None:
        self.findings.append(
            Finding(
                check=check,
                severity=severity,
                message=message,
                registry=entry.registry if entry is not None else registry,
                entry_id=entry.entry_id if entry is not None else None,
            )
        )

    def metric(self, registry: str, name: str) -> Metric:
        return self.completeness.setdefault(registry, {}).setdefault(name, Metric())

    def entries(self, registry: str) -> Iterable[RegistryEntry]:
        return self.registries[registry].entries


def build_context(root: Path, registries: dict[str, Registry]) -> AuditContext:
    """Create the context, index IDs, and build the cross-reference graph."""
    ctx = AuditContext(root=Path(root), registries=registries)
    for registry in registries.values():
        for entry in registry.entries:
            if entry.entry_id is not None:
                ctx.id_index[entry.entry_id] = registry.name
    # Cross-reference graph: every ID-like string except an entry's own id.
    for registry in registries.values():
        for entry in registry.entries:
            for key, value in entry.data.items():
                if key == "id":
                    continue
                for text in iter_strings(value):
                    for ref in ID_REF_RE.findall(text):
                        if ref != entry.entry_id:
                            ctx.referenced_by.setdefault(ref, set()).add(
                                (registry.name, entry.label)
                            )
    return ctx


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_registry_health(ctx: AuditContext) -> None:
    """Load errors, duplicate IDs, and ID prefix conformance."""
    for registry in ctx.registries.values():
        if not registry.found:
            ctx.add(
                "registry-not-found",
                SEVERITY_INFO,
                "registry file not found (searched: "
                + ", ".join(registry.spec.path_candidates)
                + ")",
                registry=registry.name,
            )
            continue
        for error in registry.load_errors:
            ctx.add(
                "registry-load-error",
                SEVERITY_ERROR,
                f"{registry.path}: {error}",
                registry=registry.name,
            )
        seen: set[str] = set()
        for entry in registry.entries:
            eid = entry.entry_id
            if eid is None:
                ctx.add(
                    "missing-id",
                    SEVERITY_ERROR,
                    f"entry {entry.index} has no 'id' field",
                    entry=entry,
                )
                continue
            if eid in seen:
                ctx.add(
                    "duplicate-id",
                    SEVERITY_ERROR,
                    f"duplicate id {eid!r} in registry {registry.name!r}",
                    entry=entry,
                )
            seen.add(eid)
            if not eid.startswith(registry.spec.id_prefix):
                ctx.add(
                    "id-prefix-mismatch",
                    SEVERITY_WARNING,
                    f"id {eid!r} does not start with expected prefix {registry.spec.id_prefix!r}",
                    entry=entry,
                )
        metric = ctx.metric(registry.name, "entries_with_id")
        metric.total = len(registry.entries)
        metric.passed = sum(1 for e in registry.entries if e.entry_id)


# -- evidence claims --------------------------------------------------------


def check_claims_have_references(ctx: AuditContext) -> None:
    metric = ctx.metric("evidence", "claims_with_references")
    for entry in ctx.entries("evidence"):
        refs, _ = first_present(entry.data, "references", "reference_ids", "citations")
        ok = is_nonempty(refs)
        metric.record(ok)
        if not ok:
            ctx.add(
                "claim-without-references",
                SEVERITY_ERROR,
                f"evidence claim {entry.label} has no supporting references",
                entry=entry,
            )


# -- mechanisms -------------------------------------------------------------


def _status_of(entry: RegistryEntry) -> str:
    value, _ = first_present(entry.data, "status", "maturity", "classification")
    return str(value).strip().lower() if value is not None else ""


def is_exploratory(entry: RegistryEntry) -> bool:
    if entry.data.get("exploratory") is True:
        return True
    return _status_of(entry) in EXPLORATORY_STATUSES


def is_implemented(entry: RegistryEntry) -> bool:
    if entry.data.get("implemented") is True:
        return True
    status = _status_of(entry)
    if status:
        return status in IMPLEMENTED_STATUSES
    if is_exploratory(entry):
        return False
    impl, _ = first_present(entry.data, "implementation", "code_path")
    return is_nonempty(impl)


def mechanism_test_links(
    ctx: AuditContext,
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Return (mechanism_id -> test ids, test_id -> mechanism ids)."""
    mech_to_tests: dict[str, set[str]] = {}
    test_to_mechs: dict[str, set[str]] = {}
    for entry in ctx.entries("mechanisms"):
        if entry.entry_id is None:
            continue
        tests, _ = first_present(
            entry.data, "tests", "test_ids", "validation_tests", "validated_by"
        )
        for ref in _id_list(tests):
            mech_to_tests.setdefault(entry.entry_id, set()).add(ref)
            test_to_mechs.setdefault(ref, set()).add(entry.entry_id)
    for entry in ctx.entries("validation_tests"):
        if entry.entry_id is None:
            continue
        mechs, _ = first_present(
            entry.data, "mechanisms", "mechanism_ids", "covers_mechanisms", "targets"
        )
        for ref in _id_list(mechs):
            test_to_mechs.setdefault(entry.entry_id, set()).add(ref)
            mech_to_tests.setdefault(ref, set()).add(entry.entry_id)
    return mech_to_tests, test_to_mechs


def _id_list(value: Any) -> list[str]:
    """Extract ID references from a field that may be a string or list."""
    if value is None:
        return []
    refs: list[str] = []
    for text in iter_strings(value):
        refs.extend(ID_REF_RE.findall(text))
    return refs


def check_mechanisms_have_claims(ctx: AuditContext) -> None:
    metric = ctx.metric("mechanisms", "mechanisms_with_claims_or_exploratory")
    for entry in ctx.entries("mechanisms"):
        claims, _ = first_present(entry.data, "claims", "claim_ids", "evidence_claims", "evidence")
        if is_nonempty(claims):
            metric.record(True)
            continue
        if is_exploratory(entry):
            metric.record(True)
            ctx.add(
                "exploratory-mechanism-without-claims",
                SEVERITY_INFO,
                f"exploratory mechanism {entry.label} has no supporting "
                "evidence claims (allowed while exploratory)",
                entry=entry,
            )
        else:
            metric.record(False)
            ctx.add(
                "mechanism-without-claims",
                SEVERITY_ERROR,
                f"mechanism {entry.label} has no supporting evidence claims "
                "and is not marked exploratory",
                entry=entry,
            )


def check_implemented_mechanisms_have_tests(ctx: AuditContext) -> None:
    mech_to_tests, _ = mechanism_test_links(ctx)
    metric = ctx.metric("mechanisms", "implemented_mechanisms_with_tests")
    for entry in ctx.entries("mechanisms"):
        if not is_implemented(entry):
            continue
        tests = mech_to_tests.get(entry.entry_id or "", set())
        # Only count links that resolve to real validation tests.
        real_tests = {t for t in tests if ctx.id_index.get(t) == "validation_tests"}
        metric.record(bool(real_tests))
        if not real_tests:
            ctx.add(
                "implemented-mechanism-without-tests",
                SEVERITY_ERROR,
                f"implemented mechanism {entry.label} is not covered by any validation test",
                entry=entry,
            )


# -- equations --------------------------------------------------------------


def check_equations(ctx: AuditContext) -> None:
    expr_m = ctx.metric("equations", "equations_with_expression")
    assump_m = ctx.metric("equations", "equations_with_assumptions")
    prov_m = ctx.metric("equations", "equations_with_provenance")
    full_m = ctx.metric("equations", "equations_fully_documented")
    for entry in ctx.entries("equations"):
        expression, _ = first_present(entry.data, "expression", "equation", "formula", "latex")
        assumptions = entry.data.get("assumptions")
        provenance, _ = first_present(entry.data, "provenance", "source", "derived_from", "origin")
        ok_expr = is_nonempty(expression)
        ok_assump = is_nonempty(assumptions)
        ok_prov = is_nonempty(provenance)
        expr_m.record(ok_expr)
        assump_m.record(ok_assump)
        prov_m.record(ok_prov)
        full_m.record(ok_expr and ok_assump and ok_prov)
        if not ok_expr:
            ctx.add(
                "equation-missing-expression",
                SEVERITY_ERROR,
                f"equation {entry.label} has no mathematical expression",
                entry=entry,
            )
        if not ok_assump:
            ctx.add(
                "equation-missing-assumptions",
                SEVERITY_ERROR,
                f"equation {entry.label} has no documented assumptions",
                entry=entry,
            )
        if not ok_prov:
            ctx.add(
                "equation-missing-provenance",
                SEVERITY_ERROR,
                f"equation {entry.label} has no provenance (source/derivation)",
                entry=entry,
            )


# -- parameters -------------------------------------------------------------


def check_parameters(ctx: AuditContext) -> None:
    src_m = ctx.metric("parameters", "parameters_with_source")
    est_m = ctx.metric("parameters", "parameters_with_estimation_method")
    prov_m = ctx.metric("parameters", "parameters_with_provenance")
    full_m = ctx.metric("parameters", "parameters_fully_documented")
    for entry in ctx.entries("parameters"):
        source = entry.data.get("source")
        method, _ = first_present(entry.data, "estimation_method", "estimation", "method")
        provenance, _ = first_present(entry.data, "provenance", "derived_from")
        ok_src = is_nonempty(source)
        ok_est = is_nonempty(method)
        ok_prov = is_nonempty(provenance)
        src_m.record(ok_src)
        est_m.record(ok_est)
        prov_m.record(ok_prov)
        full_m.record(ok_src and ok_est and ok_prov)
        if not ok_src:
            ctx.add(
                "parameter-missing-source",
                SEVERITY_ERROR,
                f"parameter {entry.label} has no source",
                entry=entry,
            )
        if not ok_est:
            ctx.add(
                "parameter-missing-estimation-method",
                SEVERITY_ERROR,
                f"parameter {entry.label} has no estimation method",
                entry=entry,
            )
        if not ok_prov:
            ctx.add(
                "parameter-missing-provenance",
                SEVERITY_ERROR,
                f"parameter {entry.label} has no provenance",
                entry=entry,
            )


# -- validation tests -------------------------------------------------------


def check_validation_tests(ctx: AuditContext) -> None:
    exp_m = ctx.metric("validation_tests", "tests_with_expected_behavior")
    acc_m = ctx.metric("validation_tests", "tests_with_acceptance_criteria")
    jus_m = ctx.metric("validation_tests", "tests_with_justification")
    full_m = ctx.metric("validation_tests", "tests_fully_specified")
    for entry in ctx.entries("validation_tests"):
        expected, _ = first_present(entry.data, "expected_behavior", "expected", "expected_result")
        acceptance, _ = first_present(entry.data, "acceptance_criteria", "acceptance", "criteria")
        justification, _ = first_present(entry.data, "justification", "rationale", "purpose")
        ok_exp = is_nonempty(expected)
        ok_acc = is_nonempty(acceptance)
        ok_jus = is_nonempty(justification)
        exp_m.record(ok_exp)
        acc_m.record(ok_acc)
        jus_m.record(ok_jus)
        full_m.record(ok_exp and ok_acc and ok_jus)
        if not ok_exp:
            ctx.add(
                "test-missing-expected-behavior",
                SEVERITY_ERROR,
                f"validation test {entry.label} has no expected behavior",
                entry=entry,
            )
        if not ok_acc:
            ctx.add(
                "test-missing-acceptance-criteria",
                SEVERITY_ERROR,
                f"validation test {entry.label} has no acceptance criteria",
                entry=entry,
            )
        if not ok_jus:
            ctx.add(
                "test-missing-justification",
                SEVERITY_ERROR,
                f"validation test {entry.label} has no scientific justification",
                entry=entry,
            )


# -- simulations ------------------------------------------------------------


def check_simulations(ctx: AuditContext) -> None:
    cfg_m = ctx.metric("simulations", "simulations_with_config")
    mdl_m = ctx.metric("simulations", "simulations_with_model_provenance")
    for entry in ctx.entries("simulations"):
        config, _ = first_present(
            entry.data, "config", "config_path", "configuration", "config_file"
        )
        model, _ = first_present(
            entry.data,
            "model",
            "model_id",
            "model_version",
            "model_commit",
            "model_provenance",
        )
        ok_cfg = is_nonempty(config)
        ok_mdl = is_nonempty(model)
        cfg_m.record(ok_cfg)
        mdl_m.record(ok_mdl)
        if not ok_cfg:
            ctx.add(
                "simulation-missing-config",
                SEVERITY_ERROR,
                f"simulation output {entry.label} has no config provenance",
                entry=entry,
            )
        if not ok_mdl:
            ctx.add(
                "simulation-missing-model-provenance",
                SEVERITY_ERROR,
                f"simulation output {entry.label} has no model provenance "
                "(model id/version/commit)",
                entry=entry,
            )


# -- cross-registry links and orphans ---------------------------------------


def check_broken_links(ctx: AuditContext) -> None:
    for registry in ctx.registries.values():
        for entry in registry.entries:
            for key, value in entry.data.items():
                if key == "id":
                    continue
                for text in iter_strings(value):
                    for ref in ID_REF_RE.findall(text):
                        if ref == entry.entry_id or ref in ctx.id_index:
                            continue
                        ctx.add(
                            "broken-cross-registry-link",
                            SEVERITY_ERROR,
                            f"{entry.label} references unknown id {ref!r} (field {key!r})",
                            entry=entry,
                        )


def check_orphans(ctx: AuditContext) -> None:
    """Warn about evidence/unused components not referenced anywhere."""
    mech_to_tests, _ = mechanism_test_links(ctx)
    for entry in ctx.entries("evidence"):
        if entry.entry_id and not ctx.referenced_by.get(entry.entry_id):
            ctx.add(
                "orphan-evidence-claim",
                SEVERITY_WARNING,
                f"evidence claim {entry.label} is not referenced by any "
                "mechanism or other component",
                entry=entry,
            )
    for entry in ctx.entries("references"):
        if entry.entry_id and not ctx.referenced_by.get(entry.entry_id):
            ctx.add(
                "uncited-reference",
                SEVERITY_WARNING,
                f"reference {entry.label} is not cited by any evidence claim or other component",
                entry=entry,
            )
    for entry in ctx.entries("mechanisms"):
        if entry.entry_id is None:
            continue
        used = (
            bool(ctx.referenced_by.get(entry.entry_id))
            or bool(mech_to_tests.get(entry.entry_id))
            or is_implemented(entry)
        )
        if not used:
            ctx.add(
                "unused-mechanism",
                SEVERITY_WARNING,
                f"mechanism {entry.label} is not implemented and not used by "
                "any test, simulation, or other component",
                entry=entry,
            )
    for name, check in (("equations", "unused-equation"), ("parameters", "unused-parameter")):
        for entry in ctx.entries(name):
            if entry.entry_id and not ctx.referenced_by.get(entry.entry_id):
                ctx.add(
                    check,
                    SEVERITY_WARNING,
                    f"{name[:-1]} {entry.label} is not referenced by any "
                    "mechanism, test, or simulation",
                    entry=entry,
                )


#: Default checks, in execution order.
ALL_CHECKS = (
    check_registry_health,
    check_claims_have_references,
    check_mechanisms_have_claims,
    check_implemented_mechanisms_have_tests,
    check_equations,
    check_parameters,
    check_validation_tests,
    check_simulations,
    check_broken_links,
    check_orphans,
)


def run_checks(ctx: AuditContext, checks: Iterable = ALL_CHECKS) -> AuditContext:
    for check in checks:
        check(ctx)
    return ctx


def main(argv=None) -> int:
    """Console-script entry point (``ocpe-dm-traceability``).

    Delegates to :func:`.runner.main`; imported lazily to avoid a circular
    import, since :mod:`.runner` depends on this module.
    """
    from .runner import main as _main

    return _main(argv)
