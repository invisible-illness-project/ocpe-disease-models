# Stage 1.1 validation matrix

This matrix maps the seven-layer validation architecture onto the Stage 1.1
(model 0.3.0, 12 states, five volumes) revision.

**Execution status (two distinct tracks, both executed).**

1. **Scientific scenario comparisons — EXECUTED.** The deterministic 0.3.0
   scientific comparison matrix is generated at
   `validation/stage1-1/scientific-comparison-matrix.md` and
   `validation/stage1-1/scientific-comparison-matrix.json` (schema 1.0,
   model_version 0.3.0, per-run configuration SHA-256 and solver metadata;
   analysis policy: no gain recalibration, no threshold widening, no
   synthetic cohort, no posture-inferred hypocapnia). Its results are
   reported in sections 4–6 below, including all negative outcomes.
2. **Release validation — EXECUTED.** The full pytest suite, the seven-layer
   runner, the strict scientific-traceability audit, strict OCPE package
   validation, regression-fixture regeneration, sensitivity exports, and
   demonstration regeneration have all been executed for 0.3.0 at frozen
   tested source commit `a6d7619e277fc05081de3c852189b549d714b8b5`
   (`validation/reports/validation-report.json` / `.md`,
   `model_version: 0.3.0`). Full suite: **323 passed, 1 skipped
   (`tests/unit/test_ocpe_adapter.py:74`, upstream OCPE checkout
   unavailable; strict installed-engine OCPE validation separately passes
   with 0 errors/0 warnings), 6 xfailed, 2 warnings in 344.19s**. Every
   layer's execution status is PASS; the disease-phenotype layer contains
   six strict expected failures, so its scientific status is FAIL and the
   **overall seven-layer scientific status is FAIL** — the strict xfails
   preserve unresolved scientific criterion misses and are not passes. The
   Stage 1 results below are historical, bound to the 0.2.0 tested commit
   (`fb13cb21aa811da9babff6b271f006b8c79ec30f`, 287 tests passed with two
   intended soft-anchor warnings). Prior Stage 1 misses are preserved as
   open items, not resolved.

## 1. Layer matrix

| Layer | Stage 1 (0.2.0, historical) | Stage 1.1 (0.3.0) status | Stage 1.1-specific requirements |
|---|---|---|---|
| Software | 122 passed | **Executed — 127 passed, 1 skipped (upstream OCPE checkout unavailable; strict installed-engine OCPE validation passes separately, 0 errors/0 warnings), 202 deselected in 198.15s; execution PASS** | Reject segments specifying both `upright` and `tilt_angle_deg`; reject angle outside [0, 90]; reject nonpositive declared ETCO2; reject baroreflex weights not summing to 1 (1e-6); unknown-parameter rejection still covers renamed keys |
| Mathematical | 44 passed | **Executed — 45 passed, 285 deselected in 9.33s; execution PASS** | Exact **five-volume** telescoping (`dVa+dVc+dVs+dVl+dVo = 0`) and tight simulated drift across all protocol families including active standing, graded tilt, tilt-back, and sustained contraction; exact supine fixed point for **all** registered configurations under 0.3.0 parameters; CFI bounds including the CO2-term upper bound `exp(0.035 × 15)` |
| Physiological | 29 passed, 1 warning | **Executed — 64 passed, 266 deselected, 1 preserved early-CO soft-anchor warning (0.35% vs the 10–30% band) in 8.15s; execution PASS** (scenario matrix executed separately, below) | Orthostatic directionality at each graded angle; monotonic posture dose–response across 30/45/60/70 degrees (directional, not fitted); isolated-pressure vs isolated-CO2 vs combined cerebral protocols separate the two effects; pressure recovery with persistent hypocapnia does not restore CFI |
| Disease phenotype | 35 passed | **Executed — 29 passed, 295 deselected, 6 strict xfailed in 186.51s; execution PASS, scientific status FAIL for the unchanged sustained-HR criterion misses** | All ten configurations re-derived to exact supine fixed points after resistance re-partition and baroreflex split; POTS sustained-HR-rise scenario criterion re-evaluated with dual-sensor baroreflex |
| Empirical (scientific scenario comparisons) | 9 passed, 1 warning | **Executed — 10 passed, 320 deselected, 1 preserved healthy-CFI warning (1.645% vs the 3–11% band) in 96.46s; execution PASS** — see sections 4–6; includes 8 Zaidi CO/SV MISSes and 5 sustained-HR criterion FAILs | Anchors in section 4 evaluated unchanged; Stage 1 misses (section 5) re-measured; negative results reported, not tuned |
| Sensitivity/uncertainty | 13 passed | **Executed — 13 passed, 317 deselected in 124.91s; execution PASS; 59 local, 27 grid, 3 split scenarios regenerated** | Local CO2-reactivity and CO2-clip scenarios and a CO2-reactivity × cerebral-outflow-pressure grid are included; heights, sensor heights, and other-systemic resistances are also covered. These deterministic scenarios do not establish global identifiability |
| Scientific traceability | 40 passed | **Executed — 40 passed, 290 deselected in 4.16s; execution PASS; strict audit 0 errors/0 warnings/0 infos on the synchronized 0.3.0 registries** | Equation, parameter, mechanism, protocol, simulation, and validation registries are synchronized to the 0.3.0 names/counts (69 references, 41 evidence claims, 24 mechanisms, 22 equations, 68 parameters, 29 validation records, 19 protocols, 11 simulation records) |

