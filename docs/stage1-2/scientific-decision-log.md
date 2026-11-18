# Stage 1.2 scientific decision log

## Purpose and scope

Stage 1.2 remediates orthostatic cardiovascular behavior exposed by Stage 1.1 while preserving its architecture. The work is a deterministic reduced-order scenario calibration and regression effort. It is not patient-specific fitting, clinical validation, diagnostic model development, or treatment evaluation.

Authoritative source records:

- Stage 1.1 base: `f85360d8337144e118eb0d2aef317fd1b949b3dd`.
- Stage 1.2 remediation: `6034d11d4737bca5d3b6d853900a69690ab90907`.
- Executed before/after outputs: `validation/stage1-2/scientific-comparison-matrix.json` and `.md`.
- Parameter provenance: `literature/parameter_registry.yaml`.
- Historical Stage 1.1 records remain unchanged under `docs/stage1-1/` and `validation/stage1-1/`.

## Preserved architecture

No governing equation, state name, state ordering, solver method, or conservation identity was changed. Stage 1.2 retains:

1. five exactly conserved stressed-volume compartments;
2. the twelve-state layout and residual systemic venous compartment;
3. explicit tilt-angle geometry and `0.7356 × height_cm × sin(angle)` hydrostatic pressure;
4. separate aortic and carotid baroreceptor pressure errors;
5. distinct cardiac-sympathetic, vascular-sympathetic, and vagal states;
6. independent cerebral pressure and declared end-tidal-CO2 pathways.

No POTS chronotropic gain, vascular resistance gain, blood-volume factor, pressure setpoint, pressure scale, or acceptance threshold was changed.

## Root cause

### Residual systemic preload bypass

Stage 1.1 assigned the residual other-systemic bed a zero hydrostatic height even though that compartment carries 50% of baseline systemic flow. During tilt it therefore behaved as a heart-level preload-preserving pathway. In the exact baseline rerun, its late stressed volume **decreased by 101.656 mL**, while central venous volume decreased by only 281.021 mL. This volume redistribution opposed the intended orthostatic preload loss.

The problem was not five-volume conservation: the five compartments remained exactly conservative. It was the physiological assignment of geometry within that conservative structure.

### Insufficient stroke-volume and cardiac-output response

The preload bypass limited central preload loss and hence stroke-volume loss. At 70° and two minutes, Stage 1.1 produced only 3.105% CO reduction and 12.733% SV reduction. The healthy early minimum CO reduction was 0.346%, below the preserved 10–30% plausibility band. These responses left vascular sympathetic compensation with little CO deficit to offset.

### Pressure over-defence and aortic/carotid cancellation

With equal sensor setpoints and scales, the integrated weighted reflex effectively defends an upright heart-level pressure above the supine setpoint because the carotid sensor experiences a hydrostatic pressure drop while the aortic sensor remains at heart level. At Stage 1.1 defaults and 70°, the corresponding integrated target is approximately `100 + 0.75 × 17.28 = 112.96 mmHg` before dynamic feedback effects.

When the preload defect preserved CO, vascular sympathetic activation drove heart-level MAP to 111.332 mmHg. The resulting positive aortic pressure error opposed the carotid orthostatic error. Integrated baroreflex targets consequently remained too low for the unchanged POTS chronotropic gains to generate a sustained rise of at least 30 bpm. Increasing those gains would have concealed the shared hemodynamic defect rather than remediate it.

### Cerebral consequence

The same pressure over-defence, together with the cerebral autoregulation residual slope of 0.2, limited healthy end-tilt CFI reduction to 1.645%, below the preserved 3–11% soft group-level band. The cerebral response was therefore downstream of both the cardiovascular defect and a conservative cerebral calibration.

## Selected remediation

