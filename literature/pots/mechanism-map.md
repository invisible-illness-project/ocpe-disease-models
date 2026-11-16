# POTS Mechanism Map

This map connects POTS evidence claims to mechanisms, equations, parameters,
phenotype configurations, validations, and the curated simulation record. IDs
refer to the registry files under `literature/` and
`validation/validation_registry.yaml` / `simulations/simulation_registry.yaml`.
Legend: **[measured]** = human data in a cited reference; **[assumption]** =
calibrated/chosen model value or structure; **[exploratory]** = hypothesis-grade
or unimplemented M0/M1 mechanism.

## Shared substrate (inherited by every POTS configuration)

| Mechanism | Maturity / status | Equations | Key parameters | Claims |
|---|---|---|---|---|
| MEC-CV-VOLUME (conservative three-compartment hemodynamics) | M3, implemented | EQ-CV-001, EQ-CV-002, EQ-CV-003, EQ-CV-004, EQ-CV-005 | PAR-ARTERIAL-COMPLIANCE 1.5 mL/mmHg; PAR-CENTRAL-VENOUS-COMPLIANCE 140.0; PAR-PERIPHERAL-VENOUS-COMPLIANCE 120.0; PAR-SYSTEMIC-RESISTANCE ~1.102 mmHg·s/mL; PAR-VENOUS-RETURN-RESISTANCE ~0.0612; PAR-STROKE-VOLUME-MAX 100.0 mL; PAR-STROKE-VOLUME-HALF-VOLUME 300.0 mL; PAR-CONTRACTILITY-SYMPATHETIC-GAIN 0.25 | CLM-CV-HEMODYNAMICS (E3, REF-GEDDES-2022) |
| MEC-AUT-BAROREFLEX (sigmoidal baroreflex feedback) | M3, implemented | EQ-AUT-001, EQ-AUT-002, EQ-AUT-003 | PAR-BAROREFLEX-PRESSURE-SETPOINT 100.0 mmHg; PAR-BAROREFLEX-PRESSURE-SCALE 2.0 mmHg; PAR-SYMPATHETIC-TIME-CONSTANT 4.0 s; PAR-HEART-RATE-BASE 50.0; PAR-HEART-RATE-SYMPATHETIC-GAIN 40.0; PAR-EXERCISE-HEART-RATE-GAIN 70.0 | CLM-POTS-BAROREFLEX (E3), CLM-POTS-CRITERIA (E4) |

**[assumption]** All nominal values are explicit computational operating points
(parameter-registry policy); cited references support structure and direction,
not the numbers. Volume conservation is exact by construction (EQ-CV-003) and
checked by VAL-MATH-CONSERVATION; solver robustness by VAL-MATH-CONVERGENCE.

## POTS-specific mechanism overlay

```
upright input u ──> EQ-ORT-001 venous-return opposition  [MEC-VASC-POOLING, M3]
                         │            ▲ CLM-POTS-POOLING (E3)
                         │            │ [measured] REF-STEWART-2003 pooling,
                         │            │ REF-JACOB-2000 / REF-GIBBONS-2013 denervation
                         ▼
        lower venous return → lower central volume → lower SV (EQ-CV-004)
                         │
                         ▼
        arterial pressure error → EQ-AUT-001 sigmoid → EQ-AUT-002 lag
                         │
            ┌────────────┼───────────────────────────────┐
            ▼            ▼                               ▼
   EQ-AUT-003 HR   EQ-VASC-001 resistance        PAR gain settings per
   chronotropic    modulation                    subtype (calibrated)
   compensation    (MEC-VASC-CONSTRICTION, M3)
```

