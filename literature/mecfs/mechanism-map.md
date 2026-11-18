# ME/CFS Mechanism Map

IDs refer to `literature/*.yaml`, `validation/validation_registry.yaml`, and
`simulations/simulation_registry.yaml`. Legend: **[measured]** human data in a
cited reference; **[assumption]** calibrated/chosen value or structure;
**[exploratory]** hypothesis-grade or unimplemented M0/M1 mechanism.

## Mechanism inventory for ME/CFS

| Mechanism | Maturity / status | Role | Claims |
|---|---|---|---|
| MEC-RCV-PEM | M3, implemented | Delayed exertional stress and asymmetric PEM state | CLM-ME-PEM-KINETICS (E3), CLM-ME-CPET (E3), CLM-LC-PEM (E3) |
| MEC-MET-CAPACITY | M3, implemented | PEM-dependent normalized exertional capacity | CLM-ME-CPET (E3), CLM-LC-CPET (E4), CLM-ME-METABOLISM (E1) |
| MEC-MET-EXTRACTION | M3, implemented | Peripheral oxygen-extraction fraction, separable from cardiac output | CLM-ME-PRELOAD (E2), CLM-LC-EXTRACTION (E2) |
| MEC-CBF-AUTOREG | M3, implemented (shared) | Normalized cerebral-flow index with orthostatic impairment and slow recovery | CLM-ME-CBF (E2) |
| MEC-VASC-POOLING | M3, implemented (shared) | Orthostatic venous-return opposition (preload-side pathway) | CLM-POTS-POOLING (E3) |
| MEC-MICROVASC | **M0, hypothesis — unimplemented** | **[exploratory]** endothelial/microvascular; documented in `literature/long_covid/mechanism-map.md` | CLM-LC-ENDOTHELIAL (E1) |
| MEC-INFL-SIGNAL | **M0, hypothesis — unimplemented** | **[exploratory]** neuroimmune signaling; documented in `literature/cross_disease/mechanism-map.md` | CLM-LC-ENDOTHELIAL (E1), CLM-ME-METABOLISM (E1) |
| MEC-SLEEP-CIRCADIAN | **M0, hypothesis — unimplemented** | **[exploratory]** no oscillator parameters (CLM-CROSS-SLEEP, E1) | CLM-CROSS-SLEEP (E1) |

## The PEM dynamic chain (all normalized, phenomenological)

```
exertion input e
   │
   ▼  EQ-RCV-001  dL/dt = (e/C − L)/τ_L          τ_L = 1800 s        [assumption]
exertional load L  (C = current capacity, EQ-MET-001)
   │
   ▼  EQ-RCV-002  dD/dt = (L − D)/τ_D           τ_D = 72000 s in mecfs-pem [assumption]
delayed stress D
   │
   ▼  EQ-RCV-003  PEM_target = min(1, g·max(0,(D−θ)/(1−θ)))
                                   θ = 0.001, g = 20.0 in mecfs-pem  [assumption]
                                   (healthy θ = 0.999 and g = 0.0 disable PEM)
   │
   ▼  EQ-RCV-004  dPEM/dt with asymmetric τ
                                   τ_onset = 86400 s in mecfs-pem     [assumption]
                                   τ_recovery = 172800 s in mecfs-pem [assumption]
PEM state
   │
   ├──► EQ-MET-001  C = max(0.05, C_0·(1 − k_C·PEM))
   │                  C_0 = 0.85 in mecfs-pem                        [assumption]
   │                  → reduces subsequent functional capacity
   │                    ([measured] direction: CLM-ME-CPET day-2 declines)
   └──► EQ-MET-002  E_a-v = clip(E_0·(1 − k_EO·PEM), 0, 0.99);
                    F = C·E_a-v/0.78
                    E_0 = 0.74 in mecfs-pem (healthy 0.78)           [measured anchor:
                                                                       REF-JOSEPH-2021 subgroup]
```

