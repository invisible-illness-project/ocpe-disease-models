# Stage 1.3 sensitivity and identifiability report

## Executed scope

All analyses are deterministic model perturbations, not synthetic patients, probability distributions, population estimates, or clinical validation.

| Analysis | Fresh rows | Coverage |
|---|---:|---|
| Local sensitivity | 96 | 43 neuropathic-POTS rows; 50 healthy-reference rows; 3 hEDS rows |
| Healthy local breakdown | 50 | 33 head-up-tilt; 5 CO₂; 9 rhythmic-muscle; 3 sustained-contraction rows |
| Assumption-uncertainty grid | 27 | 9 hEDS; 9 ME/CFS; 9 healthy cerebral/CO₂ scenarios |
| Fixed-total chronotropic split | 3 | Cardiac-sympathetic fractions 0, 0.5, and 1 |
| Central-difference fixtures | 6 parameters | 60° HR/MAP derivatives for geometry, compensation, blood volume, compliance, and elastance |

Artifacts are `validation/sensitivity/local_sensitivity.json`, `uncertainty_grid.json`, `chronotropic_split.json`, their CSV exports, `sensitivity-report.md`, and `validation/fixtures/sensitivity_ranges.json`. Every row retains its configuration hash and solver metadata.

A separate four-point healthy tilt-ranking test uses lower-limb resistance-gain endpoints 0.35 and 0.8. This deliberately spans reduced compensation through the Stage 1.2 nominal and is asymmetric around the Stage 1.3 nominal 0.45. It is a deterministic legacy-spanning ranking check, not a centered statistical uncertainty interval, and is not part of the 27-row exported grid.

## Local healthy orthostatic sensitivity

Normalized sensitivity is the centered output change divided by the fractional parameter span and, where defined, absolute baseline output. It is a local response measure, not a regression coefficient or causal effect estimate. The table reports sustained HR rise and final MAP for every changed healthy parameter.

| Parameter | Sustained-HR normalized sensitivity | Final-MAP normalized sensitivity |
|---|---:|---:|
| Splanchnic venous compliance | 0.03620 | −0.03109 |
| Lower-limb venous compliance | 0.05634 | −0.04798 |
| Other-systemic venous compliance | −0.01516 | 0.01321 |
| Dependent-venous stiffening | −0.14510 | 0.13880 |
| Splanchnic resistance sympathetic gain | −0.03408 | 0.02972 |
| Lower-limb resistance sympathetic gain | −0.02612 | 0.02278 |
| Other-systemic resistance sympathetic gain | −0.05804 | 0.05060 |
| Splanchnic hydrostatic height | 0.15360 | −0.12980 |
| Lower-limb hydrostatic height | 0.17490 | −0.14750 |
| Other-systemic hydrostatic height | 0.04186 | −0.03644 |
| Aortic baroreflex weight, paired perturbation | −0.05296 | −0.01314 |
| Carotid baroreflex weight, paired perturbation | 0.09887 | 0.02453 |
| Cardiac-sympathetic chronotropic gain | 0.45930 | 0.03478 |
| Vagal chronotropic gain | 0.45930 | 0.03478 |
| Contractility sympathetic gain | −0.02335 | 0.02033 |
| Cerebral autoregulation residual slope | approximately 0 for HR/MAP | approximately 0 for HR/MAP |

The cerebral residual slope is instead influential in the cerebral pathway: changing it alters the pressure-autoregulation target without directly changing systemic HR or MAP. Declared CO₂ parameters affect cerebral outputs only under protocols that actually change ETCO₂; zero or undefined tilt sensitivities are expected, not evidence that CO₂ is physiologically unimportant.

At 60°, the central-difference fixture gives dependent-elastance derivatives of approximately −19,297 bpm per (mmHg/mL²) for HR and +141,910 mmHg per (mmHg/mL²) for MAP. These large raw derivatives reflect the tiny coefficient scale; the normalized local measure is more interpretable. The same fixture retains blood-volume-factor MAP sensitivity of approximately 104.483 mmHg per unit factor, demonstrating that absolute pressure remains strongly blood-volume dependent.

## Mechanism isolation and interaction

