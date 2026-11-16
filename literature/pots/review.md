# POTS Literature Review

Scope: postural orthostatic tachycardia syndrome (POTS) evidence curated in
`literature/references.yaml`, `literature/evidence_registry.yaml`,
`literature/mechanism_registry.yaml`, `literature/equation_registry.yaml`, and
`literature/parameter_registry.yaml`. Nothing in this review introduces
references, quantitative findings, or parameters beyond those registries.
Throughout, statements are tagged as **measured finding** (human data reported
in a cited reference), **modeling assumption** (a value or structure chosen for
the computational configuration), or **exploratory hypothesis** (E1/low-grade
or unimplemented M0/M1 mechanism).

## 1. Diagnostic framing (consensus, not model output)

The Heart Rhythm Society consensus defines POTS by a sustained orthostatic
heart-rate rise of at least 30 bpm in adults (at least 40 bpm in adolescents)
without orthostatic hypotension (REF-SHELDON-2015). In this repository that
definition is claim CLM-POTS-CRITERIA (evidence grade E4): it supplies
scenario-level acceptance metrics for VAL-POTS-NEUROPATHIC, VAL-POTS-HYPER and
VAL-POTS-HYPO, not evidence that any simulation is clinically valid. A
simulated trace crossing 30 bpm is a plausibility check; the model is never
used to diagnose.

## 2. Heterogeneity and subtype structure

POTS is mechanistically heterogeneous, and neuropathic, hypovolemic and
hyperadrenergic contributions can coexist rather than forming disjoint
diagnoses (CLM-POTS-PHENOTYPES, grade E3; REF-LOW-2009, REF-GEDDES-2022,
REF-FU-2018, REF-THIEBEN-2007, REF-FU-2010). The Mayo Clinic tertiary cohort
(REF-THIEBEN-2007, n=152) reported overlapping neuropathic, hypovolemic and
hyperadrenergic features, but it is a retrospective referral sample: its
cohort fractions are **measured findings** about that clinic and must not be
read as population subtype probabilities. This directly motivates the
repository's mixed phenotype (`phenotypes/pots/pots-mixed.yaml`, maturity M2,
`classification: phenomenological_composition`) and the registry rule that
mechanisms are composed through coherent parameter configurations, never
through output multipliers.

## 3. Neuropathic subtype

**Measured findings.** In a selected mechanistic case-control study (12
neuropathic POTS, 10 controls; REF-JACOB-2000), partial sympathetic/sudomotor
denervation with impaired peripheral vasoconstriction was demonstrated.
Skin-biopsy and sudomotor data in 24 neuropathic POTS patients versus 10
controls (REF-GIBBONS-2013) provide structural and functional evidence of
small-fiber abnormalities. Regional vascular measurements (REF-STEWART-2003)
document excess venous pooling and impaired vasoconstriction in POTS
subgroups. These support CLM-POTS-POOLING (grade E3): regional vascular
dysfunction can reduce venous return and stroke volume during orthostasis.