## 2. New invariants introduced by 0.3.0

- Five-volume conservation (analytic and integrated) replaces the
  four-volume identity; the Stage 1 four-volume tests are superseded, not
  deleted from history.
- `aortic_baroreflex_weight + carotid_baroreflex_weight = 1` within 1e-6.
- At `tilt_angle_deg = 0` every hydrostatic term is exactly zero and the
  CO2 factor is exactly 1 at the 40 mmHg reference.
- During a transition, only the angle varies; all other inputs are
  piecewise constant.
- Baseline systemic flow partition is 25/25/50 (splanchnic/lower-limb/
  other) at the healthy operating point, with total stressed volume
  2550 mL.

## 3. Predefined time-resolved reporting windows (CO/SV/HR)

Windows are declared **before** the rerun to prevent post-hoc selection.
`t0` denotes the start of the first non-supine segment (120 s in the
registered tilt/standing protocols). Statistics follow the existing
`SimulationResult.metric` conventions.

| Window | Definition | Reported quantities | Primary use |
|---|---|---|---|
| Supine baseline | t ∈ [0, t0 − 2 s] | mean HR, CO, SV, MAP, venous return | Reference for all rises/reductions |
| Transition | t ∈ [t0, t0 + transition_duration] | time-resolved HR, CO, SV, MAP | Active-stand (3 s) vs passive-tilt (30 s) transient shape |
| Early upright | t ∈ [t0, t0 + 30 s] | min CO, min SV, min venous return, HR | Early orthostatic CO transient (Stage 1 soft anchor) |
| Peak | t ∈ [t0, t0 + 300 s] | max HR; HR rise vs baseline | Peak orthostatic HR rise (secondary POTS metric) |
| Sustained | final 120 s of the upright/standing segment | mean HR; sustained HR rise; late regional volumes | **Primary** POTS scenario criterion; caudal volume accumulation |
| Recovery (tilt-back) | t ∈ [600, 1200] of `tilt-recovery` | time-resolved HR, CO, SV, CFI recovery | Tilt-back recovery dynamics |

The same window definitions apply to the cerebral CO2 protocols with the
segment boundaries declared in their YAMLs; no window is fitted to an
observed feature.

## 4. Protocol-specific empirical anchors (executed 0.3.0 outcomes)

Source: `validation/stage1-1/scientific-comparison-matrix.md` / `.json`.
Stage 1 bands and criteria are unchanged. The Zaidi 60/70-degree CO/SV
comparisons are newly predeclared for Stage 1.1, not historical Stage 1
criteria. No threshold was widened and no gain was recalibrated.

