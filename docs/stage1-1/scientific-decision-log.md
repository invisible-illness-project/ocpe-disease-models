# Stage 1.1 scientific decision log

Each entry records the decision, rationale, considered alternative, and
status. "Implemented" means present in source. The deterministic scientific
scenario comparison matrix has been executed for 0.3.0
(`validation/stage1-1/scientific-comparison-matrix.md` / `.json`), and the
release validation cycle (test suite, traceability, OCPE package validation,
fixtures, sensitivity, demonstrations) has been executed at frozen tested
commit `942713ef720ad0e801e71bf9bc78405cd844a739` — full suite 327 passed,
1 skipped, 6 xfailed, 2 warnings in 341.60s; all seven layer execution
statuses PASS; overall seven-layer scientific status FAIL from the preserved
strict phenotype xfails (see `validation-matrix.md`).

## D1.1-01 — Add one residual other-systemic venous compartment

- **Decision.** Split the systemic circulation into splanchnic, lower-limb,
  and one lumped residual (`other_systemic_venous_volume`) venous path, with
  matching arterial resistances. Five volume states, twelve states total.
- **Rationale.** The Stage 1 two-region peripheral split forced 50/50
  baseline flow between splanchnic and lower-limb beds, which
  under-represents the rest of the systemic circulation. A single residual
  compartment is the smallest change that admits a literature-consistent
  **25/25/50 baseline flow partition** while keeping exact volume
  conservation (five derivatives telescope to zero) and a **2550 mL** total
  healthy stressed volume.
- **Alternative rejected.** Adding further named regional beds (renal,
  cerebral, cutaneous, muscle sub-compartments): not identifiable from
  current evidence and would multiply assumed parameters.
- **Status.** Implemented; scenario-matrix baselines are consistent
  (healthy baseline CO 81.667 mL/s, MAP 100 mmHg); fixed-point and
  conservation evidence executed in the mathematical layer (45 passed,
  exact five-volume telescoping and exact supine fixed points of all ten
  configurations).

## D1.1-02 — Re-partition resistances at fixed total conductance

- **Decision.** Double splanchnic and lower-limb arterial resistances
  (defaults and explicit phenotype overrides) and set
  `other_systemic_arterial_resistance` to the original value; same pattern
  for venous resistances. Phenotypes without explicit resistance overrides
  (including neuropathic POTS, hEDS, ME/CFS, Long COVID) received none.
- **Rationale.** At the shared baseline pressures this leaves total systemic
  conductance and cardiac output unchanged while producing the 25/25/50
  partition; the transformation is exact arithmetic, not recalibration.
- **Alternative rejected.** Refitting resistances per phenotype from flow
  data: no patient-level regional flow data justify it.
- **Status.** Implemented in defaults and in the three POTS YAMLs with
  explicit resistance overrides; executed in the scenario matrix.

## D1.1-03 — Hydrostatic heights and explicit tilt angle

- **Decision.** Replace per-region gravity pressure offsets (mmHg) with
  heights (cm) converted at 0.7356 mmHg/cm and scaled by sin(tilt angle).
  Defaults migrated exactly (`4.0/0.7356`, `8.0/0.7356`); phenotype offsets
  migrated with full-precision division. Posture is declared as
  `tilt_angle_deg` in [0, 90]; the legacy `upright` fraction maps through
  `degrees(arcsin(upright))`; declaring both is an error. Transitions
  linearly interpolate the **angle only** over `transition_duration`.
- **Rationale.** The Stage 1 fixed offsets could not represent graded tilt
  (30/45/60/70 degrees), active standing, or tilt-back; sin(θ) scaling is
  the standard hydrostatic geometry and makes the supine limit exactly zero.
- **Alternative rejected.** Instantaneous (step) posture changes: retained
  only when `transition_duration = 0`; a nonzero passive-transition time
  (30 s tilt, 3 s active stand) is the more faithful scenario.
- **Status.** Implemented and executed in the scenario matrix: graded
  healthy sustained HR rises of 3.626/5.417/6.954/7.723 bpm at 30/45/60/70
  degrees, active-standing 8.383 bpm, inactive-standing 8.383 bpm;
  `head-up-tilt` and `passive-tilt-70` produce equivalent reported metrics
  under their declared solver sample grids. Simulation-registry
  synchronization is complete (19 protocols, 11 simulation records).

## D1.1-04 — Separate aortic and carotid sensors; integrated weighted baroreflex

- **Decision.** Model aortic (heart level, 0 cm) and carotid (25 cm)
  baroreceptor pressures separately, each with its own setpoint and scale,
  and integrate one weighted error (defaults 0.25 aortic / 0.75 carotid,
  sum-to-1 enforced within 1e-6) into the unchanged sigmoid target and the
  unchanged three first-order effector lags. Brain-level pressure (27 cm)
  remains a distinct parameter used only for cerebral perfusion.
- **Rationale.** A single head-level proxy conflated the carotid sinus with
  the aortic arch and with brain perfusion; the sites experience different
  hydrostatic corrections under tilt. Independent setpoints/scales allow
  phenotype scenarios (e.g., the hypovolemic and mixed POTS pressure
  setpoints) without implying a brain-pressure change.
- **Alternative rejected.** Separate aortic and carotid effector pathways:
  doubles the autonomic state space without evidence to identify it.
