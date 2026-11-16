# ME/CFS Literature Review

Scope: myalgic encephalomyelitis / chronic fatigue syndrome evidence in the
repository registries. Statements are tagged **measured finding**,
**modeling assumption**, or **exploratory hypothesis**. No reference, quantity,
or parameter is introduced beyond the registries.

## 1. Post-exertional malaise as a delayed phenomenon

**Measured findings (CLM-ME-PEM-KINETICS, grade E3).** The consensus evidence
review (REF-IOM-2015) establishes PEM as a core disease feature with delayed
exacerbation and prolonged recovery. Qualitative characterization in nine NIH
focus groups (43 patients; REF-STUSSMAN-2020) found that after daily activity
PEM onset was commonly 12–48 h, peak around 48 h and duration 2–7 days; after
CPET, most respondents reported onset within 24 h and peak within 72 h. PEM is
therefore not equivalent to immediate exertional fatigue.

**Limitations.** Recall-based qualitative data constrain temporal
phenomenology; they do not identify molecular dynamics or a causal equation.

**Modeling assumption.** MEC-RCV-PEM implements an explicitly phenomenological
chain — exertional load (EQ-RCV-001, PAR-EXERTIONAL-LOAD-TIME-CONSTANT =
1800 s), a first-order delayed-stress state (EQ-RCV-002,
PAR-DELAYED-STRESS-TIME-CONSTANT = 43200 s in `mecfs-pem`), a thresholded PEM drive
(EQ-RCV-003, PAR-PEM-TRIGGER-THRESHOLD = 0.001 and PAR-PEM-RESPONSE-GAIN =
20.0 in the `mecfs-pem` configuration; healthy threshold 99.0 disables PEM by
construction), and asymmetric onset/recovery (EQ-RCV-004,
PAR-PEM-ONSET-TIME-CONSTANT = 172800 s and PAR-PEM-RECOVERY-TIME-CONSTANT =
86400 s in `mecfs-pem`). These are operating-point choices inside declared sensitivity
ranges (delayed stress 14400–43200 s; onset 43200–172800 s; recovery 86400–604800 s), constrained — not
identified — by the reported 12–48 h onset and 2–7 day duration windows.
VAL-ME-PEM directly tests the defining temporal distinction: PEM below 0.01
during exertion and the first hour, a subsequent delayed peak, and no PEM in
the healthy reference.

## 2. Repeated-CPET heterogeneity

**Measured findings (CLM-ME-CPET, grade E3).**

- REF-KELLER-2014 (n=22, no control group): day-2 VO2peak declined 13.8%,
  peak work 12.5%, and work at ventilatory threshold 21.3% on tests 24 h
  apart.
- REF-SNELL-2013 (51 CFS, 10 controls): lower day-2 VO2 and workload in
  patients despite similar day-1 findings.
- REF-KELLER-2024 (84 ME/CFS, 71 sedentary controls; multisite): day-2 VO2
  declined 5.3% at peak and 6.7% at ventilatory threshold.

The registry records that effect sizes vary across cohorts and **negative
replications exist**; REF-KELLER-2014 lacked a control group and all studies
suffer spectrum bias toward patients able to complete maximal testing.

**Modeling consequence.** CLM-ME-CPET supports the *direction* of a
PEM-driven capacity reduction and a broad 0–15% VO2-like comparison band —
not a fixed patient effect. MEC-MET-CAPACITY (EQ-MET-001,
PAR-BASELINE-METABOLIC-CAPACITY = 0.85 and PAR-PEM-CAPACITY-PENALTY per
registry) implements this as a normalized construct. VAL-ME-CPET compares the
simulated subsequent-capacity reduction against a predeclared broad 2–20%
scenario band around the 5.3% and 13.8% anchors, with the extra width
explicitly attributed to construct mismatch. The normalized capacity is not a
VO2 measurement and cannot distinguish central from peripheral causes.

## 3. Preload failure and oxygen extraction

**Measured findings (CLM-ME-PRELOAD, grade E2, confidence low).** A
retrospective invasive-CPET study (196 participants; REF-JOSEPH-2021) found
exercise right-atrial pressure 1.9±2 versus 8.3±1.5 mmHg and, in a selected
high-flow subgroup, impaired systemic oxygen extraction (0.74 versus
0.86–0.88).

**Limitations.** The cohort was preselected for low right-atrial pressure;
prevalence in unselected ME/CFS cannot be inferred. The registry mandates
that preload and extraction remain separable mechanisms.

