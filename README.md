# OCPE Disease Models

Literature-grounded, executable research models of POTS, hEDS-associated orthostatic intolerance, ME/CFS post-exertional malaise (PEM), and Long COVID physiological subgroups, with scientific provenance and seven-layer validation.

**Research software only.** These models are reduced-order computational scenarios, not diagnostic tools, treatment guides, digital twins, or clinically validated representations of individual patients. A successful simulation or a POTS threshold crossing is not evidence of clinical validity.

## What is implemented

- A beat-averaged, volume-conserving cardiovascular and autonomic model (Stage 1 revision, eleven states) with four conservative stressed-volume compartments (arterial, central venous, splanchnic venous, lower-limb venous), differentiated vagal, cardiac-sympathetic, and vascular-sympathetic effector states, an explicit rhythmic skeletal-muscle pump, an independent sustained-contraction venous impediment, preload-dependent stroke volume, and a cerebral-perfusion-pressure-based normalized cerebral-flow index (CPP/CFI).
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
python scripts/audit_traceability.py --root . --strict
ocpe validate ocpe/packages/disease-models --strict
python scripts/run_sensitivity.py
python scripts/run_validation.py
```

The seven layers—software, mathematical, physiological, disease phenotype, empirical, sensitivity/uncertainty, and scientific traceability—are reported separately. Empty test selections, missing references, failed scenarios, and strict-audit warnings are not converted into passes. See `docs/validation/validation-runbook.md` and `validation/reports/validation-report.md` for the executed snapshot.

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
- `docs/stage1/revised-physiological-architecture.md` — the reviewed four-compartment eleven-state architecture, migration formulas, per-phenotype fixed-point derivation, and calibration record implemented in the current code.

## Scope

Stage 2 synthetic wearable dataset generation, large simulated cohorts, Stage 3 flare prediction, TSFM training, patient-facing software, and clinical recommendations are excluded. The deterministic sensitivity grids are not synthetic patients and have no assigned probabilities.

## License and citation

Apache-2.0; see `LICENSE` and `CITATION.cff`. Preserve the OCPE commit and all reference identifiers when reusing scientific records.