**[measured] constraints on the chain:** PEM onset 12–48 h, peak ~48 h,
duration 2–7 days after daily activity; onset within 24 h and peak within 72 h
after CPET (REF-STUSSMAN-2020); day-2 VO2peak decrements of 13.8%
(REF-KELLER-2014) and 5.3% (REF-KELLER-2024) with negative replications noted
in CLM-ME-CPET. The time constants are operating points whose plausibility
windows these findings constrain; the equation *form* (first-order delay,
threshold, asymmetric recovery) is **[assumption]** — the registry records
"exploratory for equation form" on MEC-RCV-PEM. The 72000 s delayed-stress
constant is an explicit exception above the declared 14400–43200 s local
sensitivity range, not a patient measurement. In the current repeated-exertion
scenario, PEM first exceeds 0.05 at approximately 5.7 h after the day-1 bout
ends, earlier than the 12–48 h daily-activity onset window but within reported
post-CPET onset within 24 h; the separate peak at approximately 39.2 h after
the bout remains compatible with the delayed-peak evidence. This onset-window tension is retained as a limitation.

## Cerebral-flow branch

```
CPP = P_a − G_head·u − P_c ──► EQ-CBF-001  r = CPP/CPP_ref
        CFI_target = r/(s_ar + (1−s_ar)r) · (1−β·u)
                     CPP_ref = 95 mmHg, s_ar = 0.2 [assumptions]
                     β = 0.23 in mecfs-pem [calibrated assumption]
                     ([measured] anchor: 26% vs 7% end-tilt reduction,
                      REF-VANCAMPEN-2020, E2/single-center Doppler)
                          ▼
EQ-CBF-002  asymmetric kinetics: τ_decline = 5 s; τ_recovery = 240 s in mecfs-pem
            ([measured] motivation: incomplete post-tilt recovery,
             REF-VANCAMPEN-2021; exact τ unmeasured → [assumption])
```

Guardrail encoded in CLM-ME-CBF: cerebral flow is **not** inferred from MAP
alone; CPP includes the heart-to-head correction and venous back pressure, and
the impairment term and recovery lag are explicit phenomenological elements.
The index is normalized and is not a Doppler reconstruction. Stage 1.3 healthy
end-tilt CFI reduction is 4.961%, within the broad 3–11% disclosure band around
the reported 7% control finding; this is calibrated scenario agreement, not
independent control validation.

## Configuration and validation

`phenotypes/mecfs/mecfs-pem.yaml` (M3, `phenomenological_dynamic_model`):
common healthy anatomical hydrostatic heights; HR rest 70.0 bpm;
cardiac-sympathetic/vagal chronotropic gains 25.0/25.0 bpm; cerebral impairment
0.23; cerebral recovery τ 240.0 s; baseline capacity 0.85; extraction 0.74;
delayed-stress τ 72000.0 s (explicit range exception); PEM onset/recovery τ
86400.0/172800.0 s; PEM threshold 0.001; PEM gain 20.0. These are calibrated
scenario values, not patient measurements.

| Validation | What it establishes | What it does not establish |
|---|---|---|
| VAL-ME-PEM (M3) | Delayed, non-immediate PEM with slow recovery; healthy stays PEM-free | Any molecular or inflammatory cause |
| VAL-ME-CPET (M3) | Subsequent capacity reduction within a predeclared broad 2–20% band around the 5.3%/13.8% anchors | Patient-level or prospective external validation |
| VAL-ME-CBF (M3) | End-tilt index reduction within a broad 15–35% band around the 26% group mean; healthy reduction smaller; healthy 3–11% soft-band miss warned explicitly | Volumetric CBF accuracy, successful healthy-control reproduction, or single-patient prediction |
| VAL-PHYS-RECOVERY | Post-tilt recovery behavior | Recovery time-constant identification |

SIM-ME-REPEATED-EXERTION persists the scenario; declared status:
phenomenological PEM dynamics, not a cellular causal model or synthetic
cohort.

## Boundaries

- **Repeated-CPET heterogeneity is preserved:** anchors are reported as a
  range with negative replications acknowledged; the model is never fitted to
  one study (CLM-ME-CPET `modeling_implications`).
- **Preload and extraction remain separable** (CLM-ME-PRELOAD
  `modeling_implications`); no preload state exists beyond the shared
  venous-return chain.
- **No resting mitochondrial defect is asserted** (REF-WALITT-2024;
  CLM-ME-METABOLISM E1); the capacity state is phenomenology.
- **Unimplemented M0 modules** (MEC-MICROVASC, MEC-INFL-SIGNAL,
  MEC-SLEEP-CIRCADIAN) are mapped in their registry-designated documents and
  must not be cited as ME/CFS model behavior.
