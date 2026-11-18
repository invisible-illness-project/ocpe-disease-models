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

Every command must collect tests. Pytest exit code 5 (`no tests ran`) is a validation failure. Investigate failed numerical tolerances or scenario criteria; do not weaken a criterion after seeing an inconvenient result without a documented scientific review. Stage 1.1's five POTS/Long-COVID-autonomic strict expected failures are preserved only in its historical commit and reports. Stage 1.2 removed them after direct passes; current Stage 1.3 behavior is guarded by `tests/physiological/test_stage1_3_orthostatic_fidelity.py`. All eight preserved CO/SV comparisons are within band: four 60° rows are direct experimental-angle comparisons, while four 70° rows are extrapolated model-specific criteria. Neither category is independent clinical validation.

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

Review `validation/sensitivity/sensitivity-report.md` and full JSON/CSV rows. Stage 1.3 exports 96 local scenarios, 27 deterministic grid scenarios, and three chronotropic-split scenarios, including every changed healthy parameter, dependent elastance, and paired baroreflex-weight perturbations. CO2-reactivity/clipping and CO2-reactivity × cerebral-outflow coverage remain included. No current hEDS grid case ends below 70 mmHg MAP; historical failures remain separate. The separate healthy tilt-ranking check deliberately spans gain 0.35 through the Stage 1.2 nominal 0.8 and is asymmetric around the Stage 1.3 nominal 0.45; it is not a centered statistical interval. Do not delete failed combinations or describe a grid as a patient distribution. There is no stochastic sampling; seed metadata does not substitute for probabilistic analysis.

## 6. Full seven-layer report

```bash
python scripts/run_validation.py
```

Generate current Stage 1.3 mechanism-isolation, orthostatic, empirical-comparison, and cerebral evidence with:

```bash
python scripts/run_stage1_3_validation.py
```

`python scripts/run_stage1_1_validation.py` is reserved for historical reproduction in a Stage 1.1 checkout. Do not use it as a current writer or overwrite `validation/stage1-1/`; current before/after evidence is under `validation/stage1-3/`, with exhaustive Stage 1.2 reproduction in `validation/stage1-3/baseline-reproduction.json`.

To rerun without recomputing sensitivity artifacts:

```bash
python scripts/run_validation.py --no-analysis
```

A nonzero command exit remains expected whenever unresolved strict scientific expected failures are present. Stage 1.3 has none, but a zero exit still does not establish independent physiological or clinical validity; inspect the separate per-layer execution and scientific statuses and the Stage 1.3 comparison matrix.

For one layer, use a repeated explicit selector, for example:

```bash
python scripts/run_validation.py --layer mathematical --layer scientific_traceability
```

Read `validation/stage1-3/scientific-comparison-matrix.md`, `docs/stage1-3/readiness-assessment.md`, `validation/reports/validation-report.md`, JSON, and individual logs. `PASS` applies only to the declared computational checks with no strict expected failure. The seven-layer runner deliberately marks a layer `FAIL` when pytest reports an xfail, even if its process exits zero. Stage 1.3's within-band comparisons remain calibrated scenario agreements with narrow disclosed margins; they do not resolve structural uncertainty or establish clinical readiness. A partial-layer run is not a full release validation. Stage 1.2 and Stage 1.1 reports under their respective historical directories must not be presented as current results.

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
