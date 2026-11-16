# Cross-Disease Literature Review

Scope: shared and distinct mechanisms across POTS, hEDS, ME/CFS and Long
COVID as encoded in the repository registries. Statements are tagged
**measured finding**, **modeling assumption**, or **exploratory hypothesis**.
This review also records the evidence/maturity boundaries that any comparison
must respect, and the future modules the registry has reserved.

## 1. Shared mechanisms

| Shared mechanism | Diseases (per mechanism registry) | Grounding |
|---|---|---|
| MEC-CV-VOLUME (M3) | shared substrate for all | CLM-CV-HEMODYNAMICS (E3; REF-GEDDES-2022) |
| MEC-AUT-BAROREFLEX (M3) | shared, POTS, hEDS, ME/CFS, Long COVID | CLM-POTS-BAROREFLEX (E3), CLM-CV-HEMODYNAMICS |
| MEC-VASC-POOLING (M3) | POTS, hEDS, ME/CFS, Long COVID | CLM-POTS-POOLING (E3) |
| MEC-CBF-AUTOREG (M3) | shared, ME/CFS, Long COVID | CLM-ME-CBF (E2) |
| MEC-RCV-PEM (M3) | ME/CFS, Long COVID | CLM-ME-PEM-KINETICS (E3), CLM-LC-PEM (E3) |
| MEC-MET-CAPACITY (M3) | ME/CFS, Long COVID | CLM-ME-CPET (E3), CLM-LC-CPET (E4) |
| MEC-MET-EXTRACTION (M3) | ME/CFS, Long COVID | CLM-ME-PRELOAD (E2), CLM-LC-EXTRACTION (E2) |

Sharing a mechanism means sharing equation structure and (usually) nominal
operating points — not sharing disease parameter values. Every disease
configuration's overrides are labeled calibrated assumptions, and the shared
substrate is what makes cross-disease scenario comparison technically possible
at all (SIM-CROSS-DISEASE).

**Measured cross-disease observations:**

- Orthostatic intolerance appears in POTS (CLM-POTS-CRITERIA, E4), in
  hEDS/hypermobility cohorts (CLM-EDS-OI, E2), and in Long COVID subgroups
  (CLM-LC-AUTONOMIC, E2) — the *phenomenon* is shared, the measured effect
  sizes and cohort bases are not equivalent.
- PEM appears in ME/CFS (CLM-ME-PEM-KINETICS, E3) and in Long COVID
  (CLM-LC-PEM, E3), with the registry explicitly noting that Long COVID PEM
  trajectories can differ from ME/CFS and that identical parameters are not
  asserted.
- Cerebral-flow reduction is measured in ME/CFS tilt cohorts (26% vs 7%,
  REF-VANCAMPEN-2020) and reported in POTS orthostasis (REF-DELPOZZI-2014);
  only ME/CFS, comorbid and Long COVID configurations carry impairment values.
- Endothelial biomarkers are reported in selected Long COVID *and* ME/CFS
  groups (REF-HAFFKE-2022; CLM-LC-ENDOTHELIAL, E1) — association only, no
  flow parameter.

## 2. Distinct mechanisms

| Mechanism | Disease scope | Why it stays distinct |
|---|---|---|
| MEC-VOL-HYPOVOLEMIA (M3) | POTS only | Anchored to POTS cohorts (REF-RAJ-2005, REF-FU-2010; CLM-POTS-HYPOVOLEMIA E2); no hypovolemia parameter is asserted for other diseases |
| MEC-VASC-CONSTRICTION (M3) | POTS only | Neuropathic denervation evidence is POTS-specific (REF-JACOB-2000, REF-GIBBONS-2013) |
| MEC-AUT-HYPERADRENERGIC (M3) | POTS, Long COVID | Hyperadrenergic evidence is a POTS subgroup claim (CLM-POTS-HYPERADRENERGIC); Long COVID autonomic subgroup borrows the pathway, not the POTS gain values |
| MEC-VASC-COMPLIANCE (M2, exploratory) | hEDS only | Assumed venous-compliance hypothesis; forbidden from arterial-to-venous extrapolation and from other EDS subtypes (CLM-EDS-VASCULAR E1) |
| MEC-RAAS (M1, proposed) | POTS | Documented RAAS paradox (REF-RAJ-2005); unimplemented |

## 3. Comorbidity evidence

**Measured findings.**

- hEDS ↔ POTS: ~31% of one 91-patient POTS clinic cohort met hEDS criteria
  (REF-MILLER-POTS-2020) — a clinic comorbidity estimate with ascertainment
  bias, not a population prevalence. Earlier association: REF-ROWE-1999 (EDS,
  orthostatic intolerance, chronic fatigue), REF-GAZIT-2003 (JHS
  dysautonomia), REF-DEWANDELE-2014 (EDS-HT autonomic abnormalities).
- EDS ↔ ME/CFS: REF-ROWE-1999 links EDS to chronic fatigue and orthostatic
  intolerance in 12 patients.
