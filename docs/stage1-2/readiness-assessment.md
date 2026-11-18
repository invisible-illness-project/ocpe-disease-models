# Stage 1.2 readiness assessment

## Verdict

Stage 1.2 is suitable for continued **research scenario development with explicit residual empirical limitations**. It is not ready for clinical, diagnostic, treatment, patient-specific, or population-inference use.

The Stage 1.1 preload-buffer defect and the five associated POTS/Long-COVID-autonomic sustained-HR criterion failures are remediated without changing the governing equations or increasing chronotropic gains. Scientific readiness is nevertheless **partial**: two of eight preserved Zaidi comparisons still miss, and the healthy pressure compensation remains excessive.

## Evidence status

| Area | Status | Basis |
|---|---|---|
| Five-volume conservation and twelve-state layout | PASS | Existing mathematical tests and the Stage 1.2 layout guard |
| Supine fixed points and solver convergence | PASS | Existing mathematical layers |
| Residual-bed participation in dependent pooling | PASS | Late residual volume increases by 162.152 mL in healthy 70° tilt |
| Healthy sustained HR rise | PASS | 15.467 bpm versus the preserved 3–20 bpm band |
| Healthy early CO reduction | PASS | 14.570% versus the preserved 10–30% band |
| Healthy caudal pooling | PASS, near lower bound | 302.962 mL versus the preserved 300–900 mL band |
| Healthy end-tilt CFI reduction | PASS | 4.407% versus the preserved 3–11% band |
| ME/CFS end-tilt CFI reduction | PASS | 24.652% versus the preserved 15–35% band |
| Four POTS sustained-HR scenario criteria | PASS | 36.724, 43.175, 41.793, and 41.686 bpm |
| Long-COVID-autonomic sustained-HR criterion | PASS | 32.575 bpm |
| Long-COVID-exertional distinction | PASS | 15.467 bpm; no POTS-like chronotropic override |
| Upright MAP floor and volume conservation in POTS | PASS | Existing phenotype tests remain active |
| Zaidi 60°/70° CO and SV comparisons | **PARTIAL: 6 PASS, 2 MISS** | Both 60° CO reductions remain below 17–20% |
| Strict traceability | PASS | Zero errors, warnings, and infos |
| Strict OCPE package validation | PASS | Zero errors and warnings; structural only |
| Sensitivity and regression checks | PASS | Residual-height coverage added; fixtures reviewed and regenerated |

The executed numerical evidence and exact commits are in `validation/stage1-2/scientific-comparison-matrix.md` and `.json`.

## Retained scientific limitations

1. **Incomplete graded-tilt agreement.** At 60°, CO reduction is 15.801% at two minutes and 15.800% at five minutes. Both remain below the preserved 17–20% group-level band. Corresponding SV comparisons pass. No criterion widening is justified by the current evidence.
2. **Pressure over-defence persists.** Healthy end-tilt heart-level MAP is 108.846 mmHg versus a 100 mmHg supine baseline. Separate aortic and carotid signals are preserved, but their integrated weighted feedback and the reduced vascular structure still produce an upright pressure rise rather than a fully realistic healthy response.
3. **Pooling margin is narrow.** Healthy splanchnic-plus-lower-limb late pooling is only 2.962 mL above the lower edge of the broad band. The residual compartment pools separately and is not added to this declared caudal metric.
4. **Effective rather than anatomical geometry.** Regional heights are lumped calibration parameters. In particular, 11 cm for the residual compartment is not a measured average anatomy and must not be interpreted as a patient-specific hydrostatic column.
5. **Cerebral calibration overlap.** Residual slope 0.4 lies within the pre-existing supported range but was selected using the same healthy CFI plausibility band now reported as an outcome. This is calibration agreement, not independent external validation.
6. **Hyperadrenergic mechanism remains incomplete.** The configuration still lacks an independent non-baroreflex sympathetic or catecholamine state. Its threshold agreement must not be interpreted as identification of hyperadrenergic physiology.
7. **Other prior calibration exceptions remain.** The hypovolemic pressure-scale value of 6.0 and neuropathic gain value of 0.35 were not changed or reclassified by Stage 1.2.
8. **Non-POTS geometry overrides remain un-recalibrated.** ME/CFS, hEDS, and Long-COVID-autonomic retain their Stage 1.1 fixed-offset-derived splanchnic and lower-limb heights. Because healthy and POTS heights changed, inherited ratios to healthy values must not be interpreted as anatomical differences or phenotype-severity evidence. These configurations were not re-fitted in Stage 1.2.
9. **Structural uncertainty is not quantified.** One-at-a-time sensitivity and small deterministic grids do not identify parameter distributions, resolve model-structure alternatives, or estimate population variability.

## Validation interpretation

A green test suite means the declared executable checks passed. It does not erase separately reported empirical `MISS` rows. Conversely, the two remaining group-level misses are not software failures and must not be converted into silent expected failures. Registry status, narrative evidence, and release interpretation must preserve that distinction.

Strict OCPE validation establishes structural and semantic package consistency only. Exact volume conservation establishes an implementation invariant only. Neither establishes physiological or clinical truth.

## Required next scientific work

- Reassess tilt-angle-dependent CO/SV responses using data or structure not used for the present calibration, with particular attention to the residual 60° CO deficit.
- Investigate integrated aortic/carotid feedback and vascular compensation without removing the separate sensor architecture.
- Evaluate the narrow caudal-pooling margin under parameter perturbations and alternate protocols.
- Seek independent evidence for cerebral autoregulation and residual-bed geometry before upgrading maturity or evidence claims.
- Represent non-baroreflex catecholamine/sympathetic mechanisms before claiming mechanistic specificity for hyperadrenergic POTS.

Any future parameter change must update provenance, sensitivity coverage, regression change records, and executed Stage-specific evidence while preserving this Stage 1.2 record and the earlier Stage 1.1 history.
