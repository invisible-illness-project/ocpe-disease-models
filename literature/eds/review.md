# hEDS / EDS Literature Review

Scope: evidence curated in the repository registries for Ehlers-Danlos
syndromes with emphasis on hypermobile EDS (hEDS) and orthostatic intolerance.
Statements are tagged **measured finding**, **modeling assumption**, or
**exploratory hypothesis**. No reference, quantity, or parameter appears here
that is not present in the registries.

## 1. Historical terminology and why it matters

The underlying studies span three generations of diagnostic labels, and the
registry preserves them rather than harmonizing them away:

- **JHS (joint hypermobility syndrome)** — REF-GAZIT-2003, and the JHS/EDS-HT
  framing in REF-CELLETTI-2017.
- **EDS-HT (Ehlers-Danlos syndrome, hypermobility type)** — REF-DEWANDELE-2014;
  also the older **EDS type III** label in REF-CHENG-2017 and the early EDS
  cohort in REF-ROWE-1999.
- **hEDS (hypermobile EDS, 2017 criteria)** — REF-MILLER-2020,
  REF-MILLER-POTS-2020, REF-ROMA-2018.

**Consequence for modeling:** cohorts recruited under different criteria are
not interchangeable. REF-ROMA-2018 explicitly notes that underlying cohorts
use inconsistent JHS/EDS-HT/hEDS definitions, and CLM-EDS-OI lists "changing
diagnostic criteria" among its limitations. Findings in this review are
therefore reported with the cohort's own label, and no claim is propagated
across terminological generations without that caveat.

## 2. Association with orthostatic intolerance and POTS

**Measured findings (associational, grade E2, confidence low — CLM-EDS-OI).**

- REF-ROWE-1999: 12 patients with EDS, chronic fatigue and orthostatic
  intolerance established a clinical association between EDS, orthostatic
  intolerance and fatigue (tagged in the registry to EDS, hEDS and ME/CFS).
  It did not establish any vascular-compliance parameter.
- REF-GAZIT-2003: orthostatic intolerance was common in a selected JHS cohort
  (48 JHS, 30 controls by questionnaire; 27 and 21 autonomically tested), with
  observed adrenergic hyperresponsiveness.
- REF-DEWANDELE-2014: autonomic abnormalities including Valsalva and tilt
  responses in 39 women with EDS-HT versus 35 controls (female-only,
  cross-sectional, with residual medication/pain/activity confounding).
- REF-CELLETTI-2017: co-occurrence of hypermobility-spectrum disease and
  autonomic/orthostatic abnormalities (observational, historical categories).
- REF-MILLER-POTS-2020: approximately 31% of a 91-patient single-center POTS
  clinic cohort met hEDS criteria. The registry is explicit that this is a
  clinic comorbidity estimate with referral and ascertainment bias — **not a
  population prevalence**, and not a causal vascular parameter.
- REF-ROMA-2018 (narrative review): synthesizes venous pooling, neuropathy,
  deconditioning, pain and medication hypotheses without reducing
  hEDS-associated orthostatic intolerance to one mechanism.

**Boundary:** these are E2 observations in selected cohorts. They justify a
distinct hEDS-associated orthostatic *scenario*; they do not identify a causal
parameter value (CLM-EDS-OI `parameter_implications`).

## 3. Vascular mechanics: indirect evidence only

CLM-EDS-VASCULAR (grade E1, confidence low) is the registry's most cautious
claim: human vascular-mechanics observations motivate investigation, but
arterial elasticity is not a direct measure of venous compliance.

**Measured findings.**

- REF-MILLER-2020 (60 people with EDS including 13 hEDS; no contemporaneous
  healthy control group): central pulse-wave velocity was lower than published
  healthy reference values; PWV did **not** correlate with standing HR/BP
  changes and did **not** differ across EDS types; no venous-compliance value
  for hEDS is supplied.
- REF-CHENG-2017 (nine POTS plus EDS-III patients in the reviewed record):
  cautionary evidence *against* assuming a large arterial-stiffness
  abnormality; the record notes that arterial stiffness is not venous
  capacitance and small venous effects cannot be excluded.

