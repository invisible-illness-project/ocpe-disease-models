# Stage 1/1.1 technical handoff and Stage 2 readiness

- Release record date: 2026-11-17
- Target branch: `research/initial-disease-modeling-framework`
- Model/package version: 0.3.0 (Stage 1.1; **release validation executed** at the tested commit below — overall seven-layer scientific status **FAIL** from six preserved strict phenotype xfails; the Stage 1 0.2.0 record remains as labeled history)
- Model CURIE: `ocpe:disease-models/shared-physiology`
- Validated source/configuration commit (0.3.0): `a6d7619e277fc05081de3c852189b549d714b8b5`, recorded in `validation/reports/validation-report.json` and `validation/reproducibility.json`; the Stage 1 (0.2.0) commit-bound record at `fb13cb21aa811da9babff6b271f006b8c79ec30f` is preserved in the Stage 1 documents and Git history
- Pinned OCPE commit: `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`
- Original baseline commit: `47923223d4cf2e8a9c6a1ae8cff485b9d4327dc9`

This is computational research software, not a clinically validated model, diagnostic device, treatment system, synthetic wearable dataset, or flare predictor. **Stage 2 has not begun.**

> **Stage 1.1 status banner.** The implementation has advanced to model
> version 0.3.0: twelve states, five conserved stressed-volume compartments
> (adding one residual other-systemic venous path; 25/25/50 baseline flow
> partition; 2550 mL healthy total stressed volume), separate aortic and
> carotid baroreceptor sensors with an integrated weighted baroreflex,
> explicit `tilt_angle_deg` posture geometry with linear angle-only
> transitions, a declared per-segment end-tidal CO2 input (reference
> 40 mmHg, no posture-inferred hypocapnia, ETCO2 not exact PaCO2), and a
> fixed 5 mmHg effective cerebral outflow pressure (neither thoracic CVP
> nor resolved ICP). Stage 1.1 documentation lives in `docs/stage1-1/`.
> **The deterministic 0.3.0 scientific scenario comparison matrix has been
> executed** (`validation/stage1-1/scientific-comparison-matrix.md` /
> `.json`): healthy 70-degree sustained CO −3.105%, SV −12.733%, HR rise
> +7.723 bpm, end-CFI reduction 1.645%; all eight Zaidi 60/70-degree 2/5-min
> CO/SV comparisons MISS their preserved ranges; all four POTS phenotypes
> and Long-COVID-autonomic FAIL the unchanged ≥30 bpm sustained-HR
> criterion (17.428–19.659 bpm); ME/CFS CFI reduction 22.913% remains
> within the unchanged 15–35% band; cerebral pressure/CO2 isolation
> experiments confirm pathway separability. **Release validation for 0.3.0
> is executed** at frozen tested commit
> `a6d7619e277fc05081de3c852189b549d714b8b5`: full suite 323 passed, 1
> skipped (upstream OCPE checkout unavailable; strict installed-engine OCPE
> validation separately passes with 0 errors/0 warnings), 6 xfailed,
> 2 warnings in 344.19s; all seven layer execution statuses PASS; the
> disease-phenotype layer's six strict expected failures keep its
> scientific status and the overall seven-layer scientific status **FAIL**;
> strict traceability passes 0/0/0 and strict OCPE package validation 0/0.
> Sections A and E retain the Stage 1 (0.2.0) executed record as labeled
> history alongside the 0.3.0 record. Version synchronization is complete
> (`pyproject.toml`, `CITATION.cff`, `__init__.py` read 0.3.0). All Stage 1
> misses are preserved and all 0.3.0 negative results are reported, not
> tuned.

## A. Executive summary

Stage 1 replaces the aggregated cardiovascular/autonomic foundation with a conservative four-compartment regional model, differentiated autonomic pathways, explicit rhythmic muscle-pump and sustained-contraction mechanics, and a cerebral-perfusion-pressure-based normalized flow index. The existing phenomenological exertion/PEM cascade is retained, with its contradictory scenario timing corrected and its recovery protocol extended.

