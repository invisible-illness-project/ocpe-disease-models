# Stage 1.3 technical handoff and downstream readiness

- Current record date: 2026-11-18
- Target branch: `research/initial-disease-modeling-framework`
- Model/package version: **0.4.0**
- Overall scientific readiness: **PARTIAL — exploratory deterministic research scenarios only**
- Model CURIE: `ocpe:disease-models/shared-physiology`
- Stage 1.2 baseline source: `e48110e`
- Stage 1.1 historical comparator: `f85360d8337144e118eb0d2aef317fd1b949b3dd`
- Pinned OCPE commit: `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`
- Current execution metadata: `validation/reports/validation-report.json` and `validation/reproducibility.json`

This is computational research software, not a clinically validated model, diagnostic device, treatment system, synthetic wearable dataset, or flare predictor. **Stage 2 dataset generation and Stage 3 prediction have not begun.**

## A. Executive summary

Stage 1.3 addresses the Stage 1.2 residual-bed, dependent-pooling, pressure-defense, and 60° CO limitations while removing unsupported phenotype-specific anatomy. It does so through an explicit constitutive revision rather than by widening criteria or adding states.

Before modification, fresh detached-worktree executions reproduced every reported Stage 1.2 numerical result: 957 numeric fields and 277 non-numeric identifiers/statuses matched, with maximum absolute numeric difference 7.25 × 10⁻¹⁵. The audit-named `6034d11…` and `2d1283f` Git objects are unavailable and are disclosed rather than silently replaced in provenance.

Stage 1.3 healthy 70° outcomes are:

- sustained HR rise 13.298 bpm;
- end heart-level MAP 102.253 mmHg from 100 mmHg supine;
- caudal pooling 469.395 mL;
- residual-systemic volume change −17.931 mL;
- central-venous volume change −454.845 mL; and
- end-CFI reduction 4.961%.

All four direct 60° CO/SV group comparisons are within their preserved bands. All four 70° rows are also within the reused bands, but they are explicitly **extrapolated model-specific criteria**, not direct 70° experimental replication. All four POTS and Long-COVID-autonomic sustained-HR scenario criteria pass; ME/CFS CFI remains within its unchanged 15–35% band.

These are calibrated scenario outcomes. They do not establish independent external validation, scientific readiness, or clinical validity.

## B. Stage 1.3 report set

Current reports are under `docs/stage1-3/`:

- `baseline-reproduction.md` — exhaustive Stage 1.2/Stage 1.1 numerical reproduction and audit discrepancies;
- `parameter-and-dependency-inventory.md` — all changed executable and phenotype parameters, units, and dependencies;
- `corrected-causal-dependency-graph.md` — feedback structure and corrected common-anatomy/elastance relationships;
- `sensitivity-and-identifiability.md` — 96 local, 27 grid, and 3 chronotropic-split analyses;
- `evidence-to-parameter-traceability.md` — evidence classes and assumption status for every changed parameter;
- `implementation-and-validation.md` — isolated/combined experiments, phenotype outcomes, and execution entry points;
- `scientific-decision-log.md` — accepted/rejected decisions and downstream effects; and
- `readiness-assessment.md` — current readiness boundaries and remaining limitations.

Machine-readable evidence is under `validation/stage1-3/`, `validation/sensitivity/`, `validation/reports/`, and `validation/traceability/audit/`. Historical `docs/stage1-2/`, `validation/stage1-2/`, `docs/stage1-1/`, and `validation/stage1-1/` records remain unchanged.

## C. Implemented architecture

The current implementation retains 12 states:

1. arterial stressed volume;
2. central-venous stressed volume/preload proxy;
3. splanchnic-venous stressed volume;
4. lower-limb-venous stressed volume;
5. other-systemic venous stressed volume;
6. cardiac-sympathetic state;
7. vascular-sympathetic state;
8. vagal state;
9. exertional load;
10. delayed stress;
11. PEM severity; and
12. normalized cerebral-flow index.

The five volume derivatives telescope exactly:

`dVa/dt + dVc/dt + dVs/dt + dVl/dt + dVo/dt = 0`.

