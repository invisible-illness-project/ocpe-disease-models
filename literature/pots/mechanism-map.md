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
| MEC-CV-VOLUME (conservative four-compartment hemodynamics) | M3, implemented | EQ-CV-001, EQ-CV-002, EQ-CV-003, EQ-CV-004, EQ-CV-005 | PAR-ARTERIAL-COMPLIANCE 1.5 mL/mmHg; PAR-CENTRAL-VENOUS-COMPLIANCE 140.0; PAR-SPLANCHNIC-VENOUS-COMPLIANCE 70.0; PAR-LOWER-LIMB-VENOUS-COMPLIANCE 50.0; PAR-SPLANCHNIC-ARTERIAL-RESISTANCE and PAR-LOWER-LIMB-ARTERIAL-RESISTANCE 2.20408 mmHg·s/mL each; PAR-SPLANCHNIC-VENOUS-RESISTANCE and PAR-LOWER-LIMB-VENOUS-RESISTANCE 0.122449 mmHg·s/mL each; PAR-STROKE-VOLUME-MAX 100.0 mL; PAR-STROKE-VOLUME-HALF-VOLUME 300.0 mL; PAR-CONTRACTILITY-SYMPATHETIC-GAIN 0.25 | CLM-CV-HEMODYNAMICS (E3), CLM-CV-VENOUS-RETURN (E3), CLM-ORTHO-SPLANCHNIC (E3) |
| MEC-AUT-BAROREFLEX (head-level-pressure feedback with distinct effector states) | M3, implemented | EQ-AUT-001, EQ-AUT-002, EQ-AUT-003 | PAR-BAROREFLEX-PRESSURE-SETPOINT 100.0 mmHg; PAR-BAROREFLEX-PRESSURE-SCALE 2.0 mmHg; PAR-CARDIAC-SYMPATHETIC-TIME-CONSTANT 6.0 s; PAR-VASCULAR-SYMPATHETIC-TIME-CONSTANT 10.0 s; PAR-VAGAL-TIME-CONSTANT 1.0 s; PAR-HEART-RATE-REST 70.0 bpm; healthy PAR-HEART-RATE-CARDIAC-SYMPATHETIC-GAIN and PAR-HEART-RATE-VAGAL-GAIN 20.0 bpm each; PAR-EXERCISE-HEART-RATE-GAIN 70.0 bpm | CLM-POTS-BAROREFLEX (E3), CLM-AUT-VAGAL-FAST (E3), CLM-AUT-SYMPATHETIC-PATHWAYS (E3), CLM-POTS-CRITERIA (E4) |

**[assumption]** All nominal values are explicit computational operating points
(parameter-registry policy); cited references support structure and direction,
not the numbers. Volume conservation is exact by construction (EQ-CV-003) and
checked by VAL-MATH-CONSERVATION; solver robustness by VAL-MATH-CONVERGENCE.

## POTS-specific mechanism overlay

```
upright input u ──> EQ-ORT-001 regional venous-return opposition [MEC-VASC-POOLING, M3]
                         │            ▲ CLM-POTS-POOLING (E3)
                         │            │ [measured] REF-STEWART-2003 pooling,
                         │            │ REF-JACOB-2000 / REF-GIBBONS-2013 denervation
                         ▼
        splanchnic + lower-limb pooling → lower regional venous return
                         │                   (four-volume conservation)
                         ▼
        lower central volume → lower SV (EQ-CV-004)
                         │
                         ▼
        head-level pressure error → EQ-AUT-001 sigmoid → EQ-AUT-002 lags
                         │
            ┌────────────┼───────────────────────────────┐
            ▼            ▼                               ▼
   EQ-AUT-003 HR   EQ-VASC-001 regional           separate vagal, cardiac-
   chronotropic    resistance modulation          sympathetic and vascular-
   compensation    (MEC-VASC-CONSTRICTION, M3)    sympathetic states
```

