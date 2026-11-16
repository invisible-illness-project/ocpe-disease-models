# Stage 1 final validation report

## Scope and interpretation

This report covers the shared physiological remediation in model version 0.2.0. It does not begin Stage 2 and does not establish clinical validity, diagnostic accuracy, patient-specific calibration, treatment efficacy, or wearable agreement. The exact validated source/configuration commit, pinned OCPE commit, dependency environment, commands, and artifact hashes are recorded in `validation/reproducibility.json`; independent layer logs and machine-readable status are under `validation/reports/`.

A PASS below means that the declared computational check executed successfully. It does not convert an assumed mechanism, calibrated scenario, or literature plausibility anchor into independent physiological validation.

## Executive outcome

- The commit-bound complete suite passed **287 tests** at source/configuration commit `fb13cb21aa811da9babff6b271f006b8c79ec30f`: `287 passed, 2 warnings in 250.94s (0:04:10)`. The exact command outputs and artifact hashes are recorded in the reproducibility manifest.
- All seven independently selected validation layers pass. Dual-marked tests make the layer counts sum to more than the unique full-suite count.
- Ruff, strict OCPE validation, and strict scientific traceability pass. OCPE reports zero errors and zero warnings; traceability reports zero errors, warnings, and infos.
- Six demonstrations regenerate 16 persisted runs with current 11-state traces, parameters, protocols, configuration hashes, observations, and figures.
- Deterministic analysis regenerates 42 local-sensitivity executions, 18 assumption-grid scenarios, and three fixed-total chronotropic-split scenarios.
- Two deliberate warnings remain: healthy early cardiac-output reduction and healthy end-tilt cerebral-flow-index reduction miss their broad soft plausibility anchors. These negative results were not hidden or tuned away.

## Independent seven-layer results

| Layer | Executed result | Principal coverage |
|---|---:|---|
| Software | 122 passed | Configuration, serialization, failure behavior, OCPE adapter, executable/declarative consistency, and reviewed regression fixtures |
| Mathematical | 44 passed | Four-volume conservation, all-phenotype fixed points, flow identities, bounds, and solver convergence |
| Physiological | 29 passed, 1 soft-anchor warning | Orthostasis, recovery, autonomic separation, muscle pump/contraction, CPP/CFI, and explicit empirical anchors |
| Disease phenotype | 35 passed | POTS configurations, hEDS exploration, ME/CFS PEM, and Long COVID heterogeneity |
| Empirical | 9 passed, 1 soft-anchor warning | Literature-linked group-level plausibility comparisons with calibration overlap and the healthy cerebral-control miss disclosed |
| Sensitivity/uncertainty | 13 passed | Regional and autonomic sensitivity, deterministic grids, chronotropic split, and reproducibility |
| Scientific traceability | 40 passed | Registry schemas/links, complete scientific chains, scope guards, and bibliography synchronization |

The executed summaries and elapsed times are in `validation/reports/validation-report.json` and the corresponding layer logs. Missing layers and empty pytest selections are failures by policy, not skips.

## Mathematical and numerical validation

### Conservation and resting fixed points

The arterial, central-venous, splanchnic-venous, and lower-limb-venous derivatives telescope exactly at the RHS level. Integrated four-volume drift remains below the declared `1e-6 mL` tolerance in baseline, tilt, recovery, reduced-volume, walking, rhythmic-activity, and sustained-contraction checks. The largest drift in the reviewed 16-run regression fixture is approximately `8.28e-11 mL`.

All ten configurations are tested at their complete supine initial state. Each has maximum absolute initial RHS component below `1e-9`; observed residuals are zero or at floating-point scale (approximately `1.42e-14` maximum). The tests also require:

- `CO = HR × SV / 60` in internal mL/s units;
- total venous return equals cardiac output;
- total systemic arterial flow equals cardiac output;
- splanchnic arterial inflow equals splanchnic venous return; and
- lower-limb arterial inflow equals lower-limb venous return.

These identities verify implementation consistency, not anatomical completeness. DOP853 convergence checks independently tighten step size and tolerances. Invalid domains, negative stressed volumes, non-finite states, autonomic states outside `[0,1]`, and CFI outside declared bounds fail explicitly.

### Orthostatic metric semantics

Peak and sustained HR rise are reported separately. Sustained rise uses the mean HR over the final 120 seconds **of the upright segment**, clamped before post-tilt recovery. The peak window is also clamped to the upright segment. This prevents a supine recovery window from being mislabeled as sustained orthostatic tachycardia.

## Shared physiological mechanisms

The shared implementation has no disease-name conditionals. Disease scenarios enter only through registered parameters and protocol inputs.

- Rhythmic activity adds an explicit lower-limb-to-central-venous pump transfer. Tests require the source and destination derivatives to change by equal and opposite amounts; pumping does not create volume.
- Sustained contraction increases lower-limb venous resistance and reduces passive venous return for the same initial state. It is independent of rhythmic activity and metabolic exertion.
- Cardiac sympathetic, vascular sympathetic, and vagal states have separate targets, gains, and time constants. Independent perturbation tests prevent HR from silently proxying every autonomic pathway.
- Cerebral perfusion pressure uses head-level arterial pressure minus central venous back pressure. The normalized pressure curve passes through zero and the reference point, remains bounded in tested regimes, and uses asymmetric decline/recovery lags.
- Inactive standing, light rhythmic activity, walking, and sustained contraction are separate registered protocols, with all four volume states conserved.

## Disease-configuration outcomes

The adult sustained-HR threshold is a scenario acceptance criterion, not a diagnostic classifier or independent validation. Chronotropic gains were explicitly calibrated after the architectural migration; threshold agreement therefore has calibration overlap.

