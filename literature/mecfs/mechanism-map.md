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
   ▼  EQ-RCV-002  dD/dt = (L − D)/τ_D           τ_D = 43200 s in mecfs-pem [assumption]
delayed stress D
   │
   ▼  EQ-RCV-003  PEM_target = min(1, g·max(0,(D−θ)/(1−θ)))
                                   θ = 0.001, g = 20.0 in mecfs-pem  [assumption]
                                   (healthy θ = 99.0 disables PEM)
   │
   ▼  EQ-RCV-004  dPEM/dt with asymmetric τ
                                   τ_onset = 172800 s in mecfs-pem    [assumption]
                                   τ_recovery = 86400 s in mecfs-pem  [assumption]
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
"exploratory for equation form" on MEC-RCV-PEM.

## Cerebral-flow branch

```
arterial pressure P_a ──► EQ-CBF-001  CFI_target = (P_a/P_set)^α·(1 − β·u)
                          α = 0.8 [assumption]; β = 0.23 in mecfs-pem
                          ([measured] anchor: 26% vs 7% end-tilt reduction,
                           REF-VANCAMPEN-2020, E2/single-center Doppler)
                          ▼
EQ-CBF-002  asymmetric kinetics: τ_decline = 5 s; τ_recovery = 240 s in mecfs-pem
            ([measured] motivation: incomplete post-tilt recovery,
             REF-VANCAMPEN-2021; exact τ unmeasured → [assumption])
```

Guardrail encoded in CLM-ME-CBF: cerebral flow is **not** inferred from MAP
alone; the impairment term and recovery lag are explicit phenomenological
states. The index is normalized and is not a Doppler reconstruction.

## Configuration and validation

`phenotypes/mecfs/mecfs-pem.yaml` (M3, `phenomenological_dynamic_model`):
gravity offset 9.0; HR base 45.0; HR gain 50.0; cerebral impairment 0.23;
cerebral recovery τ 240.0 s; baseline capacity 0.85; extraction 0.74; PEM
threshold 0.001; PEM gain 20.0 — every entry a calibrated value inside a
declared registry sensitivity range.

| Validation | What it establishes | What it does not establish |
|---|---|---|
| VAL-ME-PEM (M3) | Delayed, non-immediate PEM with slow recovery; healthy stays PEM-free | Any molecular or inflammatory cause |
| VAL-ME-CPET (M3) | Subsequent capacity reduction within a predeclared broad 2–20% band around the 5.3%/13.8% anchors | Patient-level or prospective external validation |
| VAL-ME-CBF (M3) | End-tilt index reduction within a broad 15–35% band around the 26% group mean; healthy reduction smaller | Volumetric CBF accuracy or single-patient prediction |
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