- Long COVID ↔ ME/CFS: REF-DAVIS-2023 synthesizes overlapping autonomic,
  metabolic and PEM evidence; REF-APPELMAN-2024 shows exercise-provoked PEM
  with next-day onset in Long COVID; REF-HAFFKE-2022 reports endothelial
  biomarkers in both post-COVID and ME/CFS groups.

**Modeling assumption.** The `eds-heds-mecfs-comorbid` configuration (M2,
`exploratory_comorbidity`) demonstrates technical mechanism composition only;
its own limitation states there is no claim that the joint parameter
distribution is epidemiologically typical. VAL-SW-CONFIG requires that
conflicting comorbidity overrides fail explicitly rather than silently merge.

## 4. Evidence and maturity boundaries

Cross-disease comparison runs against deliberately non-equivalent evidence
levels; SIM-CROSS-DISEASE carries the status "Scenario comparison across
non-equivalent evidence levels; not a comparative effectiveness or
disease-severity ranking." The boundaries, by grade and maturity:

| Boundary | Registry statement |
|---|---|
| E4 claims | CLM-POTS-CRITERIA (diagnostic definition), CLM-LC-HETEROGENEITY, CLM-LC-CPET — strong for definitions/heterogeneity, not for mechanism magnitudes |
| E3 claims | CLM-CV-HEMODYNAMICS, CLM-POTS-PHENOTYPES, CLM-POTS-POOLING, CLM-POTS-HYPERADRENERGIC, CLM-POTS-BAROREFLEX, CLM-ME-PEM-KINETICS, CLM-ME-CPET, CLM-LC-PEM |
| E2 claims | CLM-POTS-HYPOVOLEMIA, CLM-EDS-OI, CLM-ME-PRELOAD, CLM-ME-CBF, CLM-LC-AUTONOMIC, CLM-LC-EXTRACTION, CLM-LC-MUSCLE — selected cohorts; magnitudes are scenario anchors, not population parameters |
| E1 claims | CLM-EDS-VASCULAR, CLM-ME-METABOLISM, CLM-LC-ENDOTHELIAL, CLM-CROSS-SLEEP — hypothesis grade; no direct numerical implementation from these alone |
| M3 implemented | All shared mechanisms plus disease-specific POTS/exertional mechanisms |
| M2 | MEC-VASC-COMPLIANCE (exploratory hEDS); `pots-mixed`, `eds-heds-*` configurations |
| M1 proposed, unimplemented | MEC-RAAS, MEC-CONNECTIVE, MEC-RESP-LC |
| M0 hypothesis, unimplemented | MEC-MICROVASC, MEC-INFL-SIGNAL, MEC-SLEEP-CIRCADIAN, MEC-GI-DYSMOTILITY, MEC-PAIN-AUT |

VAL-EMPIRICAL-ANCHORS enforces that every quantitative comparison in the
repository resolves to a cited group-level finding with its construct and
population limitations stated; VAL-TRACEABILITY audits the ID chain itself.

## 5. Contradictions that constrain cross-disease claims

- **Baroreflex:** REF-FU-2010 (similar BRS, POTS vs controls) versus
  REF-CELLETTI-2017 (higher resting spectral BRS in JHS/EDS-HT) — no
  universal baroreflex-gain abnormality may be claimed for any disease
  (CLM-POTS-BAROREFLEX limitations).
- **Repeated CPET:** REF-KELLER-2014 (13.8%) vs REF-KELLER-2024 (5.3%) with
  negative replications recorded — only a broad band, never a point value,
  transfers across cohorts (CLM-ME-CPET).
- **Resting metabolism:** hypometabolic signature (REF-NAVIAUX-2016) versus no
  resting mitochondrial defect (REF-WALITT-2024) — no resting cellular
  parameter exists anywhere in the model (CLM-ME-METABOLISM, E1).

## 6. Future modules (reserved, unimplemented)

The registry reserves five cross-disease or disease-specific future modules,
all documented in the mechanism maps of this directory tree and none with
parameters, equations, or tests:

- **MEC-RAAS (M1, POTS):** dynamic renal volume regulation; static volume
  factor must not be interpreted as RAAS simulation.
- **MEC-CONNECTIVE (M1, hEDS):** connective-tissue → vascular-mechanics link;
  no causal tissue-to-compliance equation asserted.
- **MEC-RESP-LC (M1, Long COVID):** respiratory/ventilatory limitation;
  extraction phenotypes are not respiratory simulations.
- **MEC-MICROVASC (M0, Long COVID/ME-CFS):** endothelial/microvascular;
  biomarker associations only (CLM-LC-ENDOTHELIAL).
- **MEC-INFL-SIGNAL (M0, ME/CFS/Long COVID):** neuroimmune signaling;
  biomarker associations must not become inflammatory causes of symptoms.
- **MEC-SLEEP-CIRCADIAN (M0, all four diseases):** CLM-CROSS-SLEEP (E1)
  records that current evidence is insufficient to parameterize a shared
  dynamic oscillator; no circadian parameters or sleep-derived disease
  multipliers exist. This is documented as future work only.
- **MEC-GI-DYSMOTILITY / MEC-PAIN-AUT (M0, hEDS):** review topics without
  defensible equations.

Promotion of any module requires new registry-grade evidence; this review
adds none.
