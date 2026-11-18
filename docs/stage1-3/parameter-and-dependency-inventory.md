# Stage 1.3 parameter and dependency inventory

## Scope and canonical sources

Model/package version is **0.4.0**. The canonical machine-readable inventory is `literature/parameter_registry.yaml`: 69 registered parameters, including the new dependent-venous coefficient. Executable defaults live in `src/ocpe_disease_models/models/shared/model.py`; phenotype overrides live under `phenotypes/`; declarative OCPE values and equations live in `ocpe/packages/disease-models/models.yaml`.

The 12-state layout and five conserved stressed-volume compartments are unchanged. Total healthy supine stressed volume remains 2550 mL. Compliance redistribution preserves the combined peripheral stressed volume at 1700 mL while changing its allocation from splanchnic/lower-limb/other-systemic 700/500/500 mL to 900/600/200 mL. Arterial and central-venous allocations remain 150 and 700 mL.

## Changed healthy-reference parameters

All selected values are **experimental computational assumptions**, not newly measured human constants.

| Parameter ID | Field | Stage 1.2 | Stage 1.3 | Units | Direct dependencies |
|---|---|---:|---:|---|---|
| PAR-SPLANCHNIC-VENOUS-COMPLIANCE | `splanchnic_venous_compliance` | 70 | 90 | mL/mmHg | EQ-CV-001; supine Vs and splanchnic pressure/flow |
| PAR-LOWER-LIMB-VENOUS-COMPLIANCE | `lower_limb_venous_compliance` | 50 | 60 | mL/mmHg | EQ-CV-001; supine Vl and lower-limb pressure/flow |
| PAR-OTHER-SYSTEMIC-VENOUS-COMPLIANCE | `other_systemic_venous_compliance` | 50 | 20 | mL/mmHg | EQ-CV-001; supine Vo and residual-bed capacity |
| PAR-DEPENDENT-VENOUS-STIFFENING | `dependent_venous_stiffening_mmHg_per_mL2` | 0 | 0.0001 | mmHg/mL² | EQ-CV-001; one-sided splanchnic/lower-limb elastance |
| PAR-SPLANCHNIC-HYDROSTATIC-HEIGHT | `splanchnic_hydrostatic_height_cm` | 7 | 13.3 | cm | EQ-ORT-001/002; splanchnic hydrostatic pressure |
| PAR-LOWER-LIMB-HYDROSTATIC-HEIGHT | `lower_limb_hydrostatic_height_cm` | 14 | 26.6 | cm | EQ-ORT-001/002; lower-limb hydrostatic pressure |
| PAR-OTHER-SYSTEMIC-HYDROSTATIC-HEIGHT | `other_systemic_hydrostatic_height_cm` | 11 | 4.5 | cm | EQ-ORT-001/002; residual-bed hydrostatic pressure |
| PAR-AORTIC-BAROREFLEX-WEIGHT | `aortic_baroreflex_weight` | 0.25 | 0.35 | dimensionless | EQ-AUT-001; paired with carotid weight |
| PAR-CAROTID-BAROREFLEX-WEIGHT | `carotid_baroreflex_weight` | 0.75 | 0.65 | dimensionless | EQ-AUT-001; paired with aortic weight |
| PAR-SPLANCHNIC-RESISTANCE-SYMPATHETIC-GAIN | `splanchnic_resistance_sympathetic_gain` | 0.8 | 0.45 | dimensionless | EQ-VASC-001; splanchnic arterial resistance |
| PAR-LOWER-LIMB-RESISTANCE-SYMPATHETIC-GAIN | `lower_limb_resistance_sympathetic_gain` | 0.8 | 0.45 | dimensionless | EQ-VASC-001; lower-limb arterial resistance |
| PAR-OTHER-SYSTEMIC-RESISTANCE-SYMPATHETIC-GAIN | `other_systemic_resistance_sympathetic_gain` | 0.8 | 0.45 | dimensionless | EQ-VASC-001; residual-bed arterial resistance |
| PAR-CONTRACTILITY-SYMPATHETIC-GAIN | `contractility_sympathetic_gain` | 0.25 | 0.10 | dimensionless | Stroke-volume constitutive path |
| PAR-HEART-RATE-CARDIAC-SYMPATHETIC-GAIN | `heart_rate_cardiac_sympathetic_gain` | 20 | 13.6 | bpm | EQ-AUT-003; cardiac-sympathetic chronotropy |
| PAR-HEART-RATE-VAGAL-GAIN | `heart_rate_vagal_gain` | 20 | 13.6 | bpm | EQ-AUT-003; vagal chronotropy |
| PAR-CEREBRAL-AUTOREGULATION-RESIDUAL-SLOPE | `cerebral_autoregulation_residual_slope` | 0.40 | 0.25 | dimensionless | EQ-CBF-001; pressure-only cerebral target |

