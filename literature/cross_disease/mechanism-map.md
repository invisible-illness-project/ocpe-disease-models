# Cross-Disease Mechanism Map

IDs refer to `literature/*.yaml`, `validation/validation_registry.yaml`, and
`simulations/simulation_registry.yaml`. Legend: **[measured]** human data in a
cited reference; **[assumption]** calibrated/chosen value or structure;
**[exploratory]** hypothesis-grade or unimplemented M0/M1 mechanism.

## One substrate, disease-specific overlays

All configurations share `src/ocpe_disease_models/models/shared/model.py`
(`ocpe:disease-models/shared-physiology`). Disease phenotypes are parameter
override sets over the shared equations; nothing disease-specific is coded as
separate dynamics except through declared mechanisms.

```
SHARED SUBSTRATE (M3)
  MEC-CV-VOLUME      EQ-CV-001..005   four conservative stressed-volume compartments,
                                      regional pressure-gradient flows, SV, CO
  MEC-AUT-BAROREFLEX EQ-AUT-001..003  head-level-pressure sigmoid; vagal, cardiac-
                                      sympathetic and vascular-sympathetic states
  MEC-VASC-POOLING   EQ-ORT-001       regional splanchnic/lower-limb pooling
  MEC-MUSCLE-PUMP    EQ-MP-001        conservative rhythmic lower-limb-to-central transfer
  MEC-SUSTAINED-CONTRACTION EQ-MP-002 lower-limb venous-resistance impediment
  MEC-CBF-AUTOREG    EQ-CBF-001/002   CPP-based normalized index, asymmetric kinetics

DISEASE OVERLAYS
  POTS       MEC-VASC-CONSTRICTION (EQ-VASC-001 regional gains) M3
             MEC-AUT-HYPERADRENERGIC (EQ-AUT-003 gains,
                                      EQ-AUT-001 scale)         M3
             MEC-VOL-HYPOVOLEMIA (initial-volume factor)        M3
             MEC-RAAS                                           M1  [exploratory, no impl]
  hEDS       MEC-VASC-COMPLIANCE (assumed lower-limb venous
             compliance 58.3333 versus healthy 50.0 mL/mmHg)     M2  [exploratory]
             MEC-CONNECTIVE                                     M1  [exploratory, no impl]
             MEC-GI-DYSMOTILITY, MEC-PAIN-AUT                   M0  [exploratory, no impl]
  ME/CFS     MEC-RCV-PEM (EQ-RCV-001..004)                      M3
             MEC-MET-CAPACITY (EQ-MET-001)                      M3
             MEC-MET-EXTRACTION (EQ-MET-002)                    M3
  Long COVID MEC-RCV-PEM / MEC-MET-CAPACITY /
             MEC-MET-EXTRACTION (shared, subgroup gains)        M3
             autonomic overlay (regional pooling + chronotropy) M3
             MEC-RESP-LC                                        M1  [exploratory, no impl]
             MEC-MICROVASC                                      M0  [exploratory, no impl]
  Cross      MEC-INFL-SIGNAL, MEC-SLEEP-CIRCADIAN               M0  [exploratory, no impl]
```

## Shared vs distinct parameter posture

| Parameter | Healthy | POTS overrides | hEDS overrides | ME/CFS | Long COVID |
|---|---|---|---|---|---|
| PAR-SPLANCHNIC-GRAVITY-PRESSURE-OFFSET | 4.0 mmHg | 5.0 (all four POTS configs) | 4.5 | 4.5 | 5.5 (autonomic) |
| PAR-LOWER-LIMB-GRAVITY-PRESSURE-OFFSET | 8.0 mmHg | 10.0 (all four POTS configs) | 9.0 | 9.0 | 11.0 (autonomic) |
| PAR-SPLANCHNIC-RESISTANCE-SYMPATHETIC-GAIN and PAR-LOWER-LIMB-RESISTANCE-SYMPATHETIC-GAIN | 0.8 each | 0.35 / 1.0 / 0.9 / 0.55 each by subtype | 0.7 each | — | — |
| PAR-HEART-RATE-CARDIAC-SYMPATHETIC-GAIN and PAR-HEART-RATE-VAGAL-GAIN | 20.0 bpm each | 40 / 70 / 60 / 50 bpm each by subtype | 30 each | 25 each | 50 each (autonomic) |
| PAR-BLOOD-VOLUME-FACTOR | 1.0 | 0.92 hypo / 0.96 mixed | — | — | — |
| PAR-LOWER-LIMB-VENOUS-COMPLIANCE | 50.0 mL/mmHg | — | 58.3333 (assumed) | — | — |
| PAR-CEREBRAL-ORTHOSTATIC-IMPAIRMENT | 0.0 | — | 0.23 (comorbid only) | 0.23 | 0.08 (autonomic) |
| PAR-CEREBRAL-RECOVERY-TIME-CONSTANT | 12.0 s | — | 240.0 s (comorbid) | 240.0 s | — |
| PAR-BASELINE-METABOLIC-CAPACITY | 1.0 | — | 0.85 (comorbid) | 0.85 | 0.85 / 0.8 |
| PAR-OXYGEN-EXTRACTION-FRACTION | 0.78 | — | 0.74 (comorbid) | 0.74 | 0.49 (exertional) |
| PAR-DELAYED-STRESS-TIME-CONSTANT | 21600.0 s | — | 72000.0 s (comorbid) | 72000.0 s | 21600.0 s (default) |
| PAR-PEM-TRIGGER-THRESHOLD | 0.999 (disables) | — | 0.001 (comorbid) | 0.001 | 0.001 |
| PAR-PEM-RESPONSE-GAIN | 0.0 | — | 20.0 (comorbid) | 20.0 | 12.0 / 16.0 |

