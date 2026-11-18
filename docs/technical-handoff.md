# Stage 1/1.1/1.2 technical handoff and Stage 2 readiness

- Current remediation record date: 2026-11-18
- Target branch: `research/initial-disease-modeling-framework`
- Model/package version: 0.3.0 (Stage 1.1 architecture with Stage 1.2 scientific remediation; overall scientific readiness **PARTIAL**)
- Model CURIE: `ocpe:disease-models/shared-physiology`
- Tested Stage 1.2 source/documentation commit: `e0c7362f6d0390b64d141e44cdc0c6b3000511e1`, recorded in `validation/reports/validation-report.json` and `validation/reproducibility.json`; the subsequent release-record commit adds generated records without claiming to have been tested before it existed
- Stage 1.2 exact base: `f85360d8337144e118eb0d2aef317fd1b949b3dd`
- Pinned OCPE commit: `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`
- Original baseline commit: `47923223d4cf2e8a9c6a1ae8cff485b9d4327dc9`

This is computational research software, not a clinically validated model, diagnostic device, treatment system, synthetic wearable dataset, or flare predictor. **Stage 2 has not begun.**

> **Current Stage 1.2 status.** The implementation retains Stage 1.1's twelve states, five conserved stressed-volume compartments, residual other-systemic path, separate aortic/carotid sensors, integrated weighted baroreflex, explicit angle geometry, three autonomic effector states, and independent cerebral pressure/declared-CO2 pathways. Stage 1.2 changed only effective regional heights and the cerebral autoregulation residual slope in the shared model; POTS chronotropic gains and all scientific criteria are unchanged. Current evidence is in `docs/stage1-2/` and `validation/stage1-2/`. Healthy early CO reduction is 14.570%, sustained HR rise 15.467 bpm, pooling 302.962 mL, and CFI reduction 4.407%. All four POTS configurations and Long-COVID-autonomic pass the sustained ≥30 bpm scenario criterion with MAP floors above 70 mmHg. Six of eight Zaidi comparisons pass; the two remaining 60° CO misses are explicit. ME/CFS CFI reduction is 24.652%, within 15–35%. Full-suite execution is 343 passed and 1 skipped; strict traceability and strict OCPE validation each report zero errors/warnings. These results do not establish clinical validity. Stage 1.1 and Stage 1 records remain preserved history.

## A. Executive summary

Stage 1.2 remediated the Stage 1.1 zero-height residual-bed preload bypass and its downstream suppression of orthostatic CO/SV loss, POTS chronotropy, and cerebral-flow reduction. All ten phenotype configurations still begin at complete supine fixed points. Five-volume conservation holds analytically and in integrated tests. POTS and Long COVID autonomic scenarios are evaluated using sustained final-120-second-upright HR rise rather than peak-only responses.

The current commit-bound execution position is:

- **343 tests passed, 1 skipped in 351.62s** in the complete suite; the skip is the environment-dependent upstream-OCPE-checkout adapter test, while strict installed-engine OCPE validation separately passes with zero errors and zero warnings;
- all seven independently selected validation layers execute successfully, with current machine-readable results in `validation/reports/validation-report.json` / `.md`;
- all four POTS configurations and Long-COVID-autonomic pass directly, with no scientific expected failures;
- healthy early CO and CFI now lie within their preserved broad bands;
- strict traceability passes with zero errors, warnings, and infos;
- 61 local-sensitivity executions, 27 deterministic grid scenarios, and three fixed-total chronotropic-split scenarios completed;
- 19 regression tests passed against fixtures regenerated with a Stage 1.2 scientific change record; and
- six demonstrations regenerated 16 persisted 0.3.0 runs.

The two residual 60° CO misses remain `VAL-PHYS-GRADED-TILT` scientific failures even though executable tests pass. Healthy end-tilt MAP is 108.846 mmHg versus 100 mmHg supine, pooling clears its lower band edge by only 2.962 mL, and ME/CFS/hEDS/Long-COVID-autonomic retain un-recalibrated Stage 1.1 caudal-geometry overrides. These are material limitations, not concealed calibration successes. Earlier Stage 1.1 and Stage 1 results remain commit-bound history in their respective documents and Git records.

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
- `docs/stage1-1/validation-matrix.md` (Stage 1.1; executed at commit `942713e`, overall scientific status FAIL)
- `docs/stage1-1/readiness-assessment.md` (Stage 1.1)
- `docs/stage1-2/scientific-decision-log.md` (current remediation)
- `docs/stage1-2/readiness-assessment.md` (current partial readiness)
- `validation/stage1-2/scientific-comparison-matrix.md` / `.json` (executed before/after evidence)

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

