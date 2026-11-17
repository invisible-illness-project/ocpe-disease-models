# Stage 1.1 readiness assessment

- Model CURIE: `ocpe:disease-models/shared-physiology`
- Model version under assessment: **0.3.0** (12 states, five volumes)
- Assessment basis: the 0.3.0 **scientific scenario comparison matrix has
  been executed** (`validation/stage1-1/scientific-comparison-matrix.md` /
  `.json`), and the **Stage 1.1 release validation cycle is complete** at
  frozen tested source commit `a6d7619e277fc05081de3c852189b549d714b8b5`:
  the full suite ran **323 passed, 1 skipped
  (`tests/unit/test_ocpe_adapter.py:74`, upstream OCPE checkout unavailable;
  strict installed-engine OCPE validation separately passes with 0
  errors/0 warnings), 6 xfailed, 2 warnings in 344.19s**; the seven-layer
  report is `validation/reports/validation-report.json` / `.md`
  (`model_version: 0.3.0`, `repository_commit: a6d7619`); strict
  disease-models OCPE validation passes with 0 errors/0 warnings and the
  strict traceability audit passes with 0 errors/0 warnings/0 infos. All
  seven layer **execution** statuses are PASS; the disease-phenotype layer
  carries six strict expected failures, so its scientific status and the
  **overall seven-layer scientific status are FAIL**. Version
  synchronization is complete (`pyproject.toml`, `CITATION.cff`, and
  `__init__.py` read 0.3.0).

This is computational research software, not a clinically validated model,
diagnostic device, treatment system, synthetic wearable dataset, or flare
predictor. **Stage 2 has not begun. Stage 3 is excluded.**

## 1. Overall readiness statement

| Question | Answer |
|---|---|
| Is the 0.3.0 architecture recorded and reviewable? | Yes — `architecture-design-record.md`, `scientific-decision-log.md` |
| Is the 0.3.0 implementation executable? | Yes — the deterministic scientific scenario matrix executed with recorded configuration SHA-256 and solver metadata per run |
| Do 0.3.0 scientific scenario results exist? | **Yes** — graded-tilt, standing, cerebral CO2 isolation, empirical CO/SV comparisons, and phenotype sustained-HR outcomes; reported in `validation-matrix.md` §§4–6 including all negative outcomes |
| Are 0.3.0 results validated in the release sense? | **Yes, executed — with an overall scientific FAIL.** The full suite (323 passed, 1 skipped, 6 xfailed, 2 warnings in 344.19s), the seven-layer runner, the strict traceability audit (0/0/0), and strict OCPE package validation (0/0) all executed at tested commit `a6d7619`; per-layer execution status is PASS in all seven layers, while the disease-phenotype layer's six strict expected failures keep its scientific status and the overall seven-layer status FAIL. The Stage 1 287-test record remains bound to the 0.2.0 tested commit as history |
| Are Stage 1 misses resolved? | **No.** The healthy CO/SV miss persists (sustained CO −3.105% at 70 degrees; all eight Zaidi comparisons MISS); the healthy CFI miss persists but narrowed (1.645% vs the unchanged 3–11% band); **new negative result**: all four POTS phenotypes and Long-COVID-autonomic FAIL the unchanged ≥30 bpm sustained-HR criterion |
| Is the repository ready for Stage 2 execution? | **No.** Stage 1 readiness for reviewed Stage 2 *planning* carried over; Stage 1.1 does not change any Stage 2 prerequisite |

## 2. Component readiness

