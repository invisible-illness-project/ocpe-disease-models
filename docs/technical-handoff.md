# Stage 1 technical handoff and Stage 2 readiness

- Release record date: 2026-11-17
- Target branch: `research/initial-disease-modeling-framework`
- Model/package version: 0.2.0
- Model CURIE: `ocpe:disease-models/shared-physiology`
- Validated source/configuration commit: recorded in `validation/reproducibility.json` and `validation/reports/validation-report.json`
- Pinned OCPE commit: `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`
- Original baseline commit: `47923223d4cf2e8a9c6a1ae8cff485b9d4327dc9`

This is computational research software, not a clinically validated model, diagnostic device, treatment system, synthetic wearable dataset, or flare predictor. **Stage 2 has not begun.**

## A. Executive summary

Stage 1 replaces the aggregated cardiovascular/autonomic foundation with a conservative four-compartment regional model, differentiated autonomic pathways, explicit rhythmic muscle-pump and sustained-contraction mechanics, and a cerebral-perfusion-pressure-based normalized flow index. The existing phenomenological exertion/PEM cascade is retained, with its contradictory scenario timing corrected and its recovery protocol extended.

All ten phenotype configurations begin at complete supine fixed points. Four-volume conservation holds analytically and in integrated tests. POTS and Long COVID autonomic scenarios are evaluated using sustained final-120-second-upright HR rise rather than peak-only responses. Original fixtures and negative results remain archived.

The pre-finalization working-tree validation position is:

- 287 unique tests collected in the complete suite;
- seven independently reported validation layers passing before the final source commit;
- strict traceability with zero errors, warnings, and infos;
- strict OCPE package validation with zero errors and warnings;
- Ruff PASS;

The 26 registry records remain PENDING until the final source-commit run; these preliminary results are not yet the commit-bound release record.
- 42 local-sensitivity executions, 18 deterministic grid scenarios, and three fixed-total chronotropic-split scenarios;
- six demonstrations and 16 persisted current-model runs.

Two healthy empirical soft-anchor misses remain. Early CO reduction is approximately 5.64%, below the broad 10–30% plausibility band. End-tilt cerebral-flow-index reduction is approximately 0.003%, below the broad 3–11% band around the reported 7% control finding, while heart-level MAP rises approximately 17.4 mmHg to 117.4 mmHg. Both are reported as warnings and unresolved structural limitations, not concealed by calibration.

## B. Scientific findings and interpretation

The focused review supports separate splanchnic and lower-limb pooling paths, pressure-gradient-driven venous return, rhythmic muscle-pump transfer, sustained-contraction impediment, faster vagal than sympathetic cardiac control, distinguishable cardiac and vascular sympathetic pathways, head-level cerebral perfusion pressure, and dynamic cerebral autoregulation. It also preserves constraining findings: tilt and LBNP are not interchangeable, muscle pump is not the sole mechanism of exercise CO augmentation, and regional impedance/TCD surrogates are not absolute volume or flow measurements.

The model does not infer CO₂-mediated cerebral vasomotor effects, renal/endocrine volume regulation, patient-specific regional compliances, or unique autonomic gains. Disease configurations remain calibrated computational scenarios. POTS threshold agreement has calibration overlap and is not independent validation. The hEDS venous-compliance value remains exploratory and M2. PEM remains a normalized phenomenological construct rather than a molecular or symptom-score model. Its first 0.05 crossing at approximately 5.7 hours after the day-1 bout ends is earlier than the 12–48-hour daily-activity onset window, although within reported post-CPET onset within 24 hours; the approximately 39.2-hour post-bout peak is a separate, compatible timing result.

Detailed records are:

- `docs/stage1/baseline-scientific-report.md`
- `docs/stage1/literature-and-evidence-matrix.md`
- `docs/stage1/revised-physiological-architecture.md`
- `docs/stage1/parameter-provenance-and-uncertainty.md`
- `docs/stage1/final-validation-report.md`

## C. Implemented architecture

The 11 states are:

1. arterial stressed volume;
2. central-venous stressed volume/preload proxy;
3. splanchnic-venous stressed volume;
4. lower-limb-venous stressed volume;
5. cardiac-sympathetic state;
6. vascular-sympathetic state;
7. vagal state;
8. exertional load;
9. delayed stress;
10. PEM severity; and
11. normalized cerebral-flow index.

