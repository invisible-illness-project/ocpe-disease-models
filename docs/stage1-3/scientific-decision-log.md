# Stage 1.3 scientific decision log

## D1 — Reproduce before remediation

**Decision:** Execute Stage 1.1 and Stage 1.2 in fresh detached worktrees and compare all historical numerical outputs before relying on Stage 1.3 experiments.

**Result:** 957 numeric fields reproduced; maximum absolute difference 7.25 × 10⁻¹⁵. Audit commits `6034d11…` and `2d1283f` are unavailable, so available revisions `f85360d` and `e48110e` are explicitly named.

**Downstream effect:** Stage 1.2 is a valid computational comparator at those available revisions. No claim is made about missing Git objects.

## D2 — Preserve architecture and criteria

**Decision:** Preserve the 12-state ODE, five-volume conservation, dual baroreceptors, three autonomic effectors, independent CO₂ pathway, solver settings, acceptance ranges, and regression tolerances.

**Reason:** The audit defects concern constitutive behavior and parameter assumptions, not evidence that state dimension or conservation should change.

**Downstream effect:** Improvements can be attributed to declared constitutive/configuration changes rather than a changed target or disabled test.

## D3 — Reject phenotype-specific anatomy

**Decision:** Remove splanchnic/lower-limb height overrides from four POTS, two hEDS, ME/CFS, and Long-COVID-autonomic YAML files.

**Reason:** No evidence justified different anatomical hydrostatic columns as disease mechanisms. Neuropathic and mixed-POTS overrides were specifically unsupported.

**Downstream effect:** All phenotype numerical outputs change; common anatomy is tested explicitly. Physiological phenotype overrides remain separate.

## D4 — Evaluate mechanisms independently

**Decision:** Run compliance, geometry, baroreflex weighting, vascular gains, cardiac compensation, dependent elastance, and cerebral autoregulation separately before combination.

**Result:** Geometry alone produces excessive CO/SV loss; cardiac compensation alone increases CO loss; elastance alone reduces pooling and CO loss. Effects are non-additive.

**Downstream effect:** No single mechanism is credited with the final combined response. The matrix preserves all isolated outcomes.

## D5 — Do not adopt the audit linear combination

**Decision:** Reject the combined linear proposal as the final model.

**Fresh result:** End MAP 52.838 mmHg; 60° CO/SV reductions 52.679/60.377%; 70° reductions 62.013/68.193%. These fail preserved physiological/comparison requirements.

**Reason:** Proposed values and narrative expectations did not reproduce under the actual source/configuration. Numerical proposals are hypotheses, not authority.

## D6 — Add one-sided dependent elastance

**Decision:** Add `k_d max(0, V − V_supine)²` to splanchnic and lower-limb pressure, with healthy `k_d=0.0001 mmHg/mL²`.

**Reason:** The linear combined model overfilled dependent beds and failed CO/SV/MAP constraints. A local pressure response to excess dependent volume addresses that defect without increasing compensatory gains or violating conservation.

**Downstream effect:** Final 60° CO/SV comparisons enter their preserved bands; residual volume change becomes slightly negative; healthy MAP over-defense decreases. The new equation form and coefficient become major structural uncertainties requiring independent testing.

## D7 — Retain explicit unit honesty

**Decision:** Keep the executable coefficient in mmHg/mL². In the OCPE declaration, use `K_d` in mmHg/mL with an explicit 1 mL reference-volume divisor.

**Reason:** The pinned unit registry does not contain pressure-per-volume-squared. Declaring the raw coefficient dimensionless or using an unregistered UCUM unit would be incorrect.

**Downstream effect:** Strict OCPE validation passes without misrepresenting dimensions.

## D8 — Preserve paired baroreflex weighting

**Decision:** Use 0.35/0.65 and perturb aortic/carotid weights as complementary pairs.

**Reason:** Their sum is one and they represent one relative-weighting degree of freedom.

**Downstream effect:** Sensitivity analysis does not introduce an invalid weight sum; non-identifiability remains explicit.

## D9 — Correct neuropathic and hEDS phenotype scenarios conservatively

**Decision:** Set neuropathic splanchnic/lower-limb gains to 0.34 and hEDS lower-limb compliance to 70 mL/mmHg.

**Reason:** With common anatomy, neuropathic gain 0.35 gave sustained HR rise 29.978 bpm, below the preserved criterion. The 0.34 value restores impaired-compensation scenario agreement without changing the threshold. The hEDS value maintains an exploratory compliance contrast relative to healthy 60.

**Downstream effect:** Neuropathic POTS passes by only 0.093 bpm and retains its range-exception disclosure. hEDS remains an unmeasured M2-style hypothesis, not a validated disease coefficient.

## D10 — Separate direct comparison from extrapolation

**Decision:** Classify 60° Zaidi comparisons as direct experimental-angle group comparisons and 70° range reuse as extrapolated model-specific criteria.

**Reason:** The cited experiment directly informs 60°, not an independent 70° replication.

**Downstream effect:** Eight within-band rows are not misreported as eight independent experimental validations.

## D11 — Maintain partial readiness

**Decision:** Do not infer scientific or clinical readiness from passing tests.

**Reason:** Calibration overlap, narrow margins, structural non-identifiability, the new unvalidated elastance law, omitted physiology, and absent independent patient/population evaluation remain.

**Downstream effect:** Use is limited to exploratory deterministic research scenarios. General-purpose synthetic-data generation, diagnosis, treatment, and patient inference remain out of scope.
