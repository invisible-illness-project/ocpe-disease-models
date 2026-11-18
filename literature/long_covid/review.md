# Long COVID Literature Review

Scope: Long COVID / post-acute sequelae of SARS-CoV-2 infection (PASC)
evidence in the repository registries. Statements are tagged **measured
finding**, **modeling assumption**, or **exploratory hypothesis**. The
governing principle, encoded in CLM-LC-HETEROGENEITY, is that Long COVID is
heterogeneous: no single uniform parameter set is ever used.

## 1. Heterogeneity is the primary finding

**Measured findings (CLM-LC-HETEROGENEITY, grade E4, confidence high for
heterogeneity, lower for mechanisms).**

- REF-THAWEETHAI-2023 (RECOVER; 9764 participants): a prospective multicenter
  cohort developed a PASC definition identifying symptom-defined heterogeneity,
  with PEM a highly weighted feature. Symptom definitions do not identify
  physiological mechanism or a single Long COVID phenotype.
- REF-DAVIS-2023 (narrative mechanistic review): synthesizes autonomic,
  endothelial, immune, metabolic and PEM evidence and its overlap with ME/CFS,
  with the explicit caution that emerging hypotheses must not be promoted to
  established causal mechanisms.
- REF-DURSTENFELD-2022 (systematic review/meta-analysis, 38 studies, 2160
  participants): symptomatic Long COVID showed 4.9 mL/kg/min lower exercise
  capacity than recovered comparators, with peripheral-extraction,
  chronotropic and ventilatory patterns that **varied across studies**.

**Modeling consequence (registry-encoded).** Separate autonomic and exertional
configurations exist (`long-covid-autonomic`, `long-covid-exertional`), and
VAL-LC-AUTONOMIC requires that the two remain distinct in the registry.
Symptom clusters are not direct physiological endotypes.

## 2. Autonomic / POTS-overlap subgroup

**Measured findings (CLM-LC-AUTONOMIC, grade E2, confidence low).** Narrative
and meta-analytic syntheses (REF-DAVIS-2023, REF-DURSTENFELD-2022) report
chronotropic and autonomic abnormalities — HR, HRV, CPET chronotropic response,
orthostatic symptoms — in some patients, overlapping with POTS and ME/CFS.
Methods and patient selection are heterogeneous; there is no universal gain.

