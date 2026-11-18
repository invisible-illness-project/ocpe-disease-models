# Stage 1.2 scientific comparison matrix

This is an executed deterministic research-scenario comparison, not a synthetic cohort, fitted patient dataset, clinical validation, or diagnostic classifier. Stage 1.1 values were rerun from the exact base Git commit; Stage 1.2 values were rerun independently from the remediation commit.

| Record | Commit |
|---|---|
| Stage 1.1 baseline | `f85360d8337144e118eb0d2aef317fd1b949b3dd` |
| Stage 1.2 remediated source | `6034d11d4737bca5d3b6d853900a69690ab90907` |

## Parameter changes

| Scope | Parameter | Stage 1.1 | Stage 1.2 |
|---|---|---:|---:|
| healthy-reference | Splanchnic height (cm) | 5.43774 | 7 |
| healthy-reference | Lower-limb height (cm) | 10.8755 | 14 |
| healthy-reference | Residual systemic height (cm) | 0 | 11 |
| healthy-reference | Cerebral residual slope | 0.2 | 0.4 |
| all_four_pots_phenotypes | Splanchnic height (cm) | 6.79717 | 8 |
| all_four_pots_phenotypes | Lower-limb height (cm) | 13.5943 | 16 |

No chronotropic gain, resistance gain, blood-volume factor, pressure setpoint/scale, governing equation, state layout, or acceptance threshold was changed.

## Healthy orthostatic response

| Metric | Stage 1.1 | Stage 1.2 | Preserved band | Result |
|---|---:|---:|---:|---|
| Sustained HR rise (bpm) | 7.723 | 15.467 | 3–20 | PASS |
| Early minimum CO reduction (%) | 0.346 | 14.570 | 10–30 | PASS |
| Caudal pooling, splanchnic + lower limb (mL) | 365.679 | 302.962 | 300–900 | PASS |
| End-tilt CFI reduction (%) | 1.645 | 4.407 | 3–11 | PASS |
| Residual systemic late volume change (mL) | -101.656 | 162.152 | diagnostic mechanism metric | reported |
| Central venous late volume change (mL) | -281.021 | -478.384 | diagnostic mechanism metric | reported |
| End-tilt heart-level MAP (mmHg) | 111.332 | 108.846 | diagnostic mechanism metric | reported |

The residual compartment no longer supplies preload by draining during tilt. Caudal pooling remains within the preserved band but close to its lower bound. Heart-level MAP remains above supine and is a retained structural limitation.

## Zaidi 60°/70° comparisons

Reductions are positive percentages. Bands and time points are unchanged from Stage 1.1.

| Protocol | Offset (s) | Metric | Stage 1.1 (%) | Stage 1.2 (%) | Published band (%) | Status |
|---|---:|---|---:|---:|---:|---|
| passive-tilt-60 | 120.0 | cardiac_output | 2.571 | 15.801 | 17–20 | MISS |
| passive-tilt-60 | 120.0 | stroke_volume | 11.375 | 29.215 | 28–34 | PASS |
| passive-tilt-60 | 300.0 | cardiac_output | 2.570 | 15.800 | 17–20 | MISS |
| passive-tilt-60 | 300.0 | stroke_volume | 11.375 | 29.214 | 28–34 | PASS |
| passive-tilt-70 | 120.0 | cardiac_output | 3.105 | 18.732 | 17–20 | PASS |
| passive-tilt-70 | 120.0 | stroke_volume | 12.733 | 33.439 | 28–34 | PASS |
| passive-tilt-70 | 300.0 | cardiac_output | 3.105 | 18.730 | 17–20 | PASS |
| passive-tilt-70 | 300.0 | stroke_volume | 12.733 | 33.438 | 28–34 | PASS |

**Six comparisons pass; two MISS.** Both residual misses are 60° cardiac-output reductions. No threshold was widened and no expected failure was introduced to hide them.

## POTS and Long-COVID-autonomic scenario criteria

| Phenotype | Stage 1.1 sustained HR rise (bpm) | Stage 1.2 (bpm) | ≥30 bpm | Minimum upright MAP (mmHg) | MAP ≥70 |
|---|---:|---:|---|---:|---|
| pots-neuropathic | 17.428 | 36.724 | PASS | 100.000 | PASS |
| pots-hyperadrenergic | 19.659 | 43.175 | PASS | 100.000 | PASS |
| pots-hypovolemic | 19.399 | 41.793 | PASS | 92.000 | PASS |
| pots-mixed | 19.216 | 41.686 | PASS | 96.000 | PASS |
| long-covid-autonomic | 18.931 | 32.575 | PASS | 100.000 | PASS |

Long-COVID-exertional remains distinct from the autonomic configuration: sustained HR rise 15.467 bpm, below the POTS scenario threshold.

## Cerebral group-level checks

| Scenario | Stage 1.1 end-tilt CFI reduction (%) | Stage 1.2 (%) | Preserved band | Status |
|---|---:|---:|---:|---|
| Healthy | 1.645 | 4.407 | 3–11 | PASS |
| ME/CFS | 22.913 | 24.652 | 15–35 | PASS |

## Independent cerebral pressure and CO2 controls

The pressure and CO2 pathways remain separately controllable; no posture-inferred hypocapnia was introduced.

| Protocol | Stage 1.1 final CFI | Stage 1.2 final CFI | Brain arterial pressure (mmHg) | ETCO2 (mmHg) | Pressure target | CO2 factor |
|---|---:|---:|---:|---:|---:|---:|
| pressure-reduction | 0.98355 | 0.95593 | 90.183 | 40.0 | 0.95593 | 1.00000 |
| co2-reduction | 0.70469 | 0.70469 | 100.000 | 30.0 | 1.00000 | 0.70469 |
| combined-pressure-co2-reduction | 0.69310 | 0.67363 | 90.183 | 30.0 | 0.95593 | 0.70469 |
| pressure-recovery-persistent-hypocapnia | 0.70469 | 0.70469 | 100.000 | 30.0 | 1.00000 | 0.70469 |
| co2-recovery-persistent-pressure-reduction | 0.98355 | 0.95593 | 90.183 | 40.0 | 0.95593 | 1.00000 |

All five protocols retain exact five-volume conservation. The pressure-only and CO2-only controls remain dissociated; combined pressure/CO2 and persistent-exposure recovery protocols are recorded in JSON.

## Interpretation and retained limitations

- Both 60-degree cardiac-output reductions remain below the preserved 17-20% group band at two and five minutes.
- Healthy heart-level MAP remains above its supine value at end tilt; the integrated reflex and reduced-order compensatory structure still over-defend pressure.
- Hyperadrenergic POTS still lacks an independent non-baroreflex sympathetic/catecholamine state.
- The residual-systemic height and other revised heights are effective calibration parameters, not measured anatomical lengths.
- The cerebral residual slope 0.4 is a calibration choice inside its existing supported range, not an independently identified human autoregulation coefficient.
- Deterministic sensitivity grids are not synthetic patients, population distributions, or probabilistic uncertainty estimates.

Passing software, conservation, scenario-threshold, and sensitivity checks does not resolve the retained empirical misses or establish clinical validity.