Local derivatives do not replace the finite, isolated mechanism experiments. Fresh results at 120 s upright include:

| Isolated change from Stage 1.2 | Sustained HR rise (bpm) | End MAP (mmHg) | 60° CO reduction (%) |
|---|---:|---:|---:|
| Compliance redistribution | 14.733 | 109.188 | 14.915 |
| Common anatomical geometry | 20.000 | 82.243 | 36.278 |
| Baroreflex weighting | 14.816 | 107.424 | 16.230 |
| Vascular compensation gains | 19.115 | 105.383 | 12.406 |
| Cardiac compensation | 12.072 | 107.318 | 19.453 |
| Dependent-venous elastance | 12.276 | 110.101 | 12.043 |
| Cerebral autoregulation | 15.467 | 108.846 | 15.801 |

The isolated effects are non-additive. In particular, geometry-only and elastance-only changes have qualitatively different effects from their final combined configuration. The audit linear proposal without elastance produces 52.679% 60° CO loss and 52.838 mmHg end MAP, so it is not a valid approximation of the final nonlinear combination. Full 60°/70° CO/SV, pooling, residual-volume, central-volume, and CFI outcomes are in `validation/stage1-3/scientific-comparison-matrix.json`.

## Deterministic grid findings

- hEDS compliance/geometry scenarios produce sustained HR rises of 21.82–24.32 bpm and final MAP of 106.7–107.5 mmHg. No grid scenario falls below the 70 mmHg MAP screening threshold. This does not validate the assumed hEDS compliance mechanism.
- ME/CFS delay/onset scenarios produce PEM peaks of 0.05566–0.1207 and final functional capacity of 0.7841–0.7915. These are phenomenological scenario ranges, not prevalence or severity distributions.
- Healthy cerebral CO₂ reactivity/clipping scenarios span CFI 0.6333–0.7838 at declared 30 mmHg ETCO₂. They do not identify patient reactivity or convert ETCO₂ into PaCO₂.

## Identifiability assessment

### Structurally constrained or non-identified combinations

1. **Baroreflex weights:** only their relative contribution to a weighted error is observable in the present model, and their sum is constrained to one. The analysis therefore uses paired perturbations. Separate aortic/carotid gains cannot be inferred from the current healthy CO/SV/HR/MAP outputs.
2. **Chronotropic split:** with total gain fixed at 27.2 bpm, cardiac-sympathetic fractions 0, 0.5, and 1 all yield sustained neuropathic-POTS HR rise 30.09 bpm and final MAP 107.3 mmHg. Peak HR differs (31.75, 30.91, and 30.62 bpm), so transient data carry some information, but sustained HR/MAP alone do not identify the split.
3. **Compliance and elastance:** both alter dependent pressure and pooling and have opposing effects on several outputs. The present group-level CO/SV bands do not uniquely identify their separate values or the quadratic equation form.
4. **Geometry and blood volume:** hydrostatic heights and blood-volume factor both influence venous return, HR, and MAP. Effective heights are not measured anatomical lengths; their values are not patient-identifiable from these scenarios.
5. **Compensation gains:** cardiac and vascular gains interact through pressure feedback. Matching one healthy tilt response does not establish unique gains or disease-specific mechanisms.
6. **Cerebral residual slope and CO₂ parameters:** separable declared protocols establish computational distinguishability, not human parameter identification. Calibration overlap remains.

### What has and has not been established

Established: local directional sensitivity, finite deterministic grid responses, exact fixed-total split behavior, configuration traceability, and interaction among mechanisms.

Not established: global sensitivity rankings, practical identifiability from noisy data, parameter posterior distributions, patient-specific estimates, population variability, equation-structure selection, or clinical validity. No Fisher-information, profile-likelihood, Bayesian, or held-out patient analysis was performed; none is claimed.

## Consequence for readiness

The final configuration remains a high-uncertainty calibrated structure. In particular, 60° CO agreement lies only about 0.081 percentage points above the lower band edge, and neuropathic-POTS sustained HR exceeds 30 bpm by only about 0.093 bpm. These narrow margins make sensitivity and independent validation more important, not less. Passing the present deterministic checks cannot justify unrestricted synthetic-data generation or a higher clinical maturity claim.