| Scope | Parameter | Stage 1.1 | Stage 1.2 | Decision basis |
|---|---|---:|---:|---|
| Healthy | `splanchnic_hydrostatic_height_cm` | 5.437737901 | 7.0 | Effective dependent-bed geometry constrained by preserved healthy CO/SV/pooling bands |
| Healthy | `lower_limb_hydrostatic_height_cm` | 10.875475802 | 14.0 | Same joint calibration |
| Healthy | `other_systemic_hydrostatic_height_cm` | 0.0 | 11.0 | Removes the zero-height preload bypass; includes the residual bed in dependent pooling |
| POTS, all four configurations | `splanchnic_hydrostatic_height_cm` | 6.797172376 | 8.0 | Phenotype-scale effective geometry without changing autonomic gains |
| POTS, all four configurations | `lower_limb_hydrostatic_height_cm` | 13.594344753 | 16.0 | Same joint calibration |
| Shared cerebral model | `cerebral_autoregulation_residual_slope` | 0.2 | 0.4 | Retains a bounded pressure-responsive component within the pre-existing 0.1–0.4 supported range |

These are effective lumped calibration parameters, not measured anatomical heights or independently identified subject-specific coefficients. The residual systemic supported range is now 5–16 cm. The revised values, calibration methods, value classes, and provenance are recorded in the parameter registry and synchronized with the declarative OCPE package.

ME/CFS, hEDS, and Long-COVID-autonomic splanchnic/lower-limb overrides were deliberately left at their Stage 1.1 fixed-offset-derived values. They were not recalibrated in this healthy/POTS-focused remediation. Their changed ratios to the new healthy defaults are therefore inherited scenario-geometry relationships, not evidence of anatomical phenotype differences or disease severity; this limitation is explicit in the registry and readiness assessment.

## Alternatives considered and rejected

### Increase POTS chronotropic gains

Rejected as the primary correction. At sustained equilibrium the unchanged model gives `ΔHR = (g_cardiac + g_vagal) × (baroreflex_target − 0.5)`. Larger gains could cross 30 bpm despite the preload and pressure-feedback artifact, but would leave healthy CO/SV, residual-compartment, and cerebral behavior incorrect. All chronotropic gains therefore remain unchanged.

### Steepen the preload–stroke-volume curve

Explored but not adopted. A steeper curve can increase SV loss without assigning the residual bed a physiologically dependent height, leaving the principal compartmental artifact in place. Stage 1.2 retains `stroke_volume_max = 100` and `stroke_volume_half_volume = 300`.

### Change only the residual systemic height

Rejected as incomplete. It corrects the bypass direction but did not provide the selected joint healthy/POTS CO, SV, pooling, and chronotropic calibration. The final choice jointly adjusts healthy and POTS caudal heights and the residual height.

### Widen bands or retain expected failures

Rejected. Existing group-level bands and the sustained POTS scenario criterion are unchanged. The five Stage 1.1 strict phenotype expected failures were removed only after direct passes. The two remaining 60° CO misses are explicitly retained as `MISS`; they are not hidden with new expected failures or excluded from the narrative evidence.

### Rewrite Stage 1.1 historical evidence

Rejected. Historical records remain an auditable account of the prior model. Stage 1.2 writes separate evidence and preserves the base commit for exact reproduction.

## Outcome

Relative to the exact Stage 1.1 Git baseline:

- healthy early minimum CO reduction changed from 0.346% to 14.570%;
- healthy sustained HR rise changed from 7.723 to 15.467 bpm;
- residual systemic late volume change reversed from −101.656 to +162.152 mL;
- central venous late volume change increased in magnitude from −281.021 to −478.384 mL;
- healthy end-tilt CFI reduction changed from 1.645% to 4.407%;
- all four POTS configurations and Long-COVID-autonomic now pass the unchanged sustained ≥30 bpm scenario criterion with upright MAP above 70 mmHg;
- six of eight preserved Zaidi comparisons pass.

The 60° CO reductions remain 15.801% and 15.800% at two and five minutes, below the unchanged 17–20% band. End-tilt healthy heart-level MAP also remains 8.846 mmHg above its supine baseline. These are unresolved scientific limitations, not validation passes.

## Sensitivity and regression policy

Residual systemic height was added to local neuropathic-POTS sensitivity, its registry fixture, and direction/coverage tests. Regression fixtures were regenerated only after the mechanism and expected directions were established; the fixture change record identifies Stage 1.2, the affected runs, and the reason. Solver settings and fixture tolerances were not weakened.

Sensitivity outputs remain deterministic scenario grids. They do not represent patients, prevalence, probability distributions, global identifiability, or population uncertainty.