- **Caveat.** The 0.25/0.75 weights are computational assumptions; legacy
  phenotype `baroreflex_pressure_setpoint/scale` overrides were duplicated
  onto both pathways unchanged, which preserves Stage 1 scenario semantics
  but is not new evidence.
- **Status.** Implemented and executed. Negative outcome preserved: all
  four POTS phenotypes (17.428–19.659 bpm) and Long-COVID-autonomic
  (18.931 bpm) FAIL the unchanged ≥30 bpm sustained-rise criterion that the
  0.2.0 calibrated scenarios met; the criterion was not widened and gains
  were not recalibrated.

## D1.1-05 — Fixed effective cerebral outflow pressure of 5 mmHg

- **Decision.** CPP = max(0, brain arterial pressure − 5 mmHg), replacing
  the Stage 1 subtraction of the central-venous compartment pressure.
- **Rationale.** Central venous pressure in this reduced model is a
  preload-proxy compartment pressure, not the venous pressure opposing
  cerebral outflow; subtracting it coupled the cerebral index to an
  unrelated state. A fixed effective downstream pressure is the smallest
  honest closure.
- **Explicit non-claims.** The 5 mmHg value is **neither thoracic CVP nor a
  resolved ICP**; no intracranial-pressure or venous-sinus state exists.
- **Status.** Implemented and executed: the healthy end-tilt CFI
  reduction is 1.645% at 70 degrees — the Stage 1 miss persists (still
  below the unchanged 3–11% disclosure band) but narrowed from ~0.003%.

## D1.1-06 — Declared end-tidal CO2 input with bounded exponential reactivity

- **Decision.** Add optional per-segment `end_tidal_co2_mmHg`; default
  reference 40 mmHg; cerebral-flow target multiplied by
  `exp(0.035 × clip(ETCO2 − 40, ±15))`.
- **Rationale.** Orthostatic hypocapnia is a documented cerebral-flow
  mechanism that Stage 1 could not express. A declared segment input keeps
  the scenario explicit and auditable.
- **Deliberate restrictions.** (i) **No posture-inferred hypocapnia**—tilt
  never changes ETCO2 by itself; (ii) **ETCO2 is not exact PaCO2**—no
  end-tidal-to-arterial correction is modeled; (iii) the ±15 mmHg clip
  bounds extrapolation of the exponential beyond the supported range.
- **Status.** Implemented and executed; the five cerebral isolation
  protocols confirm separability (pressure-only target 0.98355 with CO2
  factor 1; CO2-only factor 0.70469 with pressure target 1; combined CFI
  0.69310; recovery experiments remain separated).

## D1.1-07 — Retained equations

- **Decision.** The bounded pressure-autoregulation curve, the
  preload/contractility stroke-volume equation, the chronotropic gain split,
  muscle-pump and sustained-contraction mechanics, metabolic/extraction
  constructs, and the PEM cascade are retained unchanged.
- **Rationale.** Stage 1.1 scope is posture geometry, sensor separation,
  flow partition, and the CO2 input; changing calibrated disease semantics
  in the same revision would confound the rerun comparison.
- **Status.** Retained; the Stage 1 misses attached to these equations
  (early-CO, healthy-CFI, PEM onset timing) remain open.

## D1.1-08 — Reporting windows and empirical anchors

- **Decision.** Predefine time-resolved CO/SV/HR reporting windows per
  protocol family and keep the Stage 1 protocol-specific empirical anchors
  unchanged for the 0.3.0 rerun (see `validation-matrix.md`, sections 3–4).
- **Rationale.** Predeclared windows prevent post-hoc window selection when
  the rerun is evaluated; anchors stay fixed so the rerun is a comparison,
  not a re-tuning.
- **Status.** Windows and anchors declared and now populated by the
  executed scenario matrix; all comparisons used the unchanged anchors,
  and all eight Zaidi CO/SV comparisons MISS.

## D1.1-09 — Scope guard

- **Decision.** Stage 1.1 adds no synthetic data generation, no TSFM or
  machine-learning component, and no Stage 2/Stage 3 capability.
- **Status.** Standing; reaffirmed in `readiness-assessment.md`.

## D1.1-10 — Independent-review corrections and scientific disposition

- **Decision.** Require declared ETCO₂ values to be finite and positive, with
  regression cases for NaN, positive and negative infinity, zero, and negative
  values. Correct the technical handoff's opening summary so the current
  five-compartment Stage 1.1 architecture is not described as the historical
  four-compartment Stage 1 architecture.
- **Rationale.** Non-finite ETCO₂ inputs can contaminate the cerebral CO₂
  calculation and are not valid declared observations. Current architecture
  and historical release records must remain unambiguous.
- **Scientific disposition.** The independent review does not establish
  scientific acceptance. The POTS sustained-HR failures, healthy CO/SV
  discrepancies, uncertain baroreflex weighting and pressor response, and
  pressure-versus-CO₂ cerebral-response balance remain unresolved. Focused
  scientific remediation requires separately scoped Stage 1.2 work; Stage 2
  remains held. No equation, parameter, calibration, validation threshold,
  or scientific verdict is changed by these software/documentation fixes.
- **Status.** Corrections implemented; scientific limitations and negative
  results preserved without recalibration or threshold changes.
