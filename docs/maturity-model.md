# Evidence, model maturity, and release gates

## Two independent classifications

Evidence grade describes support for a literature claim. Model maturity describes the computational representation of a mechanism or phenotype. Neither describes diagnostic accuracy or clinical validity, and one cannot substitute for the other.

### Evidence grades E0–E5

| Grade | Meaning |
|---|---|
| E0 | Unsupported or contradicted; not eligible for implementation |
| E1 | Hypothesis, narrative mechanistic proposal, preprint, or indirect evidence |
| E2 | Small, selected, or unreplicated human observational/physiological evidence |
| E3 | Replicated human physiology or convergent controlled evidence with limitations |
| E4 | Systematic review, meta-analysis, large controlled cohort, or formal consensus evidence |
| E5 | Convergent high-quality evidence with independent prospective replication of the specific claim |

Grades apply to a bounded claim, not an entire paper or disease. For example, consensus support for a POTS HR threshold does not make a calibrated baroreflex gain E4.

### Model maturity M0–M4

| Level | Classification | Required evidence in this repository |
|---|---|---|
| M0 | Hypothesis | Mechanism identified; no computational implementation |
| M1 | Specified | Evidence reviewed; equations/parameters or explicit specification documented; assumptions identified |
| M2 | Implemented | Computational implementation exists and software tests pass |
| M3 | Physiologically verified | Mathematical and physiological validation criteria pass |
| M4 | Empirically benchmarked | Compared against independent published physiological observations |

Execution alone cannot raise a mechanism beyond M2. A unit-test pass cannot assign M3. Agreement with data used to tune the same output is not automatically independent M4 benchmarking. M4 is not clinical validation.

## Current assignments

The authoritative values live in `literature/mechanism_registry.yaml` and phenotype YAML. The initial framework uses the following conservative interpretation:

| Component | Maturity | Rationale |
|---|---|---|
| Conservative hemodynamics, baroreflex, pooling, vascular resistance, POTS mechanisms | M3 after their mathematical and physiological checks pass | Equations execute and are checked for conservation, convergence, direction, and scenario response; absolute parameter identification remains incomplete |
| Cerebral flow, dynamic capacity, oxygen extraction, delayed PEM | M3 after their declared checks pass | Dynamic and physiological behavior is tested; equations remain reduced-order or phenomenological |
| hEDS peripheral venous-compliance configuration | M2 | Software implementation exists, but the hEDS-specific venous-compliance magnitude is assumed and hypothesis-sensitive |
| Connective-tissue causal link and RAAS dynamics | M1 | Specified research gaps; no executable causal module |
| Microvascular/endothelial and respiratory Long COVID dynamics | M0/M1 as registered | Observations/review rationale exist; no defensible current equation implementation |
| Inflammatory/neuroimmune, sleep/circadian, GI dysmotility, and pain-autonomic dynamics | M0 | Reserved hypotheses with no numerical disease multiplier |
| Independent empirical M4 benchmark | Not assigned to the integrated disease models | Current comparisons are group-level plausibility checks with calibration overlap and construct mismatch |

The registry's validation-test metadata is not permission to raise these levels before execution. The final validation report and last-validated commit determine whether M3 release criteria were actually met.

## Release gates

### M0 → M1

- Named evidence claims and references, or explicit exploratory designation.
- Physiological interpretation, variables, assumptions, limitations, and a validation plan.
- No invented equation or parameter to fill a specification gap.

### M1 → M2

- Executable implementation at a stable path/class/function.
- Configuration and unit checks, failure behavior, and software tests.
- Parameters classified as measured/derived/calibrated/inferred/assumed.

### M2 → M3

- Mathematical conservation/bounds/convergence where applicable.
- Physiological baseline, directionality, feedback, and recovery checks.
- Disease-specific scenario and comorbidity checks where applicable.
- No failed required test or hidden physiological regime.

### M3 → M4

- Predeclared comparison against independent published physiological observations.
- Population, measurement, calibration overlap, and construct differences documented.
- Quantitative error/acceptance metrics and reproducible output provenance.

### Clinical use claim

Not supported by this maturity ladder. It would require an explicit clinical protocol, suitable patient data, independent validation, governance, and a defined intended use. None is part of this assignment.

## Demotion and evidence withdrawal

If a reference is corrected, a claim is downgraded, or a result fails replication, linked mechanisms must be reviewed for demotion. Maturity may decrease. Historical reports remain immutable records of their original commit; they are not rewritten to imply retrospective success. Scientific changes follow `docs/scientific-change-management.md`.