**Modeling assumption.** The `mecfs-pem` configuration sets
PAR-OXYGEN-EXTRACTION-FRACTION = 0.74 (healthy 0.78) anchored to the selected
subgroup value, inside the declared 0.7–0.85 sensitivity range, via
MEC-MET-EXTRACTION (EQ-MET-002). There is no dedicated preload state: preload
effects enter only through the shared venous-return/stroke-volume chain
(MEC-VASC-POOLING, EQ-CV-004). The 0.74 value is an anchor from a selected
subgroup, not a population parameter.

## 4. Cerebral blood flow

**Measured findings (CLM-ME-CBF, grade E2).** In a controlled tilt-table
Doppler study (429 ME/CFS patients, 44 controls; REF-VANCAMPEN-2020),
end-tilt cerebral blood-flow reduction averaged 26% versus 7% in controls —
including patients with normal HR/BP responses. A follow-up case series
(REF-VANCAMPEN-2021) found cerebral-flow recovery after return to supine
remained incomplete despite cardiac-index normalization, without a healthy
recovery-phase control group.

**Modeling assumption.** MEC-CBF-AUTOREG supplies a normalized cerebral-flow
index: pressure-dependent target with an orthostatic impairment term
(EQ-CBF-001; PAR-CEREBRAL-ORTHOSTATIC-IMPAIRMENT = 0.23 in `mecfs-pem`,
calibrated to the group mean within the 0.0–0.3 sensitivity range) and
asymmetric decline/recovery (EQ-CBF-002; PAR-CEREBRAL-RECOVERY-TIME-CONSTANT
raised to 240.0 s from the healthy 12.0 s). VAL-ME-CBF uses a broad 15–35%
scenario band around the 26% group mean.

**Limitations (as recorded).** The evidence is single-center extracranial
Doppler — a surrogate; the model's index is not a Doppler reconstruction and
is deliberately not inferred from mean arterial pressure alone. Exact recovery
time constants require calibration (REF-VANCAMPEN-2021 limitation), so the
240.0 s recovery constant is an assumption, not a measurement.

## 5. Metabolic findings: motivation without a causal claim

CLM-ME-METABOLISM (grade E1, confidence low) covers: a hypometabolic plasma
signature in 45 CFS versus 39 controls (REF-NAVIAUX-2016; resting metabolite
associations, replication required); a small deep-phenotyping study (17
post-infectious ME/CFS, 21 controls; REF-WALITT-2024) that found autonomic and
exertional differences but **no resting mitochondrial defect**; and an
explicit hypothesis review proposing autoantibody-linked autonomic/perfusion/
metabolic downregulation (REF-WIRTH-2020), whose causal chain is not uniformly
replicated. Consequences encoded in the registry: no mitochondrial parameter
exists; the dynamic capacity state (MEC-MET-CAPACITY) remains phenomenology;
and resting-metabolite associations must not be promoted to cellular causal
claims.

## 6. Comorbidity context

REF-ROWE-1999 links EDS, orthostatic intolerance and chronic fatigue; the
exploratory `eds-heds-mecfs-comorbid` configuration composes these mechanisms
and is documented in `literature/eds/` and `literature/cross_disease/`.
Overlap with Long COVID PEM is treated in `literature/long_covid/review.md`
and is explicitly not a claim of identical PEM parameters (CLM-LC-PEM
limitations).

## 7. Unimplemented mechanisms relevant to ME/CFS

- **MEC-MICROVASC (M0, hypothesis):** endothelial/microvascular dysfunction;
  biomarker associations (REF-HAFFKE-2022) do not determine whole-body
  resistance or microvascular flow. Documented in
  `literature/long_covid/mechanism-map.md`.
- **MEC-INFL-SIGNAL (M0, hypothesis):** immune signaling may interact with
  autonomic and recovery states but is not a causal dynamic module; documented
  in `literature/cross_disease/mechanism-map.md`.
- **MEC-SLEEP-CIRCADIAN (M0, hypothesis):** see CLM-CROSS-SLEEP (E1); no
  oscillator or sleep-pressure parameter is implemented.

## 8. Simulation and validation posture

SIM-ME-REPEATED-EXERTION persists the `mecfs-pem` configuration under the
repeated-exertion-recovery protocol against VAL-ME-PEM and VAL-ME-CPET, with
declared status "Explicitly phenomenological PEM dynamics; not a cellular
causal model or synthetic cohort." Severe and bedbound patients are
underrepresented in the source studies (per the `mecfs-pem` limitation field),
so scenarios represent ambulatory-range presentations.