All ten phenotype configurations begin at complete supine fixed points. Four-volume conservation holds analytically and in integrated tests. POTS and Long COVID autonomic scenarios are evaluated using sustained final-120-second-upright HR rise rather than peak-only responses. Original fixtures and negative results remain archived.

The Stage 1.1 (0.3.0) commit-bound validation position at tested source/configuration commit `a6d7619e277fc05081de3c852189b549d714b8b5` is:

- **323 tests passed, 1 skipped, 6 xfailed, 2 warnings in 344.19s** in the complete suite; the skip is `tests/unit/test_ocpe_adapter.py:74` (upstream OCPE checkout unavailable in the test environment), and strict installed-engine OCPE validation separately passes with zero errors and zero warnings;
- all seven independently selected validation layers executed with per-layer execution status PASS; the disease-phenotype layer contains six strict expected failures, so its scientific status and the overall seven-layer scientific status are **FAIL** (`validation/reports/validation-report.json` / `.md`);
- the two warnings are the preserved soft-anchor misses: healthy early-CO reduction 0.35% vs the 10–30% band (physiological layer) and healthy end-tilt CFI reduction 1.645% vs the 3–11% band (empirical layer);
- strict traceability passed with zero errors, warnings, and infos on the synchronized 0.3.0 registries;
- strict OCPE package validation passed with zero errors and warnings;
- 59 local-sensitivity executions, 27 deterministic grid scenarios, and three fixed-total chronotropic-split scenarios completed;
- 19 regression tests passed against fixtures regenerated with a Stage 1.1 scientific change record; and
- six demonstrations regenerated 16 persisted 0.3.0 runs.

The Stage 1 (0.2.0) commit-bound validation position below is preserved as history; it was recorded at source/configuration commit `fb13cb21aa811da9babff6b271f006b8c79ec30f`:

- **287 unique tests passed** in the complete suite, with two intended soft-anchor warnings (`287 passed, 2 warnings in 250.94s (0:04:10)`) (Stage 1 historical record);
- all seven independently selected validation layers passed (Stage 1 historical record);
- all 26 validation-registry records are PASS and bound to that tested source commit (Stage 1 historical record);
- strict traceability passed with zero errors, warnings, and infos;
- strict OCPE package validation passed with zero errors and warnings;
- Ruff passed;
- 42 local-sensitivity executions, 18 deterministic grid scenarios, and three fixed-total chronotropic-split scenarios completed (Stage 1 historical record); and
- six demonstrations regenerated 16 persisted current-model runs (Stage 1 historical record).

The subsequent validation-record commit adds these executed records and does not claim to have been tested before it existed.

Two healthy empirical soft-anchor misses remain. In the Stage 1 (0.2.0) historical record, early CO reduction was approximately 5.64%, below the broad 10–30% plausibility band, and end-tilt cerebral-flow-index reduction was approximately 0.003%, below the broad 3–11% band around the reported 7% control finding, while heart-level MAP rose approximately 17.4 mmHg to 117.4 mmHg. At 0.3.0 both misses persist, re-measured: the early-CO warning is 0.35% against the unchanged 10–30% band (with sustained CO −3.105% and all eight Zaidi CO/SV comparisons MISS), the end-tilt CFI warning is 1.645% against the unchanged 3–11% band, and the healthy 70-degree upright-end MAP of ~111.332 mmHg remains a disclosed fidelity limitation rather than a validated healthy MAP response. All are reported as warnings and unresolved structural limitations, not concealed by calibration.

## B. Scientific findings and interpretation

The focused review supports separate splanchnic and lower-limb pooling paths, pressure-gradient-driven venous return, rhythmic muscle-pump transfer, sustained-contraction impediment, faster vagal than sympathetic cardiac control, distinguishable cardiac and vascular sympathetic pathways, head-level cerebral perfusion pressure, and dynamic cerebral autoregulation. It also preserves constraining findings: tilt and LBNP are not interchangeable, muscle pump is not the sole mechanism of exercise CO augmentation, and regional impedance/TCD surrogates are not absolute volume or flow measurements.