| Mechanism | Maturity / status | Role in POTS | Anchoring claims |
|---|---|---|---|
| MEC-VASC-POOLING | M3, implemented | Regional splanchnic and lower-limb venous-return opposition (EQ-ORT-001); direction [measured], magnitude **[assumption]** (regional gravity offsets are not angle-specific hydrostatics) | CLM-POTS-POOLING (E3), CLM-ORTHO-SPLANCHNIC (E3) |
| MEC-VASC-CONSTRICTION | M3, implemented | Vascular-sympathetic modulation of regional arterial resistances; neuropathic subtype reduces both regional gains | CLM-POTS-POOLING, CLM-POTS-PHENOTYPES (E3) |
| MEC-AUT-HYPERADRENERGIC | M3, implemented | Raised total chronotropic gain for the hyperadrenergic subgroup, split equally between cardiac-sympathetic and vagal pathways as a calibration choice; no catecholamine state | CLM-POTS-HYPERADRENERGIC (E3) |
| MEC-VOL-HYPOVOLEMIA | M3, implemented | Scales all four initial stressed volumes; PAR-BLOOD-VOLUME-FACTOR **[assumption]**, not the measured plasma deficit; exact resting fixed points require the configured resistance and pressure-setpoint adjustments | CLM-POTS-HYPOVOLEMIA (E2) |
| MEC-CBF-AUTOREG | M3, implemented (shared) | Bounded normalized index driven by cerebral perfusion pressure (head-level arterial pressure minus central venous back pressure) with asymmetric kinetics; no CO₂ mechanism | CLM-CBF-CPP (E3), CLM-CBF-AUTOREG-DYNAMIC (E3), CLM-ME-CBF (E2) |
| MEC-RAAS | **M1, proposed — unimplemented** | **[exploratory]** RAAS volume regulation documented in REF-RAJ-2005; no parameters, no equations, no tests | CLM-POTS-HYPOVOLEMIA (E2) |

## Phenotype configurations (all calibrated scenarios, not diagnoses)

| Configuration | Distinctive overrides (all **[assumption]**) | Mechanisms | Validation |
|---|---|---|---|
| `pots-neuropathic` | splanchnic/lower-limb gravity offsets 5.0/10.0 mmHg; both regional resistance gains 0.35; HR rest 70.0 bpm; cardiac-sympathetic/vagal chronotropic gains 40.0/40.0 bpm | MEC-VASC-POOLING, MEC-AUT-BAROREFLEX, MEC-VASC-CONSTRICTION | VAL-POTS-NEUROPATHIC |
| `pots-hyperadrenergic` | gravity offsets 5.0/10.0 mmHg; pressure scale 1.5 mmHg; HR rest 71.5 bpm; chronotropic gains 70.0/70.0 bpm; both regional resistance gains 1.0; fixed-point regional resistances adjusted | MEC-AUT-HYPERADRENERGIC, MEC-VASC-POOLING | VAL-POTS-HYPER |
| `pots-hypovolemic` | gravity offsets 5.0/10.0 mmHg; blood-volume factor 0.92; pressure setpoint 92.0 mmHg; pressure scale 6.0 mmHg; chronotropic gains 60.0/60.0 bpm; both regional resistance gains 0.9; fixed-point regional resistances adjusted | MEC-VOL-HYPOVOLEMIA, MEC-VASC-POOLING, MEC-AUT-BAROREFLEX | VAL-POTS-HYPO |
| `pots-mixed` (M2, exploratory composition) | gravity offsets 5.0/10.0 mmHg; blood-volume factor 0.96; pressure setpoint 96.0 mmHg; pressure scale 3.0 mmHg; both regional resistance gains 0.55; chronotropic gains 50.0/50.0 bpm; fixed-point regional resistances adjusted | all four subtype mechanisms | VAL-POTS-MIXED |

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
- The model does not represent pulsatile flow, 0.1 Hz oscillations,
  catecholamine dynamics, pure neural transmission delays, or CO₂-mediated
  cerebral vasomotion. Vagal, cardiac-sympathetic, and vascular-sympathetic
  states and splanchnic/lower-limb venous compartments are represented, but
  their gains, lags, compliances, and gravity offsets remain reduced-order
  assumptions. The healthy early-CO and control-side cerebral-response misses
  are retained as explicit soft-anchor warnings.
