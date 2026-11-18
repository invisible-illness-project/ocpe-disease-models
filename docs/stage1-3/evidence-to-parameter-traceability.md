# Stage 1.3 evidence-to-parameter traceability matrix

## Evidence policy

No Stage 1.3 numerical value is promoted to an authoritative human measurement. The audit proposal was treated as a hypothesis. Evidence claims support mechanisms and directions; computational values remain calibrated or exploratory assumptions unless explicitly stated otherwise.

Comparison classes used in Stage 1.3 are:

- **Direct experimental-angle replication:** the healthy 60° CO/SV comparisons use the same angle as the cited Zaidi group experiment. This remains group-level plausibility with calibration overlap, not patient fitting or independent external validation.
- **Interpolation:** a value or response is estimated within an existing supported range or between declared model settings. Interpolation does not make a coefficient measured.
- **Extrapolation:** a relationship or range is applied outside its direct experimental setting. Reusing the 60°-informed CO/SV bands at 70° is explicitly extrapolated.
- **Model-specific acceptance criterion:** a repository-defined numerical or structural check, such as residual-volume change magnitude, MAP bounds, conservation, or the POTS sustained-HR scenario threshold. It is not an experimental measurement.
- **Structural modeling assumption:** a selected equation form or parameterization requiring independent validation. The one-sided quadratic dependent-elastance law belongs here.

## Healthy shared-model changes

| Parameter/change | Evidence and registry links | Evidence class | Value/status and downstream rationale |
|---|---|---|---|
| Splanchnic compliance 70→90 mL/mmHg | CLM-CV-VENOUS-RETURN; CLM-ORTHO-GRADED-TILT; EQ-CV-001; VAL-SENSITIVITY | Calibrated interpolation/model-specific assumption | Redistributes supine stressed volume and changes splanchnic pressure/flow; no direct measured coefficient claimed |
| Lower-limb compliance 50→60 mL/mmHg | Same claims; EQ-CV-001; VAL-PHYS-GRADED-TILT | Calibrated interpolation/model-specific assumption | Preserves total peripheral stressed volume jointly with other compliance changes; alters lower-limb pooling |
| Other-systemic compliance 50→20 mL/mmHg | CLM-CV-VENOUS-RETURN; EQ-CV-001 | Model-specific calibration | Reduces residual-bed supine allocation/capacitance; addresses excessive Stage 1.2 residual accumulation |
| Dependent stiffening 0→0.0001 mmHg/mL² | CLM-CV-VENOUS-RETURN; CLM-ORTHO-GRADED-TILT; EQ-CV-001; VAL-MATH-CONSERVATION; VAL-SENSITIVITY | **High-uncertainty structural extrapolation** | Activates only above scaled supine Vs/Vl; limits dependent overfilling without changing conservation; neither coefficient nor quadratic form is tissue-measured |
| Splanchnic height 7→13.3 cm | CLM-ORTHO-HYDROSTATIC; EQ-ORT-001/002 | Effective-geometry interpolation/calibration | Changes hydrostatic pressure through 0.7356 h sin(angle); not a measured anatomical length |
| Lower-limb height 14→26.6 cm | Same | Effective-geometry interpolation/calibration | Increases lower-limb gravitational loading; common across phenotypes |
| Other-systemic height 11→4.5 cm | Same | Effective-geometry calibration | Reduces unsupported residual-bed pooling drive; not an anatomical severity measure |
| Aortic/carotid weights 0.25/0.75→0.35/0.65 | CLM-AUT-DUAL-SENSOR; EQ-AUT-001; paired sensitivity | Model-specific interpolation | Preserves separate sensors and unit weight sum; relative weighting is not uniquely identified |
| Three healthy vascular sympathetic gains 0.8→0.45 | CLM-AUT-SYMPATHETIC-PATHWAYS; EQ-VASC-001 | Model-specific calibration | Reduces regional resistance compensation; evaluated independently of cardiac changes |
| Contractility sympathetic gain 0.25→0.10 | CLM-CV-HEMODYNAMICS; CLM-AUT-SYMPATHETIC-PATHWAYS | Model-specific calibration | Reduces cardiac-sympathetic SV support; no disease-specific claim |
| Cardiac-sympathetic/vagal chronotropic gains 20/20→13.6/13.6 bpm | CLM-AUT-SYMPATHETIC-PATHWAYS; CLM-AUT-VAGAL-FAST; EQ-AUT-003 | Model-specific calibration | Changes compensation without altering effector time constants; fixed-total split remains non-identified |
| Cerebral residual slope 0.40→0.25 | CLM-CBF-AUTOREG-DYNAMIC; EQ-CBF-001 | Interpolation within existing supported range; calibration overlap | Changes pressure autoregulation only; independent CO₂ pathway and fixed effective outflow pressure preserved |