| Protocol family | Anchor (group-level, predeclared) | Stage 1 outcome | Stage 1.1 (0.3.0) outcome |
|---|---|---|---|
| `head-up-tilt`, healthy | Upright HR rise within 3–20 bpm; upright MAP > 70 mmHg | Passed | Sustained HR rise **+7.723 bpm** at 70 degrees (graded: 3.626/5.417/6.954 at 30/45/60 degrees); final MAP 111.332 mmHg — direction and band consistent (the ~111.332 mmHg upright-end pressor response remains a disclosed fidelity limitation, not a validated healthy MAP response); formal tests executed in the physiological layer |
| `head-up-tilt`, healthy | Early/sustained CO reduction soft band 10–30% | **Miss (~5.64%)**, warning retained | **Miss persists**: sustained CO change **−3.105%** at 70 degrees (early-CO warning now 0.35% vs the 10–30% band); all eight Zaidi 60/70-degree 2/5-min CO/SV comparisons MISS (model CO −2.571/−3.105% vs published −20 to −17%; model SV −11.375/−12.733% vs published −34 to −28%) |
| `head-up-tilt`, healthy | Caudal stressed-volume accumulation soft band 300–900 mL | Within band (~336.55 mL) | Executed in the physiological layer (64 passed); the ~336.55 mL value remains the Stage 1 (0.2.0) historical record |
| `tilt-recovery`, healthy | End-tilt CFI reduction soft band 3–11% around the ~7% control finding | **Miss (~0.003%)**, warning retained | **Miss persists but narrows**: end CFI reduction **1.645%** at 70 degrees, still below the unchanged 3–11% disclosure band |
| `tilt-recovery`, ME/CFS | CFI reduction band 15–35% around the ~26% group mean | Passed | **Within band**: 22.913% reduction |
| `head-up-tilt`, POTS phenotypes | Sustained HR rise ≥ 30 bpm scenario criterion (calibration overlap, not independent validation) | Met by calibrated scenarios | **FAIL (all four)**: neuropathic 17.428, hyperadrenergic 19.659, hypovolemic 19.399, mixed 19.216 bpm; Long-COVID-autonomic 18.931 bpm also FAILs the unchanged ≥30 bpm criterion |
| `single-/repeated-exertion-recovery`, ME/CFS | PEM onset within the reported 12–48 h daily-activity window; repeated-CPET capacity reduction band 2–20% around 5.3%/13.8% | Band passed; onset timing caveat (~5.7 h first 0.05 crossing) retained | PEM equations unchanged; the release suite executed the exertion/recovery protocols with no PEM warning and no band weakening; the onset-timing caveat stands |
| Long COVID exertional | Oxygen extraction 0.49 vs 0.78 group anchors | Anchored scenario | Unchanged configuration; executed in the release suite (empirical layer 10 passed, 1 healthy-CFI warning) |
| `passive-tilt-30/45/60/70`, `active-standing`, `inactive-standing`, cerebral CO2 protocols | Directional/dissociation expectations (graded response; pressure–CO2 separability) | n/a (new protocols) | **Executed**: graded HR/MAP/CFI responses across 30–70 degrees; active-standing sustained rise 8.383 bpm; inactive-standing 8.383 bpm; cerebral isolation results in section 6 |

## 5. Preserved Stage 1 misses and new 0.3.0 negative results

1. **Healthy CO/SV orthostatic miss — persists.** Stage 1: early CO
   reduction ~5.64% vs the broad 10–30% soft band. Stage 1.1: sustained CO
   −3.105% and SV −12.733% at 70 degrees, and **all eight** Zaidi
   (REF-ZAIDI-2000) 60/70-degree, 2/5-minute CO/SV comparisons MISS the
   published ranges newly predeclared for this Stage 1.1 comparison. The reduced-order structure still
   underrepresents the orthostatic CO/SV reduction; this is reported as a
   negative result, not tuned.
2. **Healthy end-tilt CFI miss — persists, narrowed.** Stage 1: ~0.003% vs
   the 3–11% disclosure band around the ~7% control finding. Stage 1.1:
   1.645% at 70 degrees (0.819/1.192/1.497% at 30/45/60 degrees) — still
   below the unchanged band. The historical 0.003% value remains the Stage
   1 record.