| Configuration | Sustained HR rise (bpm) | Final MAP (mmHg) |
|---|---:|---:|
| Healthy reference, head-up tilt | 11.45 | 117.40 |
| POTS neuropathic | 31.63 | 115.71 |
| POTS hyperadrenergic | 30.38 | 118.61 |
| POTS hypovolemic | 30.66 | 105.23 |
| POTS mixed | 32.84 | 111.28 |
| Long COVID autonomic | 31.14 | 117.08 |
| hEDS vascular exploratory scenario | 19.62 | 116.87 |

The hypovolemic configuration retains its reduced resting operating point: HR 70 bpm, SV approximately 68.22 mL, and CO approximately 4.775 L/min. The mixed configuration retains HR 70 bpm, SV approximately 69.14 mL, and CO approximately 4.840 L/min. Their resting states were not restored to healthy cardiac output to obtain upright threshold crossings.

### ME/CFS delayed onset and recovery

The corrected ME/CFS configuration uses delayed-stress, PEM-onset, and PEM-recovery time constants of 72000, 86400, and 172800 s. The repeated-exertion protocol extends to seven days so prolonged recovery is observable.

- Maximum PEM during the first exertion: approximately 0.000217.
- Maximum PEM during the first post-exertional hour: approximately 0.007984, below the required 0.01.
- Delayed peak: approximately 0.1752 at 39.17 hours after the first exertion ends.
- Half-recovery after the peak: approximately 2.06 days, observable within the extended protocol.
- Normalized PEM first exceeds 0.05 approximately 5.7 hours after the day-1 bout ends. This is earlier than the commonly cited 12–48-hour onset window after daily activity, although post-CPET reports of onset within 24 hours include this timing. The early threshold crossing and the later peak are therefore distinct findings: the former is a scenario-timing limitation, while the latter is compatible with the cited delayed-peak evidence.
- Healthy PEM under the same protocol remains exactly zero.

These are normalized phenomenological states, not symptom scores, molecular mechanisms, or individual patient forecasts.

## Empirical plausibility and retained negative results

The healthy early-CO reduction is approximately **5.64%**, below the broad **10–30%** soft anchor. This remains an explicit warning and structural limitation. Caudal stressed-volume accumulation is approximately **336.55 mL**, within the broad **300–900 mL** soft band. Neither band is a hard fitted target, and a PASS elsewhere does not erase the CO miss.

The healthy end-tilt cerebral-flow-index reduction is approximately **0.003%**, far below the reported approximately **7%** control reduction and outside the broad **3–11%** disclosure band. Heart-level MAP rises approximately **17.4 mmHg to 117.4 mmHg** in the same scenario, so the pressure-only autoregulation proxy nearly abolishes the healthy control-side response. This emits a separate empirical-layer warning. The ME/CFS assertion remains within its unchanged **15–35%** scenario band and must exceed the healthy reduction; no criterion was weakened to hide the control miss.

The current hEDS compliance/gravity grid has no final-MAP values below the 70 mmHg screening threshold; its range is approximately 115.0–117.7 mmHg. This does not validate the assumed hEDS compliance. Historical Stage 0 failed regimes, including below-70-mmHg cases, remain preserved in the baseline record and are not rewritten as current successes.

## Sensitivity, uncertainty, and identifiability

Local analysis covers regional compliances and resistances, regional vascular gains and gravity offsets, blood-volume factor, all three autonomic lags, cerebral autoregulation residual slope, muscle-pump stroke volume/frequency/effectiveness/half-volume, and sustained-contraction resistance gain. Outputs include both peak and sustained HR rise.

The fixed-total chronotropic-split analysis varies cardiac-sympathetic fraction from 0 to 0.5 to 1 while holding total gain at 80 bpm. Neuropathic sustained HR rise remains approximately 31.63 bpm and final MAP approximately 115.71 mmHg, while peak HR rise changes from approximately 34.99 to 33.23 to 32.68 bpm. The split is therefore not identified by the current evidence and steady-state criteria.

All ranges are deterministic computational scenarios. They are not probability distributions, synthetic patients, prevalence estimates, global identifiability analysis, or population uncertainty quantification.

## Regression and provenance controls

The original regression fixture and original validation snapshot are preserved byte-for-byte under `validation/baseline/stage0/`, together with the fresh Stage 0 test log and environment. The Stage 1 fixture contains 16 reviewed runs—the original 12 protocols/scenarios plus four muscle-protocol runs—and a dated scientific change record linking the architecture review, mechanisms, evidence, expected directions, chronotropic calibrations, and PEM correction.

The traceability chain is:

`reference → evidence claim → mechanism → equation → parameter → implementation → validation → output`.

The current registries contain 64 references, 37 evidence claims, 23 mechanisms, 20 equations, 52 parameter records, 26 validation records, nine protocols, and eight simulation records. Strict cross-registry audit passes with zero errors and warnings. The 64-entry BibTeX export is guarded against registry drift.

## Remaining limitations and release decision

Stage 1 is computationally complete for the declared shared remediation, subject to the explicitly retained early-CO and healthy-CFI misses, the early PEM threshold-crossing caveat, and structural uncertainties. Linear compliances, clipped nonnegative flows, phenomenological gravity offsets, reduced-order preload, absent CO₂ and renal/endocrine volume regulation, lack of pure neural delays and venous valves, and calibrated disease scenarios all limit inference. No integrated model is independently clinically validated or assigned M4 on the basis of these tests.

The repository is ready for **reviewed Stage 2 planning only**. It is not ready to generate clinically meaningful synthetic wearable data without a separately specified sensor, cohort, governance, and agreement-validation framework. Stage 2 implementation has not begun.