The model does not infer CO₂-mediated cerebral vasomotor effects from posture: only a declared ETCO₂ input activates the bounded CO₂ pathway, without an end-tidal-to-arterial correction. It also does not resolve renal/endocrine volume regulation, patient-specific regional compliances, or unique autonomic gains. Disease configurations remain calibrated computational scenarios. POTS threshold agreement has calibration overlap and is not independent validation. The hEDS venous-compliance value remains exploratory and M2. PEM remains a normalized phenomenological construct rather than a molecular or symptom-score model. Its first 0.05 crossing at approximately 5.7 hours after the day-1 bout ends is earlier than the 12–48-hour daily-activity onset window, although within reported post-CPET onset within 24 hours; the approximately 39.2-hour post-bout peak is a separate, compatible timing result.

Detailed records are:

- `docs/stage1/baseline-scientific-report.md`
- `docs/stage1/literature-and-evidence-matrix.md`
- `docs/stage1/revised-physiological-architecture.md`
- `docs/stage1/parameter-provenance-and-uncertainty.md`
- `docs/stage1/final-validation-report.md`
- `docs/stage1-1/architecture-design-record.md` (Stage 1.1)
- `docs/stage1-1/scientific-decision-log.md` (Stage 1.1)
- `docs/stage1-1/validation-matrix.md` (Stage 1.1; executed at commit `a6d7619`, overall scientific status FAIL)
- `docs/stage1-1/readiness-assessment.md` (Stage 1.1)

## C. Implemented architecture

The current implementation (model version 0.3.0) has 12 states:

1. arterial stressed volume;
2. central-venous stressed volume/preload proxy;
3. splanchnic-venous stressed volume;
4. lower-limb-venous stressed volume;
5. other-systemic (residual) venous stressed volume;
6. cardiac-sympathetic state;
7. vascular-sympathetic state;
8. vagal state;
9. exertional load;
10. delayed stress;
11. PEM severity; and
12. normalized cerebral-flow index.

The five volume derivatives telescope exactly:

`dVa/dt + dVc/dt + dVs/dt + dVl/dt + dVo/dt = 0`.

The healthy baseline partitions systemic flow 25% splanchnic / 25% lower-limb / 50% other-systemic at a 2550 mL total stressed volume, implemented by doubling the splanchnic/lower-limb resistances and assigning their former values to the other-systemic path (defaults and the three POTS YAMLs with explicit resistance overrides). Rhythmic activity transfers lower-limb venous volume to the central compartment without creating blood. Sustained contraction independently increases lower-limb venous resistance. Cardiac sympathetic activity controls contractility and chronotropy, vascular sympathetic activity controls regional arterial resistances, and vagal activity contributes separately to HR.

Posture is an explicit `tilt_angle_deg` (legacy `upright` migrates via `arcsin`; transitions are linear in angle only), and hydrostatic terms are heights in cm converted at 0.7356 mmHg/cm and scaled by sin(angle). The baroreflex integrates a weighted error (default 0.25/0.75) from separate aortic (0 cm) and carotid (25 cm) sensors with independent setpoints/scales; brain-level pressure (27 cm) is a distinct parameter used only by the cerebral path. Cerebral perfusion pressure subtracts a fixed effective outflow pressure of 5 mmHg—neither thoracic CVP nor a resolved ICP—and the cerebral target is further modulated by a declared segment ETCO2 via exp(0.035 × clip(ETCO2 − 40, ±15)). The bounded pressure-autoregulation curve and the preload/contractility stroke-volume equations are retained from Stage 1.

There are no disease-specific conditional branches in the shared equations. Phenotype YAML files supply registered parameters; protocol YAML files independently declare posture, `exertion`, `rhythmic_muscle_activity`, `sustained_muscle_contraction`, and `end_tidal_co2_mmHg`.

OCPE supplies semantics, identifiers, units, specifications, evidence integrity, strict package validation, and observation exchange. SciPy DOP853 supplies numerical integration in this repository. No solver was added to upstream OCPE.

## D. Entry points and reproducible outputs

Primary entry points:

- `scripts/simulate.py` for one configured run;
- `scripts/run_examples.py` for all six demonstrations;
- `scripts/run_sensitivity.py` for local, grid, and chronotropic-split analyses;
- `scripts/run_validation.py` for independent seven-layer reporting; and
- `scripts/audit_traceability.py --root . --strict` for registry/provenance auditing.

Each persisted run records the exact resolved parameters, protocol, configuration SHA-256, model and OCPE versions, Python/NumPy/SciPy versions, and solver method, sampling interval, maximum step, relative/absolute tolerances, and seed. NPZ traces contain the 12 states and derived outputs; JSON results contain metadata and summaries; OCPE observations contain sparse mapped values, not waveforms.

The simulation registry contains 19 protocols and 11 curated simulation records at 0.3.0 (the Stage 1 record held nine protocols and eight simulation records). Six demonstrations regenerate 16 result/observation/trace sets and their figures. These are small validation artifacts, not patient cohorts or machine-learning datasets.

## E. Validation results

**Stage 1.1 (0.3.0) executed record, bound to tested commit `a6d7619e277fc05081de3c852189b549d714b8b5`** (`validation/reports/validation-report.json` / `.md`; full suite 323 passed, 1 skipped, 6 xfailed, 2 warnings in 344.19s):

| Layer | Execution status | Scientific status | Result | Scope |
|---|---|---|---|---|
| Software | PASS | PASS | 127 passed, 1 skipped, 202 deselected in 198.15s | Configuration, serialization, failure handling, OCPE mapping, declarative/executable consistency, and regression (19 regression tests). The skip is `tests/unit/test_ocpe_adapter.py:74` (upstream OCPE checkout unavailable); strict installed-engine OCPE validation passes separately with 0 errors/0 warnings |
| Mathematical | PASS | PASS | 45 passed, 285 deselected in 9.33s | Five-volume conservation, ten fixed points, identities, bounds, and convergence |
| Physiological | PASS | PASS | 64 passed, 266 deselected, 1 warning in 8.15s | Orthostasis, recovery, autonomic separation, muscle mechanics, CPP/CFI, and soft anchors; the warning is the preserved healthy early-CO miss (0.35% vs the 10–30% band) |
| Disease phenotype | PASS | **FAIL** | 29 passed, 295 deselected, 6 xfailed in 186.51s | POTS, hEDS, ME/CFS, and Long COVID configurations; six strict expected failures preserve five unchanged ≥30 bpm sustained-HR criterion misses (all four POTS phenotypes and Long-COVID-autonomic); the graded-tilt empirical anchor miss is reported separately |
| Empirical | PASS | PASS | 10 passed, 320 deselected, 1 warning in 96.46s | Heterogeneous group-level plausibility comparisons; the warning is the preserved healthy-CFI miss (1.645% vs the 3–11% band); the eight Zaidi CO/SV MISSes are recorded in the scientific comparison matrix |
| Sensitivity/uncertainty | PASS | PASS | 13 passed, 317 deselected in 124.91s | Regional, muscle, autonomic, cerebral, CO2, grid, and split analyses (59 local, 27 grid, 3 split scenarios) |
| Scientific traceability | PASS | PASS | 40 passed, 290 deselected in 4.16s | Registry integrity, scientific chains, scope guards, and bibliography synchronization; strict audit 0 errors/0 warnings/0 infos |

**Overall seven-layer scientific status: FAIL** — the six strict phenotype xfails are preserved scientific failures, not passes; per-layer execution PASS does not convert them.

**The table below is the executed Stage 1 (0.2.0) record, bound to its tested commit, preserved as history.**

| Layer | Result | Scope |
|---|---:|---|
| Software | 122 passed | Configuration, serialization, failure handling, OCPE mapping, declarative/executable consistency, and regression |
| Mathematical | 44 passed | Four-volume conservation, ten fixed points, identities, bounds, and convergence |
| Physiological | 29 passed, 1 warning | Orthostasis, recovery, autonomic separation, muscle mechanics, CPP/CFI, and soft anchors |
| Disease phenotype | 35 passed | POTS, hEDS, ME/CFS, and Long COVID configurations |
| Empirical | 9 passed, 1 warning | Heterogeneous group-level plausibility comparisons and healthy cerebral-control miss |
| Sensitivity/uncertainty | 13 passed | Regional, muscle, autonomic, cerebral, grid, and split analyses |
| Scientific traceability | 40 passed | Registry integrity, scientific chains, scope guards, and bibliography synchronization |

