# Reproducibility

How to reproduce the computational results of this repository, what metadata
is recorded with each run, and the known limits of that reproducibility.
Reproducibility here means *recomputing the same outputs from the same
configuration*; it is not validation and establishes nothing clinical.

## Environment

- Python ≥ 3.11 (CI exercises 3.11 and 3.12).
- The upstream OCPE engine is a pinned git dependency at commit
  **`3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`**. The pin appears in three
  places that must agree: `pyproject.toml` (dependency URL),
  `src/ocpe_disease_models/__init__.py::OCPE_COMMIT`, and
  `src/ocpe_disease_models/interfaces/ocpe_adapter/adapter.py::UPSTREAM_COMMIT`.

```bash
pip install -e '.[dev]'   # resolves ocpe from the pinned upstream commit
```

This install needs network access to GitHub. Offline equivalent (requires a
local upstream checkout whose HEAD is the pinned commit):

```bash
pip install -e /path/to/open-computational-physiology-engine/implementations/python
pip install pytest pytest-cov ruff jsonschema
```

## Command reference

All commands run from the repository root of a source checkout.

```bash
ruff check .                                              # lint
python -m pytest -q                                       # full test suite
python scripts/audit_traceability.py --root . --strict    # strict provenance audit (CI gate)
python -m ocpe validate ocpe/packages/disease-models --strict   # strict OCPE package validation
python scripts/run_examples.py                            # all six demonstrations
python scripts/run_sensitivity.py                         # deterministic sensitivity grids
python scripts/run_validation.py                          # seven-layer runner (regenerates sensitivity first)
python scripts/run_validation.py --no-analysis            # seven-layer runner, reuse sensitivity outputs
python scripts/simulate.py simulate --phenotype <id> --protocol <id> --output <dir>
```

Notes:

- Marker-scoped pytest runs (`-m mathematical`, etc.) select only
  implemented layers. An empty selection exits with code 5 and is a
  **failure, not a pass** ("missing means failing");
  `scripts/run_validation.py` enforces this per layer.
- `python -m ocpe validate ... --strict` checks structural/semantic package
  soundness only — never scientific or clinical validity.
- Example runners and `simulate.py` overwrite their output directories; the
  curated `examples/*/output/` artifacts are pinned by
  `simulations/simulation_registry.yaml`.

## Recorded metadata

Every persisted run records, per the scope note in
`simulations/simulation_registry.yaml`:

- **Configuration SHA256** (`configuration_sha256`) over the composed
  phenotype parameters and protocol — the primary reproducibility key.
- **Solver settings**: `sample_interval`, `max_step`, `rtol`, `atol`, and
  `seed` (the solver keys recognized by the sensitivity runner).
- **Dependency versions** and the **OCPE commit** (the pinned
  `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`).
- **Model version**, **Python version**, and **repository commit** (also embedded in
  `validation/reports/validation-report.json`).

The traceability audit additionally records the repository git SHA
(`git rev-parse HEAD`, overridable via `TRACEABILITY_GIT_SHA`). With
`--deterministic`, timestamps and git invocation are suppressed so the audit
reports under `validation/traceability/audit/` are byte-for-byte
reproducible; the seven-layer runner always audits in deterministic mode.

Sensitivity scenarios are deterministic computational grids over named
parameter overrides — not random samples, synthetic patients, or
population-level uncertainty estimates. Where a `seed` is part of a solver
configuration it is fixed and recorded; results are reproducible
bit-for-bit only for the same dependency versions and platform.

## Known limitations

- **Source checkout required.** The built wheel contains only
  `src/ocpe_disease_models`; phenotypes, protocols, literature registries,
  validation registries, and the `ocpe/packages/disease-models` domain
  package live at the repository root and are **not** package data. Running
  simulations or the audit from an installed wheel without the checkout
  raises `FileNotFoundError` unless `OCPE_DM_ROOT` points at a checkout (see
  `src/ocpe_disease_models/config.py::repository_root`).
- **Pinned git dependency.** Installation resolves OCPE from GitHub at the
  pinned commit; without network, use the offline editable install above.
  One adapter test (`test_upstream_commit_matches_checkout`) additionally
  compares against a local upstream checkout path and skips when it is
  absent — the skip is environmental, not a result.
- **Layer coverage.** All seven declared layers have executable tests and are
  reported independently by `scripts/run_validation.py`. A green full-suite run
  alone is not a substitute for that layer report, strict traceability, or
  strict OCPE validation; none of these establishes clinical validity.
- **Platform numerics.** Solver outputs are deterministic for a fixed
  configuration and dependency set but may differ in trailing digits across
  BLAS/LAPACK builds and platforms; quantitative acceptance criteria carry
  tolerances for this reason.