Every non-healthy entry is **[assumption]** within a declared sensitivity
range unless explicitly marked as a range exception; measured anchors exist
only for direction, timing windows, and selected group-level magnitudes (e.g.,
0.49 extraction from REF-SINGH-2022; 0.74 from the REF-JOSEPH-2021 subgroup;
26% CBF reduction from REF-VANCAMPEN-2020). The healthy early-CO reduction
(approximately 5.64%) and healthy end-tilt CFI reduction (approximately 0.003%)
miss their broad soft anchors and remain explicit warnings. The ME/CFS PEM
scenario first crosses 0.05 at approximately 5.7 hours after the day-1 bout
ends, earlier than the 12–48-hour daily-activity onset window but within
reported post-CPET onset within 24 hours; its approximately 39.2-hour post-bout
peak is separately reported.

## Comorbidity composition

`eds-heds-mecfs-comorbid` (M2) is the only multi-disease configuration:
hEDS vascular overlay + ME/CFS PEM/exertional overlay. VAL-SW-CONFIG requires
deterministic composition and explicit failure on conflicting overrides; the
configuration's limitation forbids reading it as an epidemiologically typical
joint distribution. Comorbidity **evidence** (REF-ROWE-1999 EDS–fatigue–OI;
REF-MILLER-POTS-2020 clinic comorbidity estimate ~31%; REF-DAVIS-2023 and
REF-APPELMAN-2024 Long COVID–ME/CFS overlap) is associational and does not
identify shared parameters.

## Evidence/maturity boundary table

| Layer | Strongest statement permitted |
|---|---|
| E4 (CLM-POTS-CRITERIA, CLM-LC-HETEROGENEITY, CLM-LC-CPET) | Definitions, heterogeneity, group-level capacity differences — not mechanism magnitudes |
| E3 (hemodynamics, pooling, PEM kinetics, CPET direction, hyperadrenergic subset) | Direction and structure; calibrated magnitudes remain assumptions |
| E2 (hypovolemia, hEDS–OI, preload, CBF, LC autonomic/extraction/muscle) | Scenario anchors from selected cohorts; no prevalence claims |
| E1 (hEDS vascular, ME metabolism, LC endothelial, cross sleep) | Hypotheses; CLM-EDS-VASCULAR and CLM-LC-ENDOTHELIAL explicitly forbid numerical promotion |
| M0/M1 modules | Documentation-only; no executable path, parameters, or tests |

VAL-EMPIRICAL-ANCHORS and VAL-TRACEABILITY enforce these boundaries
mechanically; VAL-SCOPE-FUTURE covers declared-future scope.

## Simulation record

- **SIM-CROSS-DISEASE:** healthy, POTS neuropathic, exploratory hEDS vascular,
  ME/CFS PEM and Long COVID autonomic configurations under one orthostatic
  protocol, against VAL-PHYS-TILT, VAL-POTS-NEUROPATHIC, VAL-EDS-DIRECTION and
  VAL-LC-AUTONOMIC. Declared status: scenario comparison across non-equivalent
  evidence levels; not a comparative effectiveness or disease-severity
  ranking.
- Disease-specific runs: SIM-HEALTHY-BASELINE, SIM-POTS-ORTHOSTATIC,
  SIM-EDS-VASCULAR, SIM-ME-REPEATED-EXERTION, SIM-LC-AUTONOMIC (see each
  disease map).

## Unimplemented cross-disease modules mapped here

Per the mechanism registry, this document is the designated map for:

- **MEC-INFL-SIGNAL (M0, hypothesis).** Immune signaling may interact with
  autonomic and recovery states; **[exploratory]** with the explicit rule that
  biomarker associations (CLM-LC-ENDOTHELIAL, CLM-ME-METABOLISM) must not be
  converted into inflammatory causes of symptoms. No parameters, no equations,
  no tests.
- **MEC-SLEEP-CIRCADIAN (M0, hypothesis).** CLM-CROSS-SLEEP (E1) records
  autonomic day-night differences in selected groups but finds the evidence
  insufficient to parameterize a shared dynamic oscillator. No invented
  circadian parameters or sleep-derived disease multipliers; reserved for a
  future evidence-constrained oscillator/recovery extension.

Other unimplemented modules (MEC-RAAS, MEC-CONNECTIVE, MEC-GI-DYSMOTILITY,
MEC-PAIN-AUT, MEC-RESP-LC, MEC-MICROVASC) are mapped in their disease
directories. Any promotion requires new registry entries; this document
creates none.