3. **PEM onset-timing caveat — stands.** PEM equations are unchanged; the
   scenario checks were re-executed in the full release suite without a PEM
   warning, and the ~5.7 h first-0.05 crossing caveat (peak ~39.2 h) is
   retained unchanged.
4. **Historical hEDS grid failures — preserved.** The pre-revision
   below-70-mmHg MAP grid failures (minimum ~37.84 mmHg) remain archived
   under `validation/baseline/stage0/`; the hEDS venous-compliance scenario
   remains M2. The 0.3.0 hEDS tilt run (sustained HR rise 12.448 bpm, final
   MAP 111.195 mmHg) shows no below-70-mmHg regime in that protocol.
5. **NEW — POTS sustained-HR criterion failure.** All four POTS phenotypes
   and the Long-COVID-autonomic phenotype now FAIL the unchanged ≥30 bpm
   sustained-rise criterion (17.428–19.659 bpm range). Under 0.2.0 the
   calibrated scenarios met it; the dual-sensor integrated baroreflex and
   re-partitioned resistances changed the sustained response. This is a
   preserved negative result: the criterion was not widened and the gains
   were not recalibrated.

## 6. Executed cerebral pressure/CO2 isolation experiments (0.3.0)

The five `simulations/cerebral/` protocols were executed; they confirm the
designed separability of the pressure and CO2 pathways:

| Protocol | Final brain arterial pressure (mmHg) | Final ETCO2 (mmHg) | Pressure target | CO2 factor | Final CFI |
|---|---:|---:|---:|---:|---:|
| `pressure-reduction` | 92.668 | 40.0 | 0.98355 | 1.00000 | 0.98355 |
| `co2-reduction` | 100.000 | 30.0 | 1.00000 | 0.70469 | 0.70469 |
| `combined-pressure-co2-reduction` | 92.668 | 30.0 | 0.98355 | 0.70469 | 0.69310 |
| `pressure-recovery-persistent-hypocapnia` | 100.000 | 30.0 | 1.00000 | 0.70469 | 0.70469 |
| `co2-recovery-persistent-pressure-reduction` | 92.668 | 40.0 | 0.98355 | 1.00000 | 0.98355 |

Interpretation: the isolated pressure reduction moves the CFI only to
0.98355 while an ETCO2 step to 30 mmHg moves it to 0.70469 (the
`exp(0.035 × −10)` factor), and the combined experiment gives 0.69310 —
the declared CO2 pathway dominates the cerebral response in this structure.
The two recovery experiments remain separated: pressure recovery with
persistent hypocapnia does **not** restore CFI (0.70469 persists), and CO2
recovery with persistent pressure reduction leaves the 0.98355 pressure
signature — confirming there is no posture-inferred hypocapnia and no
cross-coupling between the two pathways.

## 7. Closure record

The Stage 1.1 release validation record is written: (i) the sensitivity
regeneration completed and is recorded (59 local, 27 grid, 3 split
scenarios; 13 sensitivity tests passed); (ii) registry synchronization to
the 0.3.0 parameter/equation/protocol names is verified by a strict
traceability audit with zero errors, warnings, and infos; (iii) regression
fixtures were regenerated through the scientific change-management process
(19 regression tests passed, 0.2.0 fixtures preserved in Git history and
Stage 0 originals unchanged); (iv)
the full seven-layer pytest suite ran on the recorded source/configuration
commit `a6d7619e277fc05081de3c852189b549d714b8b5` (full suite 323 passed,
1 skipped, 6 xfailed, 2 warnings in 344.19s; strict disease-models OCPE
validation 0 errors/0 warnings); and (v) the negative results in sections
4–6 (8 Zaidi MISSes, 5 sustained-HR criterion FAILs, persistent healthy
CO/SV and CFI misses) are carried into the release report unchanged. Every
layer's execution status is PASS; because the disease-phenotype layer's six
strict expected failures are preserved scientific failures, the layer's
scientific status and the **overall seven-layer scientific status are
FAIL**. Execution PASS is not a scientific pass, and neither is clinical
validation.