The baroreflex weights remain paired and sum to one. Sensitivity perturbations preserve that constraint rather than varying one weight independently.

## New constitutive term

For each dependent bed \(i\in\{s,l\}\),

\[
P_i=\frac{V_i}{C_i}+k_d\max(0,V_i-P_{i,0}C_i f_{bv})^2.
\]

The threshold is the scaled supine stressed volume, so the term is exactly zero at the healthy supine fixed point and \(k_d=0\) recovers the Stage 1.2 linear law. The term changes pressure for a given volume; it does not add/remove volume or change any flow-conservation derivative.

The executable coefficient has units mmHg/mL². Because the pinned OCPE unit registry has no pressure-per-volume-squared UCUM unit, the declarative package declares the numerically equivalent `K_d` in mmHg/mL and divides squared excess volume by an explicit 1 mL reference volume. This is a units representation, not a second parameter.

## Phenotype-specific inventory

| Configuration | Stage 1.3 value | Interpretation |
|---|---|---|
| Neuropathic POTS | splanchnic/lower-limb resistance sympathetic gains 0.34 | Impaired peripheral compensation assumption; range exception remains disclosed |
| hEDS vascular | lower-limb venous compliance 70 mL/mmHg | Exploratory contrast with healthy 60; not a measured hEDS coefficient |
| hEDS/ME-CFS comorbid | lower-limb venous compliance 70 mL/mmHg | Same exploratory assumption under composition |
| Eight disease configurations | no splanchnic/lower-limb height override | Common healthy anatomical geometry is inherited |

The removed overrides apply to neuropathic, hyperadrenergic, hypovolemic, and mixed POTS; both hEDS configurations; ME/CFS PEM; and Long-COVID-autonomic. Other phenotype mechanisms—blood-volume factor, chronotropic calibration, hyperadrenergic drive, cerebral impairment, PEM, and metabolic extraction—remain independently declared.

## Unchanged structural and scientific dependencies

- Five volume states: arterial, central venous, splanchnic venous, lower-limb venous, and other-systemic venous.
- Three autonomic states: cardiac sympathetic, vascular sympathetic, and vagal.
- Exertional load, delayed stress, PEM severity, and cerebral-flow index complete the 12 states.
- Separate aortic and carotid sensors, explicit `0.7356 × height_cm × sin(angle)` geometry, preload-dependent SV, and independent declared-CO₂ cerebral modulation remain.
- Fixed effective cerebral outflow pressure remains 5 mmHg; it is neither resolved ICP nor thoracic CVP.
- Solver settings, validation bands, POTS/Long-COVID sustained-HR thresholds, and regression tolerance classes are unchanged.
- `validation/validation_registry.yaml`, `literature/equation_registry.yaml`, and `simulations/simulation_registry.yaml` link the changed fields to equations, evidence claims, tests, and fresh outputs.

See `docs/stage1-3/corrected-causal-dependency-graph.md` for direction of causation and `evidence-to-parameter-traceability.md` for evidence classification.