Layer counts include dual-marked tests and therefore exceed the unique full-suite total when summed. Empty required selections fail by design. Exact elapsed times and commands are in `validation/reports/`.

The Stage 1 regression fixture contains 16 runs and a scientific change record; the Stage 1.1 fixture regeneration (19 regression tests passed at 0.3.0) carries its own Stage 1.1 scientific change record. The original fixture and original validation snapshot under `validation/baseline/stage0/` are byte-identical to their baseline versions. No test criterion was weakened to hide the early-CO or healthy-CFI results, restore healthy CO in hypovolemia, or substitute peak-only POTS responses. The healthy-CFI control miss has its own warning; the ME/CFS 15–35% scenario band is unchanged.

## F. Scientific confidence and maturity

Confidence is strongest in software integrity, exact conservation, fixed-point accounting, deterministic reproducibility, and explicit provenance. It is weaker in absolute parameter identification, structural uncertainty, disease heterogeneity, and generalization beyond demonstrated scenarios.

Evidence grades E0–E5 and maturity M0–M4 remain independent. Execution alone does not establish clinical maturity. No integrated disease model is assigned M4 from these results. Group-level empirical anchors overlap with calibration and are not prospective external validation. The early-CO and healthy-CFI misses, early PEM threshold-crossing caveat, reduced-order preload proxy, clipped flows, linear compliances, absent end-tidal-to-arterial CO₂ correction, and absent renal/endocrine volume-regulation mechanisms remain material limitations.

## G. Stage 2 technical handoff and readiness

### Available computational contract

A separately approved Stage 2 project may use the shared simulator as a deterministic source of latent beat-averaged states and derived outputs. The usable contract is:

- inputs: phenotype IDs, explicit protocol segments, resolved `ModelParameters`, and solver settings;
- outputs: time in seconds, 12 states, regional pressures/flows, HR, SV, CO, CPP/CFI, capacity/extraction, and PEM constructs;
- persistence: compressed NPZ plus JSON parameters/metadata/summaries and optional sparse OCPE observations;
- traceability: configuration hash, model version, OCPE commit, solver settings, and registry-linked parameters/validations.

Stage 2 must not treat deterministic sensitivity rows as patients, assign them prevalence or probabilities, or interpret normalized states as measured clinical scores. Shared-equation changes require a new Stage 1-style scientific review and validation cycle rather than being embedded in a sensor generator.

### Missing prerequisites

No raw ECG, PPG, HRV, respiratory, temperature, electrodermal, or accelerometry waveform is generated. There is no sampling/aliasing model, motion artifact, sensor bias/drift/dropout model, device-specific error model, reference measurement, cohort design, governance process, or wearable agreement analysis.

| Capability | Readiness at Stage 1 handoff |
|---|---|
| Deterministic latent physiological scenarios | Available for research use, with declared structural/calibration limitations |
| OCPE semantic mapping | Available for sparse declared observations; strict validation passes |
| Waveform and beat-level observation models | Missing |
| Sensor/device error and artifact models | Missing |
| Synthetic cohort design and governance | Missing |
| Wearable agreement validation (ICC/CCC/Bland–Altman or equivalent) | Missing |
| Clinically meaningful synthetic wearable dataset | **Not ready** |

Before Stage 2 implementation, a separate protocol must define intended use, channels, sampling and time synchronization, observation mappings, sensor/reference error structure, cohort and phenotype sampling assumptions, governance, held-out evaluation, and agreement criteria. It must explicitly address the unresolved healthy early-CO and healthy-CFI misses and the PEM onset-window caveat, and avoid converting calibrated scenario thresholds into ground-truth diagnostic labels.

