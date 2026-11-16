# hEDS / EDS Mechanism Map

IDs refer to `literature/*.yaml`, `validation/validation_registry.yaml`, and
`simulations/simulation_registry.yaml`. Legend: **[measured]** human data in a
cited reference; **[assumption]** calibrated/chosen value or structure;
**[exploratory]** hypothesis-grade or unimplemented M0/M1 mechanism.

## Mechanism inventory for hEDS

| Mechanism | Maturity / status | Content | Claims | Parameters |
|---|---|---|---|---|
| MEC-VASC-COMPLIANCE | **M2, implemented, exploratory** | Increased lower-limb venous compliance tests whether regional vascular mechanics amplify orthostatic pooling | CLM-EDS-VASCULAR (E1), CLM-EDS-OI (E2) | PAR-LOWER-LIMB-VENOUS-COMPLIANCE = 58.3333 mL/mmHg **[assumption]** (healthy 50.0), migrated from the legacy aggregated value by 140 × 50/120 |
| MEC-VASC-POOLING | M3, implemented (shared) | Regional splanchnic and lower-limb venous-return opposition, EQ-ORT-001 | CLM-POTS-POOLING (E3), CLM-CV-HEMODYNAMICS (E3), CLM-ORTHO-SPLANCHNIC (E3) | PAR-SPLANCHNIC-GRAVITY-PRESSURE-OFFSET = 4.5 and PAR-LOWER-LIMB-GRAVITY-PRESSURE-OFFSET = 9.0 mmHg in hEDS configs **[assumption]** |
| MEC-AUT-BAROREFLEX | M3, implemented (shared) | Head-level-pressure sigmoidal target; separate vagal, cardiac-sympathetic, and vascular-sympathetic lags; chronotropic response (EQ-AUT-001/002/003) | CLM-POTS-BAROREFLEX (E3), CLM-AUT-VAGAL-FAST (E3), CLM-AUT-SYMPATHETIC-PATHWAYS (E3) | no hEDS-specific setpoint/scale override; only calibrated chronotropic and regional resistance gains |
| MEC-CONNECTIVE | **M1, proposed — unimplemented** | **[exploratory]** connective-tissue → vascular-mechanics link; documented here per the registry | CLM-EDS-OI, CLM-EDS-VASCULAR | none |
| MEC-GI-DYSMOTILITY | **M0, hypothesis — unimplemented** | **[exploratory]** GI dysmotility / postprandial pooling; no defensible equation | CLM-EDS-OI | none |
| MEC-PAIN-AUT | **M0, hypothesis — unimplemented** | **[exploratory]** pain–autonomic coupling; no signal mapping asserted | CLM-EDS-OI | none |

## Causal chain as implemented (M2 scenario)

```
[exploratory] connective-tissue difference (MEC-CONNECTIVE, no equation)
        │  — indirect motivation only; never an implemented arrow —
        ▼
[assumption] PAR-LOWER-LIMB-VENOUS-COMPLIANCE 50.0 → 58.3333  (MEC-VASC-COMPLIANCE)
        │  EQ-CV-001: lower lower-limb venous pressure per unit stressed volume
        ▼
upright input u → EQ-ORT-001 regional venous-return opposition (MEC-VASC-POOLING)
        │  amplified effective lower-limb pooling relative to healthy
        ▼
lower central volume → lower stroke volume (EQ-CV-004) → head-level pressure error
        ▼
EQ-AUT-001/002/003 differentiated autonomic compensation (MEC-AUT-BAROREFLEX)
        ▼
larger orthostatic HR rise than healthy  ── checked by VAL-EDS-DIRECTION
```

The arrow from connective tissue to compliance is deliberately **not**
implemented: CLM-EDS-VASCULAR is E1, the only direct human vascular data are
arterial (REF-MILLER-2020 PWV; REF-CHENG-2017 stiffness), and
arterial-to-venous extrapolation is prohibited by the registry's own
limitation fields.

## Configuration record

| Configuration | Maturity | Key overrides (all **[assumption]**) | Validation |
|---|---|---|---|
| `eds-heds-vascular` | M2 | lower-limb venous compliance 58.3333 mL/mmHg; splanchnic/lower-limb gravity offsets 4.5/9.0 mmHg; both regional resistance gains 0.7; HR rest 70.0 bpm; cardiac-sympathetic/vagal chronotropic gains 30.0/30.0 bpm | VAL-EDS-DIRECTION, VAL-SENSITIVITY |
| `eds-heds-mecfs-comorbid` | M2, exploratory_comorbidity | vascular overrides plus cerebral impairment 0.23, cerebral recovery τ 240.0 s, baseline capacity 0.85, extraction 0.74, delayed-stress τ 72000.0 s, PEM threshold 0.001, PEM gain 20.0 (PEM side anchored in ME/CFS claims CLM-ME-PEM-KINETICS / CLM-ME-CPET) | configuration-level checks via VAL-SW-CONFIG; PEM dynamics via VAL-ME-PEM / VAL-ME-CPET |

Both configurations are hEDS-specific and carry the limitation that they do
not generalize to vascular EDS or other EDS subtypes and make no
arterial-rupture representation.

## Validation and simulation posture

- **VAL-EDS-DIRECTION (M2):** the assumed compliance increase must alter
  orthostatic pooling and compensation in the expected direction, HR rise must
  exceed healthy, MAP must stay above 70 mmHg, volume must remain conserved,
  and sensitivity must include the healthy compliance value. Passing this test
  establishes that the hypothesis behaves as hypothesized — nothing more.
- **VAL-SENSITIVITY:** required because the compliance value is assumed
  (parameter registry: `sensitivity_required: true`).
- **SIM-EDS-VASCULAR:** persisted exploratory hEDS-only run; declared status
  "Hypothesis-constrained hEDS-only scenario; venous-compliance magnitude is
  assumed, not measured."
- **SIM-CROSS-DISEASE:** includes the hEDS vascular configuration alongside
  healthy, POTS, ME/CFS and Long COVID configurations under the explicit
  caveat of non-equivalent evidence levels.

## Boundaries and guardrails

1. **No arterial-to-venous extrapolation.** Arterial PWV/stiffness
   (REF-MILLER-2020, REF-CHENG-2017) never enters the model as venous
   compliance; the 58.3333 mL/mmHg lower-limb value is an assumption tested by
   sensitivity analysis, not a measurement. It was migrated from the legacy
   aggregated 140 mL/mmHg scenario by 140 × 50/120 and is not a newly measured
   hEDS coefficient.
2. **No cross-subtype generalization.** Labels JHS, EDS-HT/EDS-III and hEDS
   are retained per cohort; configurations are hEDS-specific; nothing is
   asserted about vascular EDS.
3. **Contradictory baroreflex evidence** (higher resting spectral BRS in
   JHS/EDS-HT, REF-CELLETTI-2017; similar BRS in POTS versus controls,
   REF-FU-2010) blocks any universal gain claim; no baroreflex structural
   parameter is changed for hEDS.
4. **Unimplemented M0/M1 modules** (MEC-CONNECTIVE, MEC-GI-DYSMOTILITY,
   MEC-PAIN-AUT) are documented here by registry designation; they have no
   parameters, equations, or tests and must not be cited as model behavior.