**Current Stage 1.2 executed record, bound to tested source/documentation commit `e0c7362f6d0390b64d141e44cdc0c6b3000511e1`:** full suite 343 passed, 1 skipped in 351.62s; exact seven-layer selections, elapsed times, commands, and per-layer statuses are in `validation/reports/validation-report.json` / `.md` and `validation/reproducibility.json`. The disease-phenotype criteria now pass directly. The graded-tilt registry record remains **FAIL** because two 60° CO comparisons miss; overall scientific readiness is **PARTIAL**. Layer execution PASS does not erase empirical MISS rows.

The Stage 1.1 executed record at `942713ef720ad0e801e71bf9bc78405cd844a739` (327 passed, 1 skipped, 6 xfailed; overall scientific status FAIL) is preserved in `docs/stage1-1/` and `validation/stage1-1/`, not represented as current.

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

The Stage 1 regression fixture contains 16 runs and a scientific change record; the current fixture regeneration carries a Stage 1.2 scientific change record and passes 19 regression tests. Historical fixtures and validation snapshots remain preserved. No criterion was weakened to hide orthostatic CO/SV/CFI results, restore healthy CO in hypovolemia, or substitute peak-only POTS responses. The ME/CFS 15–35% scenario band is unchanged.

## F. Scientific confidence and maturity

Confidence is strongest in software integrity, exact conservation, fixed-point accounting, deterministic reproducibility, and explicit provenance. It is weaker in absolute parameter identification, structural uncertainty, disease heterogeneity, and generalization beyond demonstrated scenarios.

Evidence grades E0–E5 and maturity M0–M4 remain independent. Execution alone does not establish clinical maturity. No integrated disease model is assigned M4 from these results. Group-level empirical anchors overlap with calibration and are not prospective external validation. The residual 60° CO misses, MAP over-defence, narrow pooling margin, calibration overlap, retained non-POTS geometry, early PEM threshold-crossing caveat, reduced-order preload proxy, clipped flows, linear compliances, absent end-tidal-to-arterial CO₂ correction, and absent renal/endocrine volume-regulation mechanisms remain material limitations.

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

Before Stage 2 implementation, a separate protocol must define intended use, channels, sampling and time synchronization, observation mappings, sensor/reference error structure, cohort and phenotype sampling assumptions, governance, held-out evaluation, and agreement criteria. It must explicitly address the residual 60° CO misses, healthy MAP over-defence, narrow pooling margin, and PEM onset-window caveat, and avoid converting calibrated scenario thresholds into ground-truth diagnostic labels.

Accordingly, the repository is **ready for reviewed Stage 2 planning, not automatic Stage 2 execution**. No Stage 2 dataset or sensor model is included here.

## H. Stage 3 compatibility

Stage 3 flare prediction is also excluded. No forecasting model, symptom label, TSFM, machine-learning cohort, patient-facing prediction, or treatment recommendation is supplied. Longitudinal protocols may provide research inputs only after outcomes, labels, missingness, governance, validation splits, calibration, and clinical utility are independently specified. File-format compatibility is not readiness for flare prediction.

## I. Baseline and migration record

The unmodified Stage 0 behavior is documented in `docs/stage1/baseline-scientific-report.md`. Archived materials under `validation/baseline/stage0/` include the original regression fixture, original validation snapshot, environment, and fresh baseline test log. Historical failed physiological regimes and legacy negative findings remain historical evidence; they are not rewritten as current successes or deleted.

At the Stage 1 (0.2.0) record, the declarative OCPE package describes the same 11 states, 52 parameters, four protocol inputs, equations, units, and outputs as the executable implementation. Synchronization of the declarative package and registries to the current 0.3.0 revision (12 states, five volumes, remediated hydrostatic heights, and current protocols) is **complete**: the strict traceability audit passes with zero errors, warnings, and infos, and strict OCPE package validation passes with zero errors and zero warnings; see `docs/stage1-2/readiness-assessment.md`. The legacy short identifier `three-compartment-cardiovascular` is retained only as an alias; the canonical CURIE is `ocpe:disease-models/shared-physiology`.

## J. Traceability

The implemented chain is:

`reference → evidence claim → mechanism → equation → parameter → implementation → validation test → simulation output`.

The 0.3.0 registries contain 69 references, 41 evidence claims, 24 mechanisms, 22 equations, 68 parameters, 29 validation records (28 PASS, 1 FAIL, 0 PENDING — the sole FAIL is the graded-tilt record because two 60° CO comparisons remain outside their unchanged band), 19 protocols, and 11 simulation records; the Stage 1 (0.2.0) registries contained 64 references, 37 evidence claims, 23 mechanisms, 20 equations, 52 parameters, 26 validation records, nine protocols, and eight simulation records (preserved history). Stage 1.1's 23 PASS / 6 FAIL registry state also remains historical evidence. The BibTeX export contains all 69 references and has a synchronization test. Canonical reports are `validation/traceability/audit/traceability_report.json` and `.md`. Record integrity does not establish mechanism truth or clinical validity.

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