**Modeling assumption.** `long-covid-autonomic` (M3,
`phenomenological_composition`) reuses the shared autonomic and venous
mechanisms (MEC-AUT-BAROREFLEX, MEC-VASC-POOLING, MEC-RCV-PEM) with calibrated
overrides: common healthy anatomical hydrostatic heights with no phenotype-
specific override, PAR-HEART-RATE-REST = 70.0
bpm, PAR-HEART-RATE-CARDIAC-SYMPATHETIC-GAIN and PAR-HEART-RATE-VAGAL-GAIN =
50.0 bpm each, PAR-CEREBRAL-ORTHOSTATIC-IMPAIRMENT = 0.08,
PAR-BASELINE-METABOLIC-CAPACITY = 0.85, PAR-PEM-TRIGGER-THRESHOLD = 0.001, and
PAR-PEM-RESPONSE-GAIN = 12.0. VAL-LC-AUTONOMIC requires an orthostatic
HR rise of at least 30 bpm with MAP at least 70 mmHg — a POTS-like scenario
criterion for this one subgroup, not a characterization of Long COVID.
Viral persistence, microclots and immune signaling are not causally encoded
(per the configuration's own limitations).

## 3. Exertional / impaired-extraction subgroup

**Measured findings (CLM-LC-EXTRACTION, grade E2).** A small invasive-CPET
case-control study (10 post-COVID participants, 10 controls; REF-SINGH-2022)
found systemic oxygen extraction 0.49±0.1 versus 0.78±0.1 with preserved peak
cardiac index. The sample is very small and referral-selected; 0.49 is not a
population-wide parameter and the mechanism is not necessarily mitochondrial.

**Modeling assumption.** `long-covid-exertional` (M3,
`empirically_anchored_phenomenology`) sets PAR-OXYGEN-EXTRACTION-FRACTION =
0.49 via MEC-MET-EXTRACTION (EQ-MET-002) with PAR-BASELINE-METABOLIC-CAPACITY
= 0.8 and PEM settings (threshold 0.001, gain 16.0). Central cardiac output is
preserved separately, matching the measured dissociation. VAL-LC-EXTRACTION
requires reduced functional capacity at matched PEM severity and imposes **no**
POTS-like HR criterion on this subgroup — keeping it orthogonal to the
autonomic subgroup. Peripheral shunt, mitochondrial flux and ventilatory
control remain lumped inside the extraction/capacity approximation
(MEC-MET-EXTRACTION limitations).

**Measured group-level context (CLM-LC-CPET, grade E4).** The meta-analytic
4.9 mL/kg/min exercise-capacity deficit (REF-DURSTENFELD-2022) supports
reporting reduced functional capacity without claiming a single mechanism; it
is not mapped to the normalized capacity parameter one-to-one.

## 4. PEM in Long COVID

**Measured findings (CLM-LC-PEM, grade E3).** PEM is a highly weighted PASC
feature (REF-THAWEETHAI-2023) and is synthesized with ME/CFS overlap in
REF-DAVIS-2023. In a longitudinal exercise-provocation study (25 Long COVID
participants with PEM, 21 controls; REF-APPELMAN-2024), all patients developed
PEM one day post-test, with exertion-related metabolic and muscle-tissue
abnormalities (CLM-LC-MUSCLE, grade E2). The tissue findings are observational
and their interpretation — including microclot or mitochondrial causality — is
debated; they do not prove a molecular mechanism.

**Modeling assumption.** Both Long COVID configurations reuse MEC-RCV-PEM with
subgroup-specific response gains (12.0 autonomic, 16.0 exertional versus 20.0
in `mecfs-pem`). The registry mandates disclosing these borrowed kinetic
assumptions: Long COVID PEM trajectories vary and can differ from ME/CFS, so
identical parameters are not asserted (CLM-LC-PEM limitations). Molecular
mechanisms are kept out of the executable PEM claim (CLM-LC-MUSCLE
`modeling_implications`).

## 5. Respiratory / ventilatory phenotype — unimplemented

**Measured finding.** Ventilatory patterns varied across the 38 meta-analyzed
studies (REF-DURSTENFELD-2022), and ventilatory measures appear in the
invasive-CPET record (REF-SINGH-2022). **Status:** MEC-RESP-LC (maturity M1,
`status: proposed`, **exploratory**) documents respiratory and ventilatory
limitation as a distinct future module with no parameters, equations, or
tests. The registry guardrail: oxygen-extraction phenotypes must not be
treated as respiratory simulations.

## 6. Endothelial and microvascular hypotheses — unimplemented

**Measured findings (CLM-LC-ENDOTHELIAL, grade E1, confidence low).**
Endothelial biomarker alterations are reported in selected post-COVID and
ME/CFS groups (REF-HAFFKE-2022), and anomalous fibrin(ogen) amyloid deposits
with increased antiplasmin are reported in a laboratory case-control study
(REF-PRETORIUS-2021). Measurement standardization, replication and causal
relevance to symptoms remain unresolved.

**Status:** MEC-MICROVASC (M0, hypothesis) and MEC-INFL-SIGNAL (M0,
hypothesis) are retained as exploratory registry entries **without numerical
implementation**; no microclot resistance, shunt-flow or endothelial-biomarker
equation is defensible from current registry evidence (MEC-MICROVASC
limitations). These are mapped in `literature/long_covid/mechanism-map.md`
(MEC-MICROVASC) and `literature/cross_disease/mechanism-map.md`
(MEC-INFL-SIGNAL) per registry designation.

## 7. Summary of the explicit heterogeneity stance

| Dimension | Registry anchor | Implementation status |
|---|---|---|
| Autonomic / POTS-overlap | CLM-LC-AUTONOMIC (E2) | `long-covid-autonomic`, M3 calibrated subgroup |
| Exertional / extraction | CLM-LC-EXTRACTION (E2), CLM-LC-CPET (E4) | `long-covid-exertional`, M3 empirically anchored |
| PEM | CLM-LC-PEM (E3), CLM-LC-MUSCLE (E2) | MEC-RCV-PEM shared, subgroup-specific gains |
| Respiratory / ventilatory | CLM-LC-CPET patterns; REF-DURSTENFELD-2022 | MEC-RESP-LC, M1 — unimplemented |
| Endothelial / microvascular | CLM-LC-ENDOTHELIAL (E1) | MEC-MICROVASC, M0 — unimplemented |

SIM-LC-AUTONOMIC persists only the autonomic subgroup, under the declared
status "One autonomic subgroup only; not a uniform Long COVID model."