Accordingly, the repository is **ready for reviewed Stage 2 planning, not automatic Stage 2 execution**. No Stage 2 dataset or sensor model is included here.

## H. Stage 3 compatibility

Stage 3 flare prediction is also excluded. No forecasting model, symptom label, TSFM, machine-learning cohort, patient-facing prediction, or treatment recommendation is supplied. Longitudinal protocols may provide research inputs only after outcomes, labels, missingness, governance, validation splits, calibration, and clinical utility are independently specified. File-format compatibility is not readiness for flare prediction.

## I. Baseline and migration record

The unmodified Stage 0 behavior is documented in `docs/stage1/baseline-scientific-report.md`. Archived materials under `validation/baseline/stage0/` include the original regression fixture, original validation snapshot, environment, and fresh baseline test log. Historical failed physiological regimes and legacy negative findings remain historical evidence; they are not rewritten as current successes or deleted.

At the Stage 1 (0.2.0) record, the declarative OCPE package describes the same 11 states, 52 parameters, four protocol inputs, equations, units, and outputs as the executable implementation. Synchronization of the declarative package and registries to the 0.3.0 revision (12 states, five volumes, the renamed/added parameters, and the new protocols) is **complete**: the strict traceability audit passes with zero errors, warnings, and infos, and strict OCPE package validation passes with zero errors and zero warnings; see `docs/stage1-1/readiness-assessment.md`. The legacy short identifier `three-compartment-cardiovascular` is retained only as an alias; the canonical CURIE is `ocpe:disease-models/shared-physiology`.

## J. Traceability

The implemented chain is:

`reference → evidence claim → mechanism → equation → parameter → implementation → validation test → simulation output`.

The 0.3.0 registries contain 69 references, 41 evidence claims, 24 mechanisms, 22 equations, 68 parameters, 29 validation records (23 PASS, 6 FAIL, 0 PENDING — the FAILs are the five sustained-HR criterion records and the graded-tilt anchor record, preserved negative results), 19 protocols, and 11 simulation records; the Stage 1 (0.2.0) registries contained 64 references, 37 evidence claims, 23 mechanisms, 20 equations, 52 parameters, 26 validation records, nine protocols, and eight simulation records (preserved history). The BibTeX export contains all 69 references and has a synchronization test. Canonical reports are `validation/traceability/audit/traceability_report.json` and `.md`. Record integrity does not establish mechanism truth or clinical validity.

## K. Validation-system assessment

The validation system is suitable for a small, auditable research framework because it separates software, mathematics, physiology, disease scenarios, empirical plausibility, sensitivity, and provenance. It preserves negative results, rejects empty required selections, and records exact configurations and source revisions.

Its principal weaknesses remain scientific: assumed/calibrated parameters, calibration overlap, limited structural and global uncertainty analysis, heterogeneous group-level anchors, omitted physiology, source-checkout packaging requirements, and local rather than verified remote CI results. A green suite supports reproducible computational scrutiny, not diagnosis, prognosis, treatment selection, severity ranking, or patient-specific inference.

## L. Operational and security handoff

Scientific changes follow `docs/scientific-change-management.md`. Equation, parameter, evidence, phenotype, fixture, and maturity changes require linked provenance and appropriate review. Rollback should use reviewed Git reverts rather than destructive history changes. Any later source/configuration change requires a new validation cycle.

`validation/reproducibility.json` distinguishes the tested source/configuration commit from the subsequent validation-record commit that adds executed reports, regenerated outputs, registry results, and this handoff. It does not claim that a later commit was tested before it existed.

Security notes:

- upstream OCPE remains at its pinned commit and is not modified by this remediation;
- no PAT, token, credential, private key, or temporary secret may be committed or included in artifacts;
- CI uses read-only contents permission, disables persisted checkout credentials, and requires no secrets;
- publication uses the explicitly authorized secure repository operation; and
- the temporary PAT supplied for repository operations should be revoked or rotated after use.

Stage 2 sensor modeling and Stage 3 prediction require separate approval and scientific/engineering work. Neither is started by this handoff.
