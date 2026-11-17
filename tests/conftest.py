"""Shared fixtures and helpers for the validation test suite.

Implements the executable side of ``validation/validation_registry.yaml``.
Layer-to-marker mapping follows ``pyproject.toml``:

- ``software``       -> registry layer ``software`` and ``scientific_traceability``
- ``mathematical``   -> registry layers ``mathematical`` and ``sensitivity_uncertainty``
- ``physiological``  -> registry layer ``physiological``
- ``phenotype``      -> registry layer ``disease_phenotype``
- ``empirical``      -> registry layer ``empirical``
- ``regression``     -> registry layer ``software`` regression fixtures (VAL-REGRESSION)

All simulations are deterministic (fixed solver settings, no randomness).
Expensive exertion-protocol runs are session-scoped so each phenotype/protocol
pair is integrated once per test session.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocpe_disease_models.config import (  # noqa: E402
    compose_phenotypes,
    load_protocol,
    repository_root,
)
from ocpe_disease_models.models.shared import (  # noqa: E402
    ComputationalPatient,
    ModelParameters,
)
from ocpe_disease_models.models.shared.model import STATE_NAMES  # noqa: E402

SOLVER_KEYS = ("sample_interval", "max_step", "rtol", "atol", "seed")

# Conserved stressed-volume compartments: arterial through other-systemic venous.
VOLUME_STATE_COUNT = STATE_NAMES.index("other_systemic_venous_volume") + 1

# Tilt protocol timing (simulations/orthostatic/head-up-tilt.yaml).
TILT_START = 120.0
TILT_END = 600.0


def run_phenotype(phenotype_id: str, protocol_id: str, **solver_overrides):
    """Run a configured phenotype against a configured protocol, deterministically."""
    patient = compose_phenotypes([phenotype_id])
    segments, settings = load_protocol(protocol_id)
    solver = {k: v for k, v in settings.items() if k in SOLVER_KEYS}
    solver.update(solver_overrides)
    return patient.simulate(segments, **solver)


def stressed_volume_drift(result) -> float:
    """Maximum absolute drift of total stressed volume (mL) from its initial value."""
    total = result.states[:VOLUME_STATE_COUNT].sum(axis=0)
    return float(np.abs(total - total[0]).max())


def orthostatic_metrics(result) -> dict[str, float]:
    """Orthostatic summary for the head-up-tilt protocol geometry.

    ``hr_rise`` uses the peak upright HR within the first 300 s upright minus the
    supine baseline mean (the same convention as ``SimulationResult.summary``);
    ``hr_rise_sustained`` uses the mean over the final 120 s upright instead.
    """
    t = result.time
    hr = result.outputs["heart_rate"]
    map_ = result.outputs["mean_arterial_pressure"]
    sym = result.outputs["sympathetic_state"]
    venous = result.outputs["venous_return"]
    supine = (t >= 0.0) & (t <= TILT_START - 2.0)
    upright_end = min(TILT_END, float(t[-1]))
    upright_first300 = (t >= TILT_START) & (t <= min(TILT_START + 300.0, upright_end))
    upright_late = (t >= max(TILT_START, upright_end - 120.0)) & (t <= upright_end)
    baseline = float(hr[supine].mean())
    return {
        "hr_baseline": baseline,
        "hr_upright_peak": float(hr[upright_first300].max()),
        "hr_rise": float(hr[upright_first300].max() - baseline),
        "hr_rise_sustained": float(hr[upright_late].mean() - baseline),
        "map_final": float(map_[-1]),
        "map_upright_min": float(map_[(t >= TILT_START) & (t <= upright_end)].min()),
        "sympathetic_supine": float(sym[supine].mean()),
        "sympathetic_upright_late": float(sym[upright_late].mean()),
        "venous_return_supine": float(venous[(t >= TILT_START - 20.0) & (t <= TILT_START - 2.0)].mean()),
        "venous_return_upright_early_min": float(
            venous[(t >= TILT_START) & (t <= TILT_START + 30.0)].min()
        ),
        "volume_drift": stressed_volume_drift(result),
    }


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return repository_root()


@pytest.fixture(scope="session")
def run_cached():
    """Session-wide memoized phenotype/protocol runner (deterministic runs)."""
    cache: dict[tuple[str, str], object] = {}

    def _run(phenotype_id: str, protocol_id: str):
        key = (phenotype_id, protocol_id)
        if key not in cache:
            cache[key] = run_phenotype(phenotype_id, protocol_id)
        return cache[key]

    return _run


@pytest.fixture(scope="session")
def healthy_baseline_result(run_cached):
    return run_cached("healthy-reference", "resting-baseline")


@pytest.fixture(scope="session")
def healthy_tilt_result(run_cached):
    return run_cached("healthy-reference", "head-up-tilt")


@pytest.fixture(scope="session")
def healthy_tilt_recovery_result(run_cached):
    return run_cached("healthy-reference", "tilt-recovery")


@pytest.fixture(scope="session")
def mecfs_tilt_recovery_result(run_cached):
    return run_cached("mecfs-pem", "tilt-recovery")


@pytest.fixture(scope="session")
def mecfs_repeated_exertion_result(run_cached):
    return run_cached("mecfs-pem", "repeated-exertion-recovery")


@pytest.fixture(scope="session")
def healthy_repeated_exertion_result(run_cached):
    return run_cached("healthy-reference", "repeated-exertion-recovery")


@pytest.fixture(scope="session")
def default_parameters() -> ModelParameters:
    return ModelParameters()


@pytest.fixture(scope="session")
def patient_factory():
    def _make(overrides: dict | None = None, phenotype_id: str = "test-patient"):
        return ComputationalPatient(
            ModelParameters().replaced(overrides or {}), phenotype_id=phenotype_id
        )

    return _make
