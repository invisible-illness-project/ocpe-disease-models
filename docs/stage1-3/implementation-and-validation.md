# Stage 1.3 implementation and validation

## Implementation decision

Stage 1.3 is implemented as model/package **0.4.0**. It preserves the 12-state ODE, five conserved stressed-volume compartments, explicit angle geometry, separate aortic/carotid sensors, three autonomic effectors, preload-dependent SV, and independent cerebral pressure/declared-CO₂ pathways.

The Stage 1.3 audit values were not blindly adopted. Each mechanism group was executed independently from the reproduced Stage 1.2 healthy configuration before any combined decision. The audit linear proposal and final nonlinear combination remain separate, reproducible rows.

## Constitutive and configuration changes

1. Peripheral compliances are 90/60/20 mL/mmHg for splanchnic/lower-limb/other-systemic beds.
2. Splanchnic and lower-limb pressure include a one-sided quadratic excess-volume term with `k_d = 0.0001 mmHg/mL²`; zero recovers Stage 1.2.
3. Common effective anatomy is 13.3/26.6/4.5 cm. Eight phenotype YAML files no longer override splanchnic/lower-limb heights.
4. Aortic/carotid weights are 0.35/0.65; healthy vascular gains are 0.45; contractility is 0.10; both chronotropic gains are 13.6 bpm; cerebral residual slope is 0.25.
5. Neuropathic-POTS splanchnic/lower-limb gains are 0.34; both hEDS configurations use lower-limb compliance 70 mL/mmHg.
6. Executable, phenotype, declarative-OCPE, equation, parameter, simulation, validation, sensitivity, and fixture records were synchronized. Version references are 0.4.0.

No scientific criterion, regression tolerance, solver tolerance, state dimension, or volume-conservation equation was widened or disabled.

## Isolated and combined healthy experiments

CO/SV entries are reductions at 120 s upright. All rows begin from the reproduced Stage 1.2 configuration and use fresh DOP853 simulations.

| Experiment | Sustained HR rise (bpm) | End MAP (mmHg) | Caudal pooling (mL) | Residual ΔV (mL) | 60° CO/SV (%) | 70° CO/SV (%) |
|---|---:|---:|---:|---:|---:|---:|
| Stage 1.2 reproduced | 15.467 | 108.846 | 302.962 | +162.152 | 15.801 / 29.215 | 18.732 / 33.439 |
| Compliance only | 14.733 | 109.188 | 386.656 | +67.461 | 14.915 / 27.951 | 17.632 / 31.956 |
| Common geometry only | 20.000 | 82.243 | 771.254 | −155.401 | 36.278 / 50.437 | 44.277 / 56.660 |
| Baroreflex weighting only | 14.816 | 107.424 | 302.719 | +162.036 | 16.230 / 29.070 | 19.133 / 33.259 |
| Vascular gains only | 19.115 | 105.383 | 313.407 | +166.391 | 12.406 / 29.550 | 15.670 / 33.759 |
| Cardiac compensation only | 12.072 | 107.318 | 293.145 | +158.111 | 19.453 / 30.012 | 22.660 / 34.036 |
| Dependent elastance only | 12.276 | 110.101 | 220.454 | +192.106 | 12.043 / 23.737 | 13.981 / 26.815 |
| Cerebral autoregulation only | 15.467 | 108.846 | 302.962 | +162.152 | 15.801 / 29.215 | 18.732 / 33.439 |
| Audit linear proposal combined | 13.600 | 52.838 | 773.537 | −83.599 | 52.679 / 60.377 | 62.013 / 68.193 |
| **Stage 1.3 nonlinear combined** | **13.298** | **102.253** | **469.395** | **−17.931** | **17.081 / 29.677** | **19.816 / 32.617** |

The linear proposal fails the preserved orthostatic comparisons and pressure floor; it was rejected. The nonlinear term was introduced to address dependent overfilling without adding further compensatory gain. Its form and coefficient remain high-uncertainty modeling assumptions, not experimentally identified tissue properties.

## Current healthy and phenotype outcomes

