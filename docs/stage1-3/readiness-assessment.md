# Stage 1.3 readiness assessment

## Verdict

**Overall scientific readiness remains PARTIAL.** Stage 1.3 is suitable only for explicitly exploratory, deterministic research scenarios with the declared calibration and structural limitations. It is **not ready** for clinical, diagnostic, treatment, patient-specific, population-inference, or unrestricted/general-purpose synthetic-data use.

The preserved numerical comparisons now pass, but numerical threshold passage is not scientific readiness. The final model uses the same CO/SV/CFI and phenotype criteria that informed calibration, introduces an unvalidated quadratic constitutive form, and has narrow margins on important checks.

## Current evidence status

| Area | Status | Basis and interpretation |
|---|---|---|
| Stage 1.2 numerical reproduction | PASS | 957/957 numeric fields and 277/277 identifiers/statuses reproduced from fresh exact-commit worktrees |
| Twelve-state/five-volume architecture | PASS | Preserved; conservation and layout tests remain active |
| Supine fixed points and solver behavior | PASS | Mathematical layers; computational correctness only |
| Common anatomy across disease phenotypes | PASS | Unsupported phenotype-specific hydrostatic-height overrides removed from eight configurations |
| Healthy sustained HR/CFI | PASS, calibrated | 13.298 bpm and 4.961% at 70°; not independent validation |
| Healthy residual-bed response | PASS, model-specific | Residual volume change −17.931 mL; abs(change) <30 mL is a repository criterion |
| Healthy MAP over-defense | Improved, not resolved | End MAP 102.253 mmHg versus 100 mmHg supine; still an upright rise |
| Direct 60° CO/SV comparisons | PASS, narrow CO margin | All four within preserved group bands; CO is only about 0.081 percentage points above the lower edge |
| 70° CO/SV comparisons | PASS as extrapolation | Reused 60°-informed bands; not direct 70° experimental replication |
| Four POTS and Long-COVID-autonomic HR criteria | PASS, calibrated | Neuropathic POTS clears 30 bpm by only about 0.093 bpm; no diagnostic inference |
| ME/CFS CFI scenario | PASS | 24.538% within unchanged 15–35% band |
| Sensitivity and identifiability analysis | EXECUTED | 96 local, 27 grid, 3 split rows; no patient/population identification |
| Regression and demonstrations | PASS | 16 reviewed fixture runs; six groups/16 persisted demonstrations regenerated |
| Strict traceability and OCPE | PASS | Zero errors/warnings; record and structural integrity only |
| General-purpose synthetic-data readiness | **NOT READY** | Calibrated structure, no independent cohort or held-out validation, no population model |

## Material remaining limitations

1. **Unvalidated constitutive structure.** The one-sided quadratic term and `k_d=0.0001 mmHg/mL²` were selected in model space to correct dependent overfilling. Neither is a measured venous-tissue property. Alternative nonlinear forms have not been compared.
2. **Calibration overlap.** The 60° CO/SV bands, CFI ranges, phenotype thresholds, and related scenarios used for model selection are also reported as outcomes. They cannot serve as independent external validation.
3. **Narrow acceptance margins.** Direct 60° CO and neuropathic-POTS sustained HR pass narrowly. Small parameter or structural changes can move these results outside their criteria, as the local sensitivity analysis shows.
4. **Pressure compensation remains imperfect.** Healthy end-tilt MAP remains 2.253 mmHg above supine. The model still lacks an independent cardiopulmonary baroreflex pathway and uses simplified integrated autonomic feedback.
5. **Parameter non-identifiability.** Baroreflex weighting, chronotropic split, compliance/elastance, geometry/blood volume, and cardiac/vascular compensation are not uniquely identified by the available outputs.
6. **Effective geometry is not patient anatomy.** Common heights remove unjustified disease differences but remain lumped model parameters. They do not establish anatomical equality or patient-specific hydrostatic columns.
7. **Phenotype mechanisms remain assumptions.** Neuropathic gain 0.34 retains a disclosed range exception. Hyperadrenergic POTS lacks an independent non-baroreflex catecholamine state. hEDS compliance 70 is unmeasured. Long-COVID and mixed-POTS configurations are not validated subtypes.
8. **Cerebral simplifications persist.** Fixed effective outflow pressure is not resolved ICP or thoracic CVP; ETCO₂ is declared, bounded, and not converted to PaCO₂. The residual slope has calibration overlap.
9. **PEM remains phenomenological.** Normalized PEM/capacity states are not molecular mechanisms or measured symptom scores; prior onset-window caveats remain.
10. **Uncertainty analysis is limited.** One-at-a-time perturbations and small grids are not global sensitivity, probabilistic uncertainty, patient cohorts, or population distributions.
11. **No independent prospective benchmark.** No held-out experiment, patient dataset, or non-overlapping group benchmark establishes generalization.

## Readiness boundaries

Appropriate uses:

- reproducible deterministic research scenarios;
- mechanism hypothesis comparison with explicit assumptions;
- software, equation, provenance, and sensitivity development; and
- planning independent empirical evaluation.

Inappropriate uses:

- diagnostic labels, disease-severity scores, treatment selection, or patient-specific prediction;
- claims that parameter values are measured human or disease-specific constants;
- treating sensitivity rows as synthetic patients or assigning prevalence/probability;
- unrestricted synthetic data generation presented as physiologically validated ground truth; and
- clinical maturity upgrades based on green tests or within-band outputs.

## Required next work

1. Test the dependent-elastance equation against independent regional pressure/volume data not used for calibration; compare plausible alternative forms.
2. Obtain non-overlapping multi-angle CO/SV/MAP/HR benchmarks, including a genuine 70° experiment, with prospective acceptance criteria.
3. Use transient and beat-level data to assess chronotropic and baroreflex identifiability; extend beyond local deterministic perturbations.
4. Resolve or reject the hEDS compliance hypothesis and neuropathic range exception with defensible evidence.
5. Evaluate cardiopulmonary baroreflex and non-baroreflex catecholamine pathways before claiming mechanistic subtype specificity.
6. Preserve all Stage 1.3 assumptions and narrow margins in any downstream research-planning handoff.

No Stage 2 wearable-dataset generation or Stage 3 prediction capability is authorized or established by this assessment.