The four volume derivatives telescope exactly:

`dVa/dt + dVc/dt + dVs/dt + dVl/dt = 0`.

Rhythmic activity transfers lower-limb venous volume to the central compartment without creating blood. Sustained contraction independently increases lower-limb venous resistance. Cardiac sympathetic activity controls contractility and chronotropy, vascular sympathetic activity controls regional arterial resistances, and vagal activity contributes separately to HR. The baroreflex and cerebral proxy use a shared heart-to-head pressure correction. CPP subtracts central venous back pressure.

There are no disease-specific conditional branches in the shared equations. Phenotype YAML files supply registered parameters; protocol YAML files independently declare `upright`, `exertion`, `rhythmic_muscle_activity`, and `sustained_muscle_contraction`.

OCPE supplies semantics, identifiers, units, specifications, evidence integrity, strict package validation, and observation exchange. SciPy DOP853 supplies numerical integration in this repository. No solver was added to upstream OCPE.

## D. Entry points and reproducible outputs

Primary entry points:

- `scripts/simulate.py` for one configured run;
- `scripts/run_examples.py` for all six demonstrations;
- `scripts/run_sensitivity.py` for local, grid, and chronotropic-split analyses;
- `scripts/run_validation.py` for independent seven-layer reporting; and
- `scripts/audit_traceability.py --root . --strict` for registry/provenance auditing.

Each persisted run records the exact resolved parameters, protocol, configuration SHA-256, model and OCPE versions, Python/NumPy/SciPy versions, and solver method, sampling interval, maximum step, relative/absolute tolerances, and seed. NPZ traces contain the 11 states and derived outputs; JSON results contain metadata and summaries; OCPE observations contain sparse mapped values, not waveforms.

The simulation registry contains nine protocols and eight curated simulation records. Six demonstrations regenerate 16 result/observation/trace sets and their figures. These are small validation artifacts, not patient cohorts or machine-learning datasets.

## E. Validation results

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

The Stage 1 regression fixture contains 16 runs and a scientific change record. The original fixture and original validation snapshot under `validation/baseline/stage0/` are byte-identical to their baseline versions. No test criterion was weakened to hide the early-CO or healthy-CFI results, restore healthy CO in hypovolemia, or substitute peak-only POTS responses. The healthy-CFI control miss now has its own warning; the ME/CFS 15–35% scenario band is unchanged.

## F. Scientific confidence and maturity

Confidence is strongest in software integrity, exact conservation, fixed-point accounting, deterministic reproducibility, and explicit provenance. It is weaker in absolute parameter identification, structural uncertainty, disease heterogeneity, and generalization beyond demonstrated scenarios.

Evidence grades E0–E5 and maturity M0–M4 remain independent. Execution alone does not establish clinical maturity. No integrated disease model is assigned M4 from these results. Group-level empirical anchors overlap with calibration and are not prospective external validation. The early-CO and healthy-CFI misses, early PEM threshold-crossing caveat, reduced-order preload proxy, clipped flows, linear compliances, and absent CO₂/volume-regulation mechanisms remain material limitations.

## G. Stage 2 technical handoff and readiness

### Available computational contract

A separately approved Stage 2 project may use the shared simulator as a deterministic source of latent beat-averaged states and derived outputs. The usable contract is:

- inputs: phenotype IDs, explicit protocol segments, resolved `ModelParameters`, and solver settings;
- outputs: time in seconds, 11 states, regional pressures/flows, HR, SV, CO, CPP/CFI, capacity/extraction, and PEM constructs;
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

The declarative OCPE package now describes the same 11 states, 52 parameters, four protocol inputs, equations, units, and outputs as the executable implementation. The legacy short identifier `three-compartment-cardiovascular` is retained only as an alias; the canonical CURIE is `ocpe:disease-models/shared-physiology`.

## J. Traceability

The implemented chain is:

`reference → evidence claim → mechanism → equation → parameter → implementation → validation test → simulation output`.

Current registries contain 64 references, 37 evidence claims, 23 mechanisms, 20 equations, 52 parameters, 26 validation records, nine protocols, and eight simulation records. The BibTeX export contains all 64 references and has a synchronization test. Canonical reports are `validation/traceability/audit/traceability_report.json` and `.md`. Record integrity does not establish mechanism truth or clinical validity.

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