**Limitations.** The neuropathic samples are small and selected; they do not
estimate prevalence and do not justify assuming neuropathy in every POTS
configuration (per the reference records' own limitation fields). Regional
flow and resistance measurements cannot identify whole-body lumped compliance
or resistance parameters.

**Modeling assumption.** The `pots-neuropathic` configuration implements
neuropathy as a reduced sympathetic modulation of systemic resistance
(MEC-VASC-CONSTRICTION, EQ-VASC-001) with
PAR-RESISTANCE-SYMPATHETIC-GAIN = 0.35 (healthy 0.8), combined with amplified
orthostatic pooling (MEC-VASC-POOLING, EQ-ORT-001,
PAR-GRAVITY-PRESSURE-OFFSET = 10.0 mmHg) and calibrated chronotropic settings
(PAR-HEART-RATE-BASE = 37.5, PAR-HEART-RATE-SYMPATHETIC-GAIN = 65.0). All
gains are calibrated demonstration values, not patient measurements; the
single lumped resistance lumps regional denervation and distinct vascular
beds (per MEC-VASC-CONSTRICTION limitations). Scenario behavior is checked by
VAL-POTS-NEUROPATHIC under SIM-POTS-ORTHOSTATIC.

## 4. Hyperadrenergic subtype

**Measured findings.** Muscle sympathetic nerve activity and hemodynamic
recordings (REF-MUENTER-2005) support baroreflex/sympathetic compensation as a
measurable POTS mechanism while showing physiological heterogeneity, and
clinical reviews describe a hyperadrenergic subset with elevated sympathetic
tone (REF-LOW-2009, REF-THIEBEN-2007). CLM-POTS-HYPERADRENERGIC (grade E3)
states that increased sympathetic/chronotropic response characterizes a subset
and can be represented by altered feedback gain; computational work
(REF-GEDDES-2022) shows that increased baroreflex sensitivity can reproduce
persistent tachycardia in closed-loop models.

**Limitations.** Not all elevated catecholamines indicate primary
hyperadrenergic POTS, and no catecholamine concentration, reuptake, or
primary-versus-secondary distinction is modeled (CLM-POTS-HYPERADRENERGIC and
MEC-AUT-HYPERADRENERGIC limitation fields).

**Modeling assumption.** The `pots-hyperadrenergic` configuration raises
chronotropic gain (PAR-HEART-RATE-SYMPATHETIC-GAIN = 103.0), steepens the
sigmoidal baroreflex target (PAR-BAROREFLEX-PRESSURE-SCALE = 1.5 in EQ-AUT-001),
lowers the intercept (PAR-HEART-RATE-BASE = 20.0) and raises resistance
modulation (PAR-RESISTANCE-SYMPATHETIC-GAIN = 1.0). This is a calibrated
demonstration of direction (MEC-AUT-HYPERADRENERGIC), checked by VAL-POTS-HYPER.

## 5. Hypovolemic subtype and the RAAS gap

**Measured findings.** In 15 POTS patients versus 14 controls, plasma volume
was 2348±438 mL versus 2823±480 mL, a mean deficit of 334±187 mL
(12.8±7.6% of ideal), with inappropriately low renin/aldosterone responses
(REF-RAJ-2005; CLM-POTS-HYPOVOLEMIA, grade E2). Separately, baseline blood
volume was 60 mL/kg [54,64] versus 71 mL/kg [65,78] and left-ventricular mass
was lower in 27 POTS versus 16 controls (REF-FU-2010), with exercise training
increasing both — an association that does not prove universal deconditioning
causality.

**Modeling assumption.** MEC-VOL-HYPOVOLEMIA applies
PAR-BLOOD-VOLUME-FACTOR = 0.92 to all initial stressed compartments in
`pots-hypovolemic`. The registry is explicit: plasma-volume deficit is not
equivalent to the model's stressed whole-blood volume scaling, and 0.92 is a
calibrated assumption within a 0.85–1.05 sensitivity range, not a measured
deficit. Companion settings (PAR-BAROREFLEX-PRESSURE-SCALE = 6.0,
PAR-HEART-RATE-BASE = 30.0, PAR-HEART-RATE-SYMPATHETIC-GAIN = 80.0,
PAR-RESISTANCE-SYMPATHETIC-GAIN = 0.9) are likewise calibrated.

**Exploratory hypothesis (M1, unimplemented).** The renin-aldosterone paradox
is documented, but dynamic RAAS/renal volume regulation is a proposed
mechanism only (MEC-RAAS, maturity M1, `status: proposed`, no parameters, no
tests). The static blood-volume factor must not be interpreted as a RAAS
simulation.

## 6. Mixed subtype

The `pots-mixed` configuration composes MEC-VOL-HYPOVOLEMIA,
MEC-VASC-CONSTRICTION, MEC-AUT-HYPERADRENERGIC and MEC-VASC-POOLING with
intermediate calibrated values (PAR-BLOOD-VOLUME-FACTOR = 0.96,
PAR-BAROREFLEX-PRESSURE-SCALE = 3.0, PAR-RESISTANCE-SYMPATHETIC-GAIN = 0.55,
PAR-HEART-RATE-BASE = 32.5, PAR-HEART-RATE-SYMPATHETIC-GAIN = 75.0). It is
maturity M2 and exploratory: the joint configuration requires empirical
calibration and mechanisms need not sum linearly in patients. VAL-POTS-MIXED
requires that composition is explicit and that conflicting ad hoc overrides
raise errors rather than silently merging.

## 7. Baroreflex evidence is not uniform

CLM-POTS-BAROREFLEX (grade E3) supports baroreflex-mediated sympathetic and
chronotropic control as relevant to POTS, but the registry records directly
conflicting findings: REF-FU-2010 found similar baroreflex function between
POTS and controls, while REF-CELLETTI-2017 found higher — not lower — resting
spectral baroreflex sensitivity in a JHS/EDS-HT cohort. Consequently no
universal gain reduction is defensible, and the model uses a bounded sigmoidal
pressure target (EQ-AUT-001) with a first-order sympathetic lag (EQ-AUT-002,
PAR-SYMPATHETIC-TIME-CONSTANT = 4.0 s) and separate effector gains. The
implementation does not reproduce 0.1 Hz oscillations, does not separate vagal
from sympathetic pathways, and does not distinguish afferent from efferent
lesions (MEC-AUT-BAROREFLEX limitations).

## 8. Cerebral blood flow

**Measured finding.** A controlled orthostatic study (REF-DELPOZZI-2014)
reported reduced cerebral blood-flow velocity during orthostasis in POTS
preceding hypocapnic hyperpnea and sympathetic activation, motivating a
distinct cerebral-flow output rather than inference from blood pressure alone.

**Modeling assumption.** MEC-CBF-AUTOREG provides a normalized cerebral-flow
index with pressure dependence (EQ-CBF-001, PAR-CEREBRAL-PRESSURE-EXPONENT =
0.8) and asymmetric decline/recovery kinetics (EQ-CBF-002,
PAR-CEREBRAL-DECLINE-TIME-CONSTANT = 5.0 s,
PAR-CEREBRAL-RECOVERY-TIME-CONSTANT = 12.0 s healthy). The index is normalized;
Doppler velocity is not necessarily volumetric CBF, and the model has no CO2,
autoregulatory-gain or vascular-territory structure (per REF-DELPOZZI-2014 and
MEC-CBF-AUTOREG limitation fields). No POTS-specific impairment value is
assigned in the registry; the PAR-CEREBRAL-ORTHOSTATIC-IMPAIRMENT phenotype
values (0.23, 0.08) belong to the ME/CFS, comorbid and Long COVID
configurations and are discussed in those reviews.

## 9. What this model does not claim

- Simulations are research demonstrations; no patient-specific calibration has
  been performed for any parameter (parameter-registry policy).
- Subtype configurations are calibrated scenarios, not diagnoses; subtype
  boundaries overlap in the source literature.
- Treatment effects (e.g., exercise training in REF-FU-2010, REF-FU-2018) are
  outside scope; no treatment recommendations are encoded.
- MEC-RAAS (M1) is the only POTS-specific unimplemented mechanism; there is no
  POTS-specific M0 module in the registry.