## Phenotype changes

| Configuration/change | Evidence and validation | Classification | Limitation |
|---|---|---|---|
| Remove splanchnic/lower-limb height overrides from four POTS, two hEDS, ME/CFS, and Long-COVID-autonomic configurations | CLM-ORTHO-HYDROSTATIC; common-anatomy tests in `test_stage1_3_orthostatic_fidelity.py` | Structural correction | Anatomy is shared; disease mechanisms remain in physiological parameters. No anatomical equivalence between patients is claimed |
| Neuropathic-POTS splanchnic/lower-limb sympathetic gains 0.35→0.34 | CLM-POTS-PHENOTYPES; CLM-POTS-BAROREFLEX; VAL-POTS-NEUROPATHIC | Model-specific calibration | Retains impaired compensation versus healthy 0.45; range exception is explicit; sustained-HR margin is narrow |
| hEDS lower-limb compliance 58.333→70 mL/mmHg while healthy moves 50→60 | CLM-EDS-VASCULAR; CLM-EDS-OI; VAL-EDS-DIRECTION; VAL-UNCERTAINTY | Exploratory extrapolation | Neither healthy nor hEDS value is a measured population coefficient; deterministic grid is not patient variability |
| Preserve hyperadrenergic, hypovolemic, mixed-POTS, PEM, metabolic, and cerebral disease mechanisms | Existing claims and phenotype tests | Unchanged model assumptions | Common anatomy does not validate these mechanisms or their subtype specificity |

## Equation-to-output traceability

| Output or acceptance check | Equation/parameter pathway | Classification of conclusion |
|---|---|---|
| Five-volume drift | EQ-CV-002/003/004/005 and telescoping volume RHS | Mathematical invariant; not empirical validation |
| Supine fixed points | EQ-CV-001 through autonomic/cerebral equilibrium equations | Mathematical/model-specific check |
| 60° CO/SV at 120/300 s | EQ-ORT-001/002 + EQ-CV-001 + compensation pathways vs REF-ZAIDI-2000 | Direct experimental-angle group comparison; calibration overlap |
| 70° CO/SV at 120/300 s | Same pathways; 60°-informed published ranges reused | **Extrapolated model-specific acceptance criterion** |
| Healthy pooling, residual ΔV, MAP, and CFI | Regional constitutive/flow/autonomic/cerebral pathways | Model-specific acceptance/plausibility checks |
| POTS/Long-COVID sustained HR ≥30 bpm | Phenotype parameters + autonomic/CO pathways | Model-specific consensus-scenario criterion; not diagnostic accuracy |
| Sensitivity and chronotropic split | Declared parameter perturbations | Structural sensitivity/non-identifiability analysis; not population inference |

## Fresh evidence artifacts

- Baseline reproduction: `validation/stage1-3/baseline-reproduction.json` and `docs/stage1-3/baseline-reproduction.md`.
- Isolated and combined mechanisms: `validation/stage1-3/scientific-comparison-matrix.json` and `.md`.
- Parameter/equation links: `literature/parameter_registry.yaml` and `literature/equation_registry.yaml`.
- Validation links: `validation/validation_registry.yaml`.
- Simulation links: `simulations/simulation_registry.yaml`.
- Sensitivity/identifiability: `validation/sensitivity/` and `docs/stage1-3/sensitivity-and-identifiability.md`.

A registry chain establishes traceability, not truth. Numerical agreement cannot upgrade an assumed coefficient to an evidence-backed measurement.
