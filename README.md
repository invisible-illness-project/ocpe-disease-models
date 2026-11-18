# OCPE Disease Models

Literature-grounded, executable research models of POTS, hEDS-associated orthostatic intolerance, ME/CFS post-exertional malaise (PEM), and Long COVID physiological subgroups, with scientific provenance and seven-layer validation.

**Research software only.** These models are reduced-order computational scenarios, not diagnostic tools, treatment guides, digital twins, or clinically validated representations of individual patients. A successful simulation or a POTS threshold crossing is not evidence of clinical validity.

## What is implemented

- A beat-averaged, volume-conserving cardiovascular and autonomic model (Stage 1.1 architecture with Stage 1.2 scientific remediation, twelve states) with five conservative stressed-volume compartments (arterial, central venous, splanchnic venous, lower-limb venous, and one aggregated residual systemic venous bed), differentiated vagal, cardiac-sympathetic, and vascular-sympathetic effector states, an explicit rhythmic skeletal-muscle pump, an independent sustained-contraction venous impediment, preload-dependent stroke volume, separate aortic/carotid baroreceptor and brain-level pressures, explicit tilt-angle and end-tidal-CO2 protocol inputs, bounded CO2-dependent cerebral regulation, and a normalized cerebral-flow index (CFI). Stage 1.2 assigns every peripheral venous bed an effective dependent height, removing the Stage 1.1 residual-bed preload bypass without changing the governing equations.
- POTS neuropathic, hyperadrenergic, hypovolemic, and explicitly mixed configurations.
- An exploratory hEDS lower-limb venous-compliance scenario (migrated from the original aggregated peripheral-compliance scenario); it does not generalize to other EDS subtypes or treat arterial elasticity as venous compliance.
- A phenomenological ME/CFS exertion → delayed stress → PEM → reduced subsequent capacity cascade with asymmetric recovery.
- Separate Long COVID autonomic and exertional/oxygen-extraction configurations rather than one uniform disease model.
- OCPE semantic packages, strict observation mapping, compact reproducible traces, six demonstrations, sensitivity/uncertainty analyses, and an end-to-end traceability audit.

OCPE 0.1 supplies specification, identifier, unit, evidence, package-validation, and observation-exchange infrastructure. The pinned OCPE revision does **not** contain a numerical solver. Numerical integration therefore lives in this repository; OCPE is not misrepresented as executing these equations.

## Setup

Python 3.11 or later is required. Installation fetches OCPE at exact commit `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`.

```bash
python -m pip install -e '.[dev]'
```

For an offline source setup, install the pinned upstream `implementations/python` package first, then install this repository without replacing that pin. Configuration discovery expects a source checkout or `OCPE_DM_ROOT` pointing to one. The OCPE adapter resolves its package relative to the source tree and does not use `OCPE_DM_ROOT`; wheel-only callers must pass `package_dir` explicitly. See `docs/reproducibility.md`.

## Run the demonstrations

```bash
python scripts/run_examples.py
```

This writes compact NPZ traces, JSON parameters/metadata/summaries, validated final-time OCPE observations, and figures under `examples/<example>/output/`. These are validation traces, not wearable or machine-learning datasets.

Run one simulation directly:

```bash
python scripts/simulate.py simulate \
  --phenotype pots-neuropathic \
  --protocol head-up-tilt \
  --output /tmp/pots-trace
```

## Validate

```bash
pytest -q
python scripts/audit_traceability.py --root . --strict --deterministic \
  --out-dir validation/traceability/audit
ocpe validate ocpe/packages/disease-models --strict
python scripts/run_sensitivity.py
python scripts/run_validation.py --no-analysis
```

The Stage 1.1 matrix writer is a historical reproduction command, not part of the current default validation sequence; it must not overwrite Stage 1.2 evidence.

The seven layers—software, mathematical, physiological, disease phenotype, empirical, sensitivity/uncertainty, and scientific traceability—are reported separately. Empty test selections, missing references, failed scenarios, and strict-audit warnings are not converted into passes. See `docs/validation/validation-runbook.md`, `validation/reports/validation-report.md`, and `validation/stage1-2/scientific-comparison-matrix.md` for the executed snapshots. Stage 1.2 retains two explicit 60° cardiac-output comparison misses even though its activated regression tests pass.

## Scientific map

The auditable chain is:

```text
reference → evidence claim → mechanism → equation → parameter
          → implementation → validation test → simulation output
```

Start with:

- `literature/references.yaml` and `literature/bibliography.bib`
- disease reviews under `literature/{pots,eds,mecfs,long_covid,cross_disease}/`
- `literature/evidence_registry.yaml`
- `literature/mechanism_registry.yaml`
- `literature/equation_registry.yaml`
- `literature/parameter_registry.yaml`
- `validation/validation_registry.yaml`
- `simulations/simulation_registry.yaml`

`docs/architecture.md` explains the numerical and OCPE boundaries; `docs/methodology.md` documents equations and protocols; `docs/maturity-model.md` separates evidence grades from M0–M4 maturity; `docs/limitations.md` records unresolved scientific and engineering issues. `docs/technical-handoff.md` provides the A–L release handoff, and `validation/reproducibility.json` binds the executed results to source and artifact hashes.

The Stage 1 design and review record lives under `docs/stage1/`:

- `docs/stage1/baseline-scientific-report.md` — audit of the original three-compartment implementation (Stage 0, preserved as history).
- `docs/stage1/literature-and-evidence-matrix.md` — evidence-to-mechanism decisions for the revision.
- `docs/stage1/revised-physiological-architecture.md` — the reviewed four-compartment eleven-state Stage 1 architecture and calibration record, preserved as history.

The Stage 1.1 architecture, scientific decisions, validation matrix, and readiness assessment are preserved under `docs/stage1-1/`; its generated time-resolved scientific comparison remains under `validation/stage1-1/`.

The current Stage 1.2 root-cause analysis, calibration decisions, rejected alternatives, exact before/after metrics, and readiness assessment are under `docs/stage1-2/` and `validation/stage1-2/`. Six of eight preserved Zaidi comparisons now pass; the two 60° cardiac-output misses and persistent healthy MAP over-defence remain disclosed. All four POTS configurations and Long-COVID-autonomic pass their sustained-HR scenario criteria without chronotropic-gain changes.

## Scope

Stage 2 synthetic wearable dataset generation, large simulated cohorts, Stage 3 flare prediction, TSFM training, patient-facing software, and clinical recommendations are excluded. The deterministic sensitivity grids are not synthetic patients and have no assigned probabilities.

## License and citation

Apache-2.0; see `LICENSE` and `CITATION.cff`. Preserve the OCPE commit and all reference identifiers when reusing scientific records.