Healthy supine stressed volume remains 2550 mL. Its five-compartment allocation is 150/700/900/600/200 mL. Compliance redistribution preserves the combined peripheral allocation at 1700 mL while changing its internal distribution.

For splanchnic and lower-limb beds, Stage 1.3 uses:

`P_i = V_i/C_i + k_d × max(0, V_i − P_i0 × C_i × blood_volume_factor)^2`.

The one-sided term is zero at the supine reference and does not alter any volume derivative. `k_d=0` recovers Stage 1.2. Its quadratic form and 0.0001 mmHg/mL² value are high-uncertainty modeling assumptions, not measured tissue properties.

The pinned OCPE unit registry lacks pressure-per-volume-squared. The declarative package therefore uses `K_d` in mmHg/mL and an explicit 1 mL reference-volume divisor; this is dimensionally equivalent to the executable law and does not introduce a second parameter.

Posture remains explicit `tilt_angle_deg`, with hydrostatic corrections `0.7356 × height_cm × sin(angle)`. Healthy/common dependent heights are 13.3/26.6/4.5 cm. Eight disease configurations no longer override splanchnic/lower-limb anatomy. Aortic, carotid, and brain sites remain separate.

Aortic/carotid weights are 0.35/0.65 and sum to one. Cardiac sympathetic activity controls HR/contractility, vascular sympathetic activity controls regional resistances, and vagal activity separately controls HR. The fixed effective cerebral outflow pressure remains 5 mmHg. Declared ETCO₂ modulates CFI independently; tilt never infers hypocapnia.

There are no disease-specific conditional branches in shared equations. Disease YAML files supply registered parameters; protocol YAML files independently declare posture, exertion, muscle inputs, and ETCO₂.

## D. Scientific decision and downstream effects

Each mechanism was executed independently before combination. Geometry alone caused excessive output loss under Stage 1.2 compensation; dependent elastance alone reduced pooling and CO loss; vascular and cardiac changes had distinct, non-additive effects. Full results are in `validation/stage1-3/scientific-comparison-matrix.md`.

The audit linear proposal was rejected: its fresh combined run produced end MAP 52.838 mmHg and 60° CO/SV reductions of 52.679/60.377%. The final nonlinear combination is a separate executed row and remains within the preserved comparisons.

Neuropathic-POTS peripheral gains are 0.34 versus healthy 0.45; the range exception is disclosed. Both hEDS configurations use exploratory lower-limb compliance 70 mL/mmHg versus healthy 60. Neither is a measured disease coefficient.

The new structure improves selected numerical outputs but adds structural uncertainty. It also changes every affected phenotype output through shared anatomy and constitutive pathways. Consequently, downstream users must not mix Stage 1.2 traces with Stage 1.3 traces or interpret cross-version differences as biological discoveries.

## E. Entry points and reproducible outputs

Primary entry points:

- `scripts/simulate.py` — one configured run;
- `scripts/run_examples.py` — six demonstration groups/16 persisted runs;
- `scripts/run_sensitivity.py` — local, grid, and chronotropic-split analyses;
- `scripts/run_stage1_3_validation.py` — isolated/combined mechanism and current scientific matrix;
- `scripts/run_validation.py --no-analysis` — independent seven-layer reporting without recomputing sensitivity;
- `scripts/audit_traceability.py --root . --strict --deterministic` — registry/provenance audit; and
- `python -m ocpe validate ocpe/packages/disease-models --strict` — declarative package validation.

Each persisted run records resolved parameters, protocol, configuration SHA-256, model/OCPE versions, dependency versions, and DOP853 settings. NPZ traces contain the 12 states and derived outputs; JSON results contain metadata/summaries; OCPE observations contain sparse mapped values, not waveforms.

The simulation registry contains 19 protocols and 12 current simulation records. Generated outputs are small validation artifacts, not patient cohorts or machine-learning datasets.

## F. Validation and interpretation