| Scenario | Sustained HR rise (bpm) | End/upright-end MAP (mmHg) | End-CFI reduction (%) | Interpretation |
|---|---:|---:|---:|---|
| Healthy 30° | 6.592 | 103.860 | 1.678 | Model-specific graded response |
| Healthy 45° | 9.945 | 104.727 | 2.647 | Model-specific graded response |
| Healthy 60° | 12.538 | 103.945 | 3.896 | Direct-angle CO/SV comparison reported separately |
| Healthy 70° | 13.298 | 102.253 | 4.961 | CFI calibration-era agreement; 70° CO/SV bands are extrapolated |
| Neuropathic POTS | 30.093 | 107.320 | 3.279 | Passes unchanged ≥30 bpm scenario criterion by 0.093 bpm |
| Hyperadrenergic POTS | 33.430 | 109.673 | 2.547 | Scenario criterion only; catecholamine pathway remains simplified |
| Hypovolemic POTS | 33.690 | 95.612 | 5.287 | Scenario criterion only |
| Mixed POTS | 33.396 | 102.391 | 3.869 | Scenario criterion only |
| Long-COVID-autonomic | 32.368 | 108.150 | 10.308 | Subgroup scenario only |
| Long-COVID-exertional | 13.298 | 102.253 | 4.961 | No POTS-like chronotropic override |
| hEDS vascular | 23.118 | 107.146 | 3.334 | Exploratory assumed-compliance scenario |
| ME/CFS PEM | 21.726 | 105.916 | 24.538 | CFI within unchanged 15–35% scenario band |

The final healthy central-venous volume change is −454.844876 mL. Five-volume conservation is retained; volume redistribution must not be mistaken for blood creation or loss.

## Empirical comparison classification

| Protocol | CO/SV rows | Result | Classification |
|---|---:|---|---|
| Passive 60°, 120 and 300 s | 4 | All within preserved ranges | Direct experimental-angle group-level comparison |
| Passive 70°, 120 and 300 s | 4 | All within reused ranges | Extrapolated model-specific acceptance criterion |

At 60°, CO reductions are 17.081349% and 17.081368%; SV reductions are 29.677321% and 29.677322%. The 70° values are not direct replication of a 70° Zaidi experiment. All eight within-band results remain calibrated scenario agreements, not independent external validation.

## Regression, sensitivity, and demonstrations

- All 16 stored regression runs were regenerated with a Stage 1.3 mechanism/evidence/direction change record; tolerance classes are unchanged.
- The focused Stage 1.3 fidelity plus regression selection passed **38 tests**.
- The sensitivity/uncertainty layer passed **15 tests** against fresh exports: 96 local, 27 grid, and 3 chronotropic-split rows.
- Six demonstration groups regenerated 16 persisted result/observation/trace runs and their figures.
- Complete suite: **354 passed, 1 skipped**. The skip is the optional upstream-checkout OCPE adapter test; strict installed-engine validation passed separately.
- Seven-layer runner: **PASS** — 131 software (plus one skip), 45 mathematical, 83 physiological, 35 phenotype, 10 empirical, 15 sensitivity/uncertainty, and 40 scientific-traceability tests.
- Strict scientific traceability: **0 errors, 0 warnings, 0 infos**.
- Strict OCPE package validation: **0 errors, 0 warnings** for `disease-models@0.4.0`; this is structural validation only.
- Ruff: **all checks passed**.

The complete full-suite and seven-layer execution records are in `validation/reports/validation-report.json`, `validation/reports/validation-report.md`, and `validation/reproducibility.json`. Those records distinguish software execution from scientific readiness.

## Reproduction entry points

```bash
python scripts/run_stage1_3_validation.py
python scripts/run_sensitivity.py
python scripts/run_examples.py
python -m pytest -q
python scripts/run_validation.py --no-analysis
python scripts/audit_traceability.py --root . --strict --deterministic --out-dir validation/traceability/audit
python -m ocpe validate ocpe/packages/disease-models --strict
```

Historical Stage 1.2 and Stage 1.1 reports were not rewritten. Stage 1.3 outputs and reports are separate under `validation/stage1-3/` and `docs/stage1-3/`.