**No arterial-to-venous extrapolation.** The modeling-relevant quantity for
orthostatic pooling is peripheral *venous* compliance. The available
measurements are *arterial* (PWV, stiffness). The registry therefore forbids
treating arterial measurements as venous measurements, and
MEC-VASC-COMPLIANCE is classified `hypothesis_constrained_phenomenology`
(maturity M2, `exploratory: true`).

**No overgeneralization across EDS subtypes.** Vascular EDS and other
subtypes have distinct vascular biology; the hEDS configuration makes no
arterial-rupture representation and is labeled hEDS-specific
(`eds-heds-vascular` limitations). Findings from mixed-subtype cohorts
(REF-MILLER-2020) and historical EDS-III cohorts (REF-CHENG-2017) are not
attributed to hEDS specifically.

**Modeling assumption.** The `eds-heds-vascular` phenotype sets
PAR-LOWER-LIMB-VENOUS-COMPLIANCE = 70.0 mL/mmHg (healthy 60.0). This Stage 1.3
value replaces the legacy migration-derived number and remains an assumed
sensitivity value, not a measurement. Both hEDS configurations use the common
healthy anatomical hydrostatic heights without disease-specific overrides; both
PAR-SPLANCHNIC-RESISTANCE-SYMPATHETIC-GAIN and
PAR-LOWER-LIMB-RESISTANCE-SYMPATHETIC-GAIN = 0.7, PAR-HEART-RATE-REST = 70.0
bpm, and PAR-HEART-RATE-CARDIAC-SYMPATHETIC-GAIN and PAR-HEART-RATE-VAGAL-GAIN
= 30.0 bpm each. VAL-EDS-DIRECTION checks only that the assumed compliance
increase alters pooling and compensation in the expected direction while all
five stressed volumes are conserved; it tests the consequences of a
hypothesis, not its truth.

## 4. Contradictory baroreflex findings

The baroreflex evidence relevant to hEDS is internally contradictory and is
recorded as such in CLM-POTS-BAROREFLEX: REF-CELLETTI-2017 found **higher** —
not lower — resting spectral baroreflex sensitivity in JHS/EDS-HT, whereas
REF-FU-2010 found similar baroreflex function between POTS and controls.
Combined with the referral confounding and adrenergic hyperresponsiveness
reported in REF-GAZIT-2003, there is no defensible universal baroreflex-gain
abnormality for hEDS. The hEDS configurations therefore change no baroreflex
setpoint or scale parameter; the autonomic differences they carry are
calibrated chronotropic/resistance gains, labeled as assumptions.

## 5. Comorbidity with ME/CFS

REF-ROWE-1999 links EDS to chronic fatigue as well as orthostatic intolerance,
and the exploratory `eds-heds-mecfs-comorbid` configuration (M2,
`exploratory_comorbidity`) composes the hEDS vascular hypothesis with ME/CFS
PEM mechanisms. Its own limitation is authoritative: it demonstrates technical
composition only, with no claim that the joint parameter distribution is
epidemiologically typical. See `literature/cross_disease/review.md`.

## 6. Unimplemented hypotheses (M0/M1)

- **MEC-CONNECTIVE (M1, proposed).** Connective-tissue abnormalities may
  indirectly influence vascular properties and observable hemodynamics; no
  causal tissue-to-compliance equation is asserted and no parameters exist.
- **MEC-GI-DYSMOTILITY (M0, hypothesis).** GI dysmotility and postprandial
  pooling are a review topic only; current references identify no defensible
  dynamic GI equation or parameter.
- **MEC-PAIN-AUT (M0, hypothesis).** Pain–autonomic coupling requires
  dedicated evidence before implementation; no joint-instability-to-signal
  mapping is asserted.

All three are documented in this directory per the mechanism registry and have
no executable path.

## 7. Summary of evidence posture

| Claim | Grade | Posture |
|---|---|---|
| CLM-EDS-OI (hEDS–OI/POTS association) | E2, low | measured association in selected cohorts; scenario justification only |
| CLM-EDS-VASCULAR (vascular mechanics) | E1, low | indirect arterial evidence; venous-compliance value assumed |
| MEC-VASC-COMPLIANCE implementation | M2 | exploratory, hEDS-specific, sensitivity-analyzed (VAL-SENSITIVITY) |
| MEC-CONNECTIVE / MEC-GI-DYSMOTILITY / MEC-PAIN-AUT | M1/M0 | unimplemented hypotheses |