Current complete test and seven-layer results are recorded in `validation/reports/validation-report.json` / `.md` and `validation/reproducibility.json`. The focused Stage 1.3 fidelity/regression selection passed 38 tests; the sensitivity layer passed 15 tests. Strict traceability reports zero errors, warnings, and infos; strict OCPE reports zero errors and warnings for `disease-models@0.4.0`.

The 29 current validation-registry records are PASS. This does not erase the separate readiness assessment: PASS means the declared computational or model-specific check passed. It does not prove equation structure, mechanism truth, generalization, or clinical validity.

The regression fixture contains 16 runs and a Stage 1.3 change record explaining mechanisms, evidence, expected directions, and the rejected linear proposal. Tolerances and scientific criteria were not changed.

## G. Sensitivity and identifiability

Fresh exports contain:

- 96 local rows, including every changed healthy parameter and paired baroreflex-weight perturbations;
- 27 deterministic assumption-grid rows; and
- 3 fixed-total chronotropic-split rows.

Sustained HR/MAP do not identify the cardiac-sympathetic/vagal split. Baroreflex weights are coupled; compliance and elastance have interacting/opposing effects; geometry and blood volume are not separately identified by current outputs. Local sensitivity and deterministic grids are not global uncertainty, patient identification, or population inference.

Important margins remain narrow: direct 60° CO agreement is about 0.081 percentage points above the lower band edge, and neuropathic-POTS sustained HR exceeds its criterion by about 0.093 bpm.

## H. Scientific confidence and readiness

Confidence is strongest in software integrity, exact conservation, fixed-point accounting, deterministic reproducibility, and explicit provenance. It is weaker in constitutive structure, absolute parameter values, disease heterogeneity, and generalization.

Current appropriate use is limited to exploratory deterministic research scenarios, mechanism hypothesis comparison, and planning independent evaluation. Current inappropriate uses include diagnosis, treatment, severity ranking, patient-specific inference, population estimation, and unrestricted synthetic-data ground truth.

Material limitations include:

- unvalidated quadratic elastance and calibration overlap;
- residual healthy MAP rise and absent cardiopulmonary baroreflex pathway;
- simplified autonomic/catecholamine physiology;
- unmeasured hEDS and neuropathic parameters;
- fixed effective cerebral outflow pressure and bounded declared ETCO₂;
- phenomenological PEM and its prior onset-window caveat;
- local rather than global/patient identifiability analysis; and
- no independent prospective or held-out cohort validation.

## I. Stage 2 and Stage 3 boundary

A separately approved Stage 2 project could use the simulator as a deterministic source of latent beat-averaged states, subject to the limitations above. No ECG, PPG, HRV, respiratory, temperature, electrodermal, or accelerometry waveform is generated. There is no sensor error/artifact model, cohort design, governance process, reference measurement, or wearable agreement analysis.

Accordingly, the repository is **ready for reviewed Stage 2 planning, not automatic Stage 2 execution or clinically meaningful synthetic wearable data**. Any downstream plan must preserve calibration overlap, the unvalidated elastance structure, narrow acceptance margins, and PEM caveats; deterministic scenarios must not become diagnostic ground-truth labels.

Stage 3 flare prediction remains excluded. File-format compatibility is not readiness for prediction.

## J. Traceability and operations

The implemented chain is:

`reference → evidence claim → mechanism → equation → parameter → implementation → validation test → simulation output`.

Current audited registries contain 69 references, 41 evidence claims, 24 mechanisms, 22 equations, 69 parameters, 29 validation records, 19 protocols, and 12 simulation records. Record integrity does not establish mechanism truth.

Scientific changes follow `docs/scientific-change-management.md`. Equation, parameter, evidence, phenotype, fixture, and maturity changes require linked provenance and review. Rollback should use reviewed Git reverts. Any later source/configuration change requires a fresh validation cycle.

The reproducibility record distinguishes the tested source/configuration commit from any subsequent validation-record commit that adds generated reports and outputs. It never claims that a later commit was tested before it existed.

Upstream OCPE remains pinned and unmodified. No credential, token, private key, or temporary secret belongs in the repository, reports, or patch. CI uses read-only contents permission and requires no secrets. Local results do not substitute for successful remote Python 3.11/3.12 matrix runs.