| Mechanism | Maturity / status | Role in POTS | Anchoring claims |
|---|---|---|---|
| MEC-VASC-POOLING | M3, implemented | Orthostatic venous-return opposition (EQ-ORT-001); direction [measured], magnitude **[assumption]** (normalized gravity offset is not angle-specific hydrostatics) | CLM-POTS-POOLING (E3) |
| MEC-VASC-CONSTRICTION | M3, implemented | Sympathetic resistance modulation; neuropathic subtype reduces the gain | CLM-POTS-POOLING, CLM-POTS-PHENOTYPES (E3) |
| MEC-AUT-HYPERADRENERGIC | M3, implemented | Raised chronotropic gain for the hyperadrenergic subgroup; no catecholamine state | CLM-POTS-HYPERADRENERGIC (E3) |
| MEC-VOL-HYPOVOLEMIA | M3, implemented | Scales initial stressed volumes; PAR-BLOOD-VOLUME-FACTOR **[assumption]**, not the measured plasma deficit | CLM-POTS-HYPOVOLEMIA (E2) |
| MEC-CBF-AUTOREG | M3, implemented (shared) | Normalized cerebral-flow index motivated by POTS orthostatic CBF findings (REF-DELPOZZI-2014) | CLM-ME-CBF (E2) |
| MEC-RAAS | **M1, proposed — unimplemented** | **[exploratory]** RAAS volume regulation documented in REF-RAJ-2005; no parameters, no equations, no tests | CLM-POTS-HYPOVOLEMIA (E2) |

## Phenotype configurations (all calibrated scenarios, not diagnoses)

| Configuration | Distinctive overrides (all **[assumption]**) | Mechanisms | Validation |
|---|---|---|---|
| `pots-neuropathic` | gravity offset 10.0; resistance gain 0.35; HR base 37.5; HR gain 65.0 | MEC-VASC-POOLING, MEC-AUT-BAROREFLEX, MEC-VASC-CONSTRICTION | VAL-POTS-NEUROPATHIC |
| `pots-hyperadrenergic` | gravity offset 10.0; pressure scale 1.5; HR base 20.0; HR gain 103.0; resistance gain 1.0 | MEC-AUT-HYPERADRENERGIC, MEC-VASC-POOLING | VAL-POTS-HYPER |
| `pots-hypovolemic` | gravity offset 10.0; blood-volume factor 0.92; pressure scale 6.0; HR base 30.0; HR gain 80.0; resistance gain 0.9 | MEC-VOL-HYPOVOLEMIA, MEC-VASC-POOLING, MEC-AUT-BAROREFLEX | VAL-POTS-HYPO |
| `pots-mixed` (M2, exploratory composition) | gravity offset 10.0; blood-volume factor 0.96; pressure scale 3.0; resistance gain 0.55; HR base 32.5; HR gain 75.0 | all four subtype mechanisms | VAL-POTS-MIXED |

Diagnostic framing for all four comes from CLM-POTS-CRITERIA (E4,
REF-SHELDON-2015): sustained orthostatic HR rise ≥30 bpm (≥40 bpm adolescents)
without orthostatic hypotension — an acceptance metric, not a validity proof.
Qualitative orthostatic behavior is independently checked by VAL-PHYS-TILT and
VAL-PHYS-BASELINE; empirical anchor provenance by VAL-EMPIRICAL-ANCHORS;
parameter sensitivity by VAL-SENSITIVITY.

## Simulation record

SIM-POTS-ORTHOSTATIC persists the neuropathic, hyperadrenergic and hypovolemic
configurations under the head-up-tilt protocol against VAL-POTS-NEUROPATHIC,
VAL-POTS-HYPER, VAL-POTS-HYPO and VAL-EMPIRICAL-ANCHORS. Its declared
scientific status: "Calibrated subgroup scenarios; passing an HR threshold is
not diagnostic validation." The mixed configuration is validated structurally
(VAL-POTS-MIXED) but is not part of the persisted POTS simulation record.

## Boundaries

- **[exploratory]** MEC-RAAS (M1) is mapped here as the registry's designated
  documentation location (`implementation: literature/pots/mechanism-map.md`);
  it has no executable path.
- Conflicting baroreflex evidence (REF-FU-2010 versus REF-CELLETTI-2017; see
  CLM-POTS-BAROREFLEX limitations) forbids a universal gain-reduction claim;
  only calibrated scenario gains exist.
- The model does not represent pulsatile flow, vagal pathways, 0.1 Hz
  oscillations, splanchnic compartment detail, or catecholamine dynamics.
