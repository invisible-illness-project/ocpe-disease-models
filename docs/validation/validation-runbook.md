# Validation runbook

## 1. Clean setup

Use Python 3.11+ and a full source checkout. Do not place credentials in the repository, command logs, environment files, or CI artifacts.

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

The dependency resolves OCPE at `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`. For an offline mirror, install that exact revision from its `implementations/python` directory before installing the disease package. Confirm:

```bash
python -c 'from ocpe_disease_models import OCPE_COMMIT; print(OCPE_COMMIT)'
git rev-parse HEAD
```

If configuration discovery fails in a non-source execution context, set `OCPE_DM_ROOT` to the disease repository root. If OCPE domain-package discovery fails, pass `package_dir` explicitly to the adapter. Do not silence these errors.

## 2. Pull-request checks

```bash
ruff check .
pytest -q
python scripts/audit_traceability.py --root . --strict --deterministic \
  --out-dir validation/traceability/audit
ocpe validate ocpe/packages/disease-models --strict
```

Expected release conditions: Ruff exits zero; pytest has no failure/error; the traceability audit has zero errors and warnings; OCPE reports zero errors and warnings. An import/install failure is not an empty validation result. A strict expected failure can leave pytest green while preserving an unresolved scientific assertion failure; it is not a physiological or release-validation pass.

Run focused software/regression checks without treating the count as scientific validation:

```bash
pytest -q -m 'software or regression'
pytest -q tests/unit tests/integration
```

## 3. Mathematical, physiological, phenotype, and empirical layers

```bash
pytest -q -m mathematical
pytest -q -m physiological
pytest -q -m phenotype
pytest -q -m empirical
```

Every command must collect tests. Pytest exit code 5 (`no tests ran`) is a validation failure. Investigate failed numerical tolerances or scenario criteria; do not weaken a criterion after seeing an inconvenient result without a documented scientific review. Stage 1.1 retains narrow strict xfails for the five unchanged POTS/Long-COVID-autonomic sustained-HR criterion misses; these are executable expected failures and remain `FAIL` in the scientific matrix and release assessment.

## 4. Demonstrations and observation exchange

```bash
python scripts/run_examples.py
python scripts/simulate.py simulate \
  --phenotype pots-neuropathic \
  --protocol head-up-tilt \
  --output /tmp/ocpe-dm-pots
```

Check that each registered example directory has `trace.npz`, `result.json`, `observations.json` where applicable, and `figure.png`. `result.json` must contain resolved parameters, protocol, configuration SHA, dependency versions, OCPE commit, solver settings, and scientific status. Observation records must pass strict OCPE validation.

## 5. Sensitivity and uncertainty

```bash
python scripts/run_sensitivity.py
pytest -q -m sensitivity_uncertainty
```

Review `validation/sensitivity/sensitivity-report.md` and full JSON/CSV rows. Stage 1.1 exports 59 local scenarios, 27 deterministic grid scenarios, and three chronotropic-split scenarios, including CO2-reactivity/clipping and CO2-reactivity × cerebral-outflow coverage. Inspect any MAP-below-70-mmHg hEDS grid cases and retain historical failures separately. Do not delete failed combinations or describe a grid as a patient distribution. There is no stochastic sampling; seed metadata does not substitute for probabilistic analysis.

## 6. Full seven-layer report

```bash
python scripts/run_stage1_1_validation.py
python scripts/run_validation.py
```

To rerun without recomputing sensitivity artifacts:

```bash
python scripts/run_validation.py --no-analysis
```

A successful command exit is not expected while unresolved strict scientific xfails remain; inspect the separate per-layer execution and scientific statuses rather than discarding the report.

For one layer, use a repeated explicit selector, for example:

```bash
python scripts/run_validation.py --layer mathematical --layer scientific_traceability
```

Read `validation/stage1-1/scientific-comparison-matrix.md`, `validation/reports/validation-report.md`, JSON, and individual logs. `PASS` applies only to the declared computational checks with no strict expected failure. The seven-layer runner deliberately marks a layer `FAIL` when pytest reports an xfail, even if its process exits zero; this keeps the unchanged POTS/Long-COVID-autonomic criterion misses visible in the overall release verdict. A partial-layer run is not a full release validation.

## 7. Regression updates

Never update fixtures merely to make a branch green. A legitimate update requires:

1. the scientific/engineering reason and expected direction;
2. affected evidence, equations, parameters, mechanisms, phenotypes, and simulations;
3. before/after metrics and solver/settings identity;
4. review and a change record;
5. complete validation rerun.

Preserve the old commit/report. A fixture is an approved numerical regression baseline, not a clinical reference interval.

## 8. Historical reproduction

Use a separate temporary clone; never reset the pinned upstream working tree. Git history remains the authoritative archive even where `migration_archive/` is absent from current OCPE.

```bash
git clone https://github.com/invisible-illness-project/open-computational-physiology-engine.git /tmp/ocpe-history
cd /tmp/ocpe-history
git checkout 64ef9e296b12e21b1f4909f2c46dc0d5e25169e7
python -m venv /tmp/ocpe-history-venv
/tmp/ocpe-history-venv/bin/python -m pip install -e implementations/python pytest
/tmp/ocpe-history-venv/bin/python -m pytest -q
/tmp/ocpe-history-venv/bin/python -m ocpe validate packages --strict
```

Use `git checkout 64ef9e2^` in another separate clone for the parent suite. Archived numerical tests at the refactor commit require their original paths; running them unchanged produces path/import failures and is not a valid scientific comparison. Record such failures explicitly.

Verified historical baselines from the migration audit are parent 75 passed/2 strict xfailed, authoritative commit 45 passed with strict package/dependency checks, and pinned current OCPE 121 passed. Dependency versions and execution dates belong in the reproduction record.

## 9. Troubleshooting

- **OCPE import resolves to the wrong checkout:** inspect the installed distribution and use an editable install of the exact intended revision; do not rely on the current working directory accidentally supplying another version.
- **No tests collected:** fix marker/path selection. Never accept it as a skip.
- **Strict traceability warning:** resolve the orphan, missing link, undocumented component, or unused scientific record. Do not use `--no-schema` for release.
- **Nonfinite or failed solver result:** retain the log, inspect parameters/protocol boundaries, and mark the affected layer failed.
- **Physiologically implausible but numerically converged output:** report the physiological failure; convergence is not a remedy.
- **Changed demonstration metric:** review it as a scientific change, not just a snapshot refresh.
