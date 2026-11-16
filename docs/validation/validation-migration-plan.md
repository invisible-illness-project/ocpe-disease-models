# Validation migration plan

## Objective

Migrate the scientific intent of the pre-0.1 OCPE validation system without copying its numerical engine, virtual cohorts, sensor synthesis, or fixed assumptions into an incompatible architecture. The target is a disease-specific executable framework backed by OCPE semantics and end-to-end evidence provenance.

## Migration matrix

| Original capability | Original implementation | Decision | New implementation | Verification |
|---|---|---|---|---|
| YAML/schema and registry integrity | `tools/validate_kb.py`; evidence tests | Adapt | OCPE strict package validator plus JSON Schemas under `validation/traceability/schemas/` | `ocpe validate ocpe/packages/disease-models --strict`; traceability unit tests |
| Physiological extreme bounds | `validation/evaluator.py`; `AdvancedValidationSuite` | Adapt | `tests/physiological/`; broad HR/MAP/CO and finite-state checks | `VAL-PHYS-BASELINE`, `VAL-PHYS-TILT` |
| Volume conservation | Legacy physiological level 2 | Re-implement for new equations | Instantaneous RHS and integrated three-compartment conservation tests | `VAL-MATH-CONSERVATION` |
| Orthostatic HR criterion | `PhysiologicalEvaluator.evaluate` | Adapt windows/outputs | Supine versus first-300-s upright HR rise; MAP separately required | `VAL-POTS-*`, `VAL-PHYS-TILT` |
| Initial pressure drop and compensation | `PhysiologicalEvaluator` | Adapt | Venous return, sympathetic state, HR, MAP and recovery direction tests | `VAL-PHYS-TILT`, `VAL-PHYS-RECOVERY` |
| Steady-state and perturbation tests | `test_steady_state_params.py`; `test_experimental_mode.py` | Re-implement | Resting baseline, tilt, exertion, repeated exertion and recovery protocols | Mathematical/physiological/phenotype layers |
| POTS phenotype comparisons | `test_orthostatic_response.py` | Adapt | Neuropathic, hyperadrenergic, hypovolemic, mixed YAML configurations | `VAL-POTS-NEUROPATHIC`, `VAL-POTS-HYPER`, `VAL-POTS-HYPO`, `VAL-POTS-MIXED` |
| Deterministic behavior | Seeded legacy engine tests | Preserve intent | Deterministic DOP853 runs, configuration SHA, solver metadata and approved regression fixtures | `VAL-REGRESSION`, `VAL-MATH-CONVERGENCE` |
| Strict expected failures | Two strict xfails in legacy orthostatic tests | Preserve as documented limitations | No silent xfail conversion; current failures/invalid sensitivity regimes remain in reports | Legacy audit, limitations, sensitivity report |
| Review sidecars and change accountability | `validation/sidecar_manifest.py`; ADR 0001 | Adapt | Stable scientific registries, implementation links, configuration hashes, Git history and change process | `VAL-TRACEABILITY`; scientific-change-management review |
| CI test + knowledge validation | Legacy `.github/workflows/ci.yml` | Adapt | Pull-request and extended workflows with explicit nonempty layer results | Workflow runs; seven-layer JSON/Markdown reports |
| Reference outputs/regression | Legacy fixtures and `results/*.npz` | Adapt selectively | Small reviewed summary fixtures and compact demonstration traces | `tests/regression/`; configuration hashes |
| Wearable agreement (ICC/CCC/Bland–Altman) | Legacy strategy level 4 and sensor studies | Defer; out of scope | Only explicit OCPE observation mapping is retained | Strict observation integration test; no agreement claim |
| Symptom scoring and circadian variation | `AdvancedValidationSuite`; time engine | Retire from current stage | M0/M1 literature placeholders only | `VAL-SCOPE-FUTURE` |
| Medication efficacy and hydration rules | `AdvancedValidationSuite` | Retire | No intervention/treatment model in this assignment | Scope review |
| Former ODE solver and virtual subjects | `simulation/`; `population.py` | Do not copy | New reduced-order equations in disease repository; no cohort generator | Architecture and scope tests |
| Large archived telemetry | `migration_archive/results/*.npz` | Do not migrate | Compact NPZ/JSON/PNG validation outputs only | Repository-size and scope review |

## Execution phases

1. **Historical reproduction — completed.** Run parent, authoritative refactor, and pinned current OCPE suites independently; record strict package/dependency checks and archived-test path limitations.
2. **Semantic integration — completed.** Add an OCPE disease package, adapter, unit-safe observation mapping, and strict validation.
3. **Scientific registries — completed.** Implement stable references, claims, mechanisms, equations, parameters, validation and simulation records, schemas, BibTeX, and strict audits.
4. **Numerical/scientific validation — verification controlled by the final report.** Implement conservation/convergence, physiology, phenotype, empirical, sensitivity, regression, and traceability checks. A registry entry alone is not marked passed.
5. **CI and reproducibility — verification controlled by workflow runs.** Run lint, unit/integration, mathematical and registry checks on pull requests; run extended scenarios and analyses in the extended workflow. Archive small reports.
6. **Handoff — final gate.** Record exact commits, dependencies, fixtures, failures, limitations, and migration deviations. Do not declare legacy capabilities migrated if they were intentionally deferred or have not executed.

## Compatibility deviations

- The former solver API (`Hc`, `pau`, carotid pressure, beat peaks) is not preserved because the new model has different states and beat-averaged outputs. Scientific metrics are preserved where meaningful; a source-level drop-in API is not claimed.
- Legacy fixed windows are replaced by protocol-relative windows.
- The new HR-rise metric uses upright peak during the declared comparison window; sustained versus transient response must be reported distinctly in future clinical benchmarking.
- OCPE upstream remains semantic infrastructure. SciPy integration in this repository is an explicit deviation forced by the upstream 0.1 scope, not a duplicated OCPE engine.
- No legacy synthetic telemetry or wearable agreement dataset is imported. This avoids unlicensed/provenance-poor fixture reuse and respects the exclusion of synthetic wearable dataset generation.

## Retirement conditions

Legacy numerical implementations need not be retired in their own historical destination; they remain in Git history. For this repository, a compatibility wrapper should be considered only if a downstream user demonstrates a real need and supplies old/new fixtures with provenance. No such wrapper is currently justified. Any future sensor-agreement migration requires actual reference measurements and a separately approved sensor-validation protocol.