| Component | State | Readiness |
|---|---|---|
| Five-volume conservation structure | Implemented in source | **Verified** — mathematical layer executed: 45 passed, 285 deselected in 9.33s (five-volume telescoping, fixed points of all ten configurations) |
| 25/25/50 baseline flow partition, 2550 mL total stressed volume | Implemented in defaults and three POTS phenotype YAMLs | Scenario matrix baselines consistent (healthy baseline CO 81.667 mL/s, MAP 100 mmHg); fixed-point verification executed in the mathematical layer |
| Hydrostatic heights (0.7356 mmHg/cm × sin θ) | Implemented; legacy offsets migrated exactly | **Executed in scenario matrix**: graded HR rise 3.626/5.417/6.954/7.723 bpm and end-CFI reduction 0.819/1.192/1.497/1.645% across 30/45/60/70 degrees |
| Explicit `tilt_angle_deg` + arcsin legacy migration + linear angle-only transitions | Implemented; mutual-exclusion and range validation present | **Executed** (`head-up-tilt` and `passive-tilt-70` yield equivalent reported metrics under their declared solver sample grids); software layer executed: 127 passed, 1 skipped |
| New protocols (passive-tilt-30/45/60/70, active-standing with sustained quiet standing, tilt-back recovery, five cerebral CO2 protocols) | YAMLs present; executed in the scenario matrix | **Registered and executed** — 19 protocols and 11 simulation records in the synchronized simulation registry; six demonstrations regenerated 16 persisted 0.3.0 runs; layer test coverage executed |
| Dual aortic/carotid sensors, integrated weighted baroreflex (0.25/0.75, sum-to-1 enforced) | Implemented; brain pressure (27 cm) kept distinct | Executed in scenario matrix; **all POTS/Long-COVID-autonomic phenotypes FAIL the unchanged ≥30 bpm sustained-HR criterion** (17.428–19.659 bpm) — preserved negative result |
| Segment ETCO2 input (reference 40 mmHg; exp(0.035 × clip(Δ, ±15))) | Implemented; no posture-inferred hypocapnia; ETCO2 ≠ PaCO2 by declaration | **Executed**: pressure-only pressure target 0.98355 / CO2 factor 1; CO2-only (ETCO2 30) pressure target 1 / CO2 factor 0.70469; combined CFI 0.69310; persistent-hypocapnia and persistent-pressure-reduction recovery experiments remain separated |
| Fixed effective cerebral outflow pressure (5 mmHg; neither thoracic CVP nor resolved ICP) | Implemented | Executed; healthy end-CFI reduction 1.645% remains below the unchanged 3–11% disclosure band (Stage 1 miss persists, narrowed) |
| Registry/declarative-package synchronization to 0.3.0 names and counts | **Complete** | Strict traceability audit passes 0 errors/0 warnings/0 infos on the synchronized registries (69 references/BibTeX entries, 41 evidence claims, 24 mechanisms, 22 equations, 68 parameters, 29 validation records — 23 PASS / 6 FAIL / 0 PENDING, 19 protocols, 11 simulation records); strict disease-models OCPE validation passes 0 errors/0 warnings |
| Package version strings | **Done** — `pyproject.toml`, `CITATION.cff`, and `src/ocpe_disease_models/__init__.py` read 0.3.0, matching run metadata `model_version: 0.3.0` | Complete |
| Sensitivity export | Local CO2-reactivity and CO2-clip scenarios and a CO2-reactivity × cerebral-outflow grid added | **Complete** — 59 local, 27 grid, and 3 chronotropic-split scenarios regenerated; 13 sensitivity tests passed (317 deselected in 124.91s) |
| Regression fixtures | Regenerated with a Stage 1.1 structural-change record and unchanged tolerances | **Complete** — 19 regression tests passed; negative POTS outcomes remain recorded as failures |

## 3. Carried-over readiness position (Stage 1, unchanged)

The Stage 2 technical-handoff capability table is unchanged in substance:
deterministic latent physiological scenarios and sparse OCPE observation
mapping remain the only available capabilities; waveform/beat-level
observation models, sensor error and artifact models, synthetic cohort
design and governance, and wearable agreement validation remain missing.
Stage 1.1 adds a declared ETCO2 input and richer posture geometry but no
waveform, sensor, or cohort capability.

## 4. Key unresolved scientific limitations

1. **Preserved Stage 1 misses, re-measured at 0.3.0** (details in
   `validation-matrix.md` §§4–5): the healthy CO/SV orthostatic miss
   persists — sustained CO −3.105% and SV −12.733% at 70 degrees, with all
   eight Zaidi 60/70-degree 2/5-min CO/SV comparisons outside their
   preserved published ranges (MISS); the healthy end-tilt CFI miss
   persists but narrowed — 1.645% vs the unchanged 3–11% disclosure band
   around the ~7% control finding; the PEM onset-timing caveat stands
   (PEM equations unchanged; scenario checks re-executed in the full
   suite); historical hEDS
   below-70-mmHg grid failures remain archived and the mechanism stays M2.
2. **New 0.3.0 negative result:** all four POTS phenotypes (neuropathic
   17.428, hyperadrenergic 19.659, hypovolemic 19.399, mixed 19.216 bpm)
   and Long-COVID-autonomic (18.931 bpm) FAIL the unchanged ≥30 bpm
   sustained-HR-rise scenario criterion that the 0.2.0 calibrated scenarios
   met. No gain was recalibrated and no threshold was widened; the failure
   indicates the dual-sensor integrated baroreflex and re-partitioned
   resistances materially changed sustained chronotropic compensation, and
   resolving it requires reviewed scientific work, not parameter tuning to
   the threshold.
3. **New computational assumptions without direct measurement:** the
   0.25/0.75 aortic/carotid baroreflex weights, the 0/25/27 cm sensor and
   brain heights, the fixed 5 mmHg effective cerebral outflow pressure, the
   ±15 mmHg CO2 extrapolation clip, the 0 cm other-systemic hydrostatic
   height, and the 25/25/50 partition as a baseline operating point.
4. **CO2 pathway simplifications:** ETCO2 is consumed as declared, is not
   exact PaCO2, has no end-tidal-to-arterial correction, and no
   posture-inferred hypocapnia exists—so orthostatic hypocapnia scenarios
   depend entirely on declared segment values.
5. **Cerebral outflow closure:** the fixed 5 mmHg effective downstream
   pressure is deliberately neither thoracic CVP nor a resolved ICP; no
   intracranial-pressure dynamics exist. The executed cerebral experiments
   show the declared CO2 pathway dominates the CFI response in this
   structure (0.70469 CO2-only vs 0.98355 pressure-only), which bounds how
   much orthostatic cerebral-flow reduction the pressure pathway alone can
   express.
6. **CFI remains a normalized research proxy**, not measured CBF or MCA
   velocity, with no vascular territories.
7. **Unidentified chronotropic gain split** at fixed total gain (carried
   from Stage 1) and calibration overlap of the POTS sustained-HR scenario
   criterion.
8. **Single residual compartment lumping:** all non-splanchnic,
   non-lower-limb venous volume is one compartment with a 0 cm hydrostatic
   height; this is a modeling closure, not anatomy.
9. **Release verification is executed; the open items are scientific and
   operational, not executional.** The full test suite, strict
   traceability audit, strict OCPE package validation, regression-fixture
   regeneration, sensitivity export, demonstrations, and seven-layer
   report have all been executed for 0.3.0 at tested commit `a6d7619`
   (full suite 323 passed, 1 skipped, 6 xfailed, 2 warnings in 344.19s;
   overall seven-layer scientific status **FAIL** from the preserved
   strict phenotype xfails). The executed negative results (8 Zaidi
   MISSes, 5 sustained-HR criterion FAILs, persistent healthy CO/SV and
   CFI misses, early-CO 0.35% and healthy-CFI 1.645% warnings) are carried
   into the release report unchanged. Remote CI execution on Python
   3.11/3.12 remains unclaimed — local execution is not a substitute.

## 5. Conditions to advance readiness

Release-cycle conditions **met** at tested commit `a6d7619`:

1. Registries and the declarative OCPE package are synchronized to 0.3.0
   (parameters, equations, states, protocols, simulations) and the strict
   traceability audit passes with zero errors, warnings, and infos.
   (Version-string synchronization was completed earlier.)
2. Regression fixtures were regenerated with a documented scientific
   change record (19 regression tests passed); the 0.2.0 fixtures are
   preserved in Git history and the Stage 0 originals remain unchanged.
3. The sensitivity regeneration is complete and reviewed (59 local, 27
   grid, 3 chronotropic-split scenarios; 13 sensitivity tests passed).
4. The full seven-layer validation suite executed on the recorded
   source/configuration commit `a6d7619`, including the new protocol
   families, and carried the executed negative results (8 Zaidi MISSes, 5
   sustained-HR criterion FAILs, persistent healthy CO/SV and CFI misses)
   into the release report unchanged against their unchanged bands. All
   seven layer execution statuses are PASS; the overall scientific status
   is FAIL because the six strict phenotype xfails are preserved
   scientific failures, not passes.

Conditions that **remain open**:

5. Address the POTS sustained-HR criterion failure through reviewed
   scientific work (mechanism or evidence analysis), not threshold
   widening or gain tuning to pass.
6. Verify remote CI on Python 3.11 and 3.12; local execution is not a
   substitute for successful remote runs, and no remote run is claimed.
7. Only then reconsider the maturity of any mechanism or phenotype; no
   Stage 1.1 change by itself raises any maturity level, and nothing here
   begins Stage 2 or Stage 3.
