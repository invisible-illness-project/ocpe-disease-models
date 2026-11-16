# Computational architecture

## Design decision and upstream boundary

The assignment calls for OCPE-backed simulation, but inspection of the pinned OCPE 0.1 revision shows that it is a specification and semantic-interoperability engine, not a numerical simulator. Its historical solver was archived during commit `64ef9e296b12e21b1f4909f2c46dc0d5e25169e7`. This repository therefore uses a deliberate split rather than claiming a nonexistent upstream numerical capability:

| Responsibility | Owner |
|---|---|
| CURIEs, quantities, concepts, functional forms, model specifications, units, evidence/reference integrity, observation schemas, strict package validation | Pinned upstream OCPE |
| Executable ODEs, initial conditions, solver settings, phenotype composition, protocols, compact simulation traces | `ocpe-disease-models` |
| Disease evidence, equations, parameters, implementations, validation and simulation provenance | `ocpe-disease-models` registries |
| Observation unit/name adaptation and strict OCPE record validation | Adapter and observation-mapping interfaces |

OCPE is pinned at `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`. Upstream is not modified or vendored. The local `ocpe/packages/disease-models` directory is a domain package, not a copy of the engine.

## Five modeling layers

```text
Protocols: rest | tilt | tilt recovery | inactive standing |
           light rhythmic activity | walking | sustained contraction |
           single exertion | seven-day repeated exertion/recovery
                         │
                         ▼
Layer 4: dynamic stress and recovery states
                         │
Layer 1: shared cardiovascular/autonomic core ◄── Layer 2: mechanism parameters
                         │                              │
                         │                    Layer 3: phenotype YAML composition
                         ▼
Latent states and derived physiological outputs
                         │
                         ▼
Layer 5: explicit observation mapping ──► strict OCPE observation records
                         │
                         ▼
Small validation traces + provenance + independently reported validation
```

1. **Core physiology (Stage 1 revision, model version 0.2.0).** Four conserved stressed-volume compartments (arterial, central venous, splanchnic venous, lower-limb venous), regional resistance-driven flows, preload/contractility stroke volume, a head-level baroreflex pressure proxy, and three differentiated autonomic effector states. The scientific design gate and migration record are in `docs/stage1/revised-physiological-architecture.md`; the audited original architecture is preserved in `docs/stage1/baseline-scientific-report.md`.
2. **Disease mechanisms.** Parameterized reductions in volume or vascular compensation, altered chronotropic feedback, exploratory venous compliance, cerebral impairment, oxygen extraction, and PEM recovery.
3. **Phenotypes.** YAML records combine coherent mechanisms, evidence links, parameter overrides, maturity, and limitations. Conflicting ad hoc composition raises an error; it never depends on override order.
4. **Stress and recovery.** Normalized upright, exertion, rhythmic-muscle-activity, and sustained-contraction inputs drive ordinary differential equations; the rhythmic and sustained muscle inputs are independent of metabolic exertion and of each other. PEM uses an explicit delayed-state approximation rather than an immediate fatigue multiplier.
5. **Observations.** Latent/derived values remain distinct from observation records. The mapper resolves native output names and units before strict OCPE validation.

## State and input model

Time is seconds, volumes are mL, pressures are mmHg, and internal flows are mL/s. Heart rate is beats/min and exported cardiac output is L/min.

| State | Meaning | Initial condition |
|---|---|---|
| `arterial_volume` | Arterial stressed volume | `arterial_volume_initial × blood_volume_factor` |
| `central_venous_volume` | Central venous stressed volume/preload surrogate | `central_venous_volume_initial × blood_volume_factor` |
| `splanchnic_venous_volume` | Splanchnic venous stressed volume | `splanchnic_venous_pressure_initial × splanchnic_venous_compliance × blood_volume_factor` |
| `lower_limb_venous_volume` | Lower-limb venous stressed volume | `lower_limb_venous_pressure_initial × lower_limb_venous_compliance × blood_volume_factor` |
| `cardiac_sympathetic_state` | Cardiac sympathetic effector state | 0.5 |
| `vascular_sympathetic_state` | Vascular sympathetic effector state | 0.5 |
| `vagal_state` | Vagal cardiac effector state | 0.5 |
| `exertional_load` | Capacity-normalized exertional load | 0 |
| `delayed_stress` | Delayed exertional stress | 0 |
| `pem_severity` | Normalized phenomenological PEM severity | 0 |
| `cerebral_flow_index` | Normalized cerebral-flow approximation | Computed from the CPP pressure curve at the configured initial pressures |

The former single `sympathetic_state` is no longer a state or control input; a value with that name is exported only as a labeled compatibility summary equal to the arithmetic mean of the cardiac and vascular sympathetic states.

`ProtocolSegment` supplies four bounded normalized inputs—`upright`, `exertion`, `rhythmic_muscle_activity`, and `sustained_muscle_contraction`—over ordered, non-overlapping intervals. The rhythmic and sustained muscle inputs are declared independently of metabolic exertion, so supine rest, inactive standing, light rhythmic activity, walking, and sustained contraction are distinct protocol conditions. The upright input is not an angle-specific hydrostatic solution. The exertion input is normalized and is not a measured watt or VO2 value.

## Conservative hemodynamics

The implementation follows `EQ-CV-001` through `EQ-CV-005`, `EQ-ORT-001`, and `EQ-MP-001`/`EQ-MP-002`:

```text
Pa = Va/Ca        Pc = Vc/Cc        Ps = Vs/Cs        Pl = Vl/Cl
Qs,a = max(0, (Pa-Ps)/Rs,a_eff)        Ql,a = max(0, (Pa-Pl)/Rl,a_eff)
Qs,v = max(0, (Ps-Pc-Gs×upright)/Rs,v)
Qpump = f_pump × SV_pump × η_pump × rhythmic × Vl/(Vl+K_pump)
Ql,v = max(0, (Pl-Pc-Gl×upright)/Rl,v_eff) + Qpump
Qco  = HR/60 × SV

dVa/dt = Qco-Qs,a-Ql,a
dVc/dt = Qs,v+Ql,v-Qco
dVs/dt = Qs,a-Qs,v
dVl/dt = Ql,a-Ql,v
```

Consequently `d(Va+Vc+Vs+Vl)/dt = 0` analytically; the four volume derivatives telescope exactly. The muscle pump transfers volume from the lower-limb to the central venous compartment—it does not create blood—and the pump flow is added outside the nonnegative passive-gradient floor so a negative passive gradient cannot cancel a declared contraction. Sustained contraction instead raises lower-limb venous resistance. Nonnegative flow clamps are constitutive boundary choices, not evidence of venous valve or collapsible-vessel behavior.

`blood_volume_factor` scales all four initial volumes, but uniform volume scaling alone does not preserve the exact supine fixed point; each phenotype derives its regional resistances and pressure setpoint so that its complete initial state is a fixed point (tested for all ten configurations with maximum absolute RHS component below 1e-9).

## Autonomic, cerebral, metabolic, and recovery subsystems

- `EQ-AUT-001..003`: a sigmoidal head-level-pressure baroreflex target; first-order cardiac-sympathetic, vascular-sympathetic, and vagal lags (distinct time constants, fast vagal versus slower sympathetic); and HR from resting, cardiac-sympathetic, vagal, and exertion terms. The cardiac-sympathetic/vagal chronotropic gain split at fixed total gain is unidentified by current evidence and is sensitivity-tested explicitly.
- `EQ-VASC-001`: regional splanchnic and lower-limb arterial resistances modulated by the vascular sympathetic state; exertional vasodilation applies to the lower-limb arterial path only.
- `EQ-CBF-001..002`: cerebral perfusion pressure (arterial pressure minus the orthostatic heart–brain hydrostatic offset and central venous back pressure) feeding a bounded autoregulation proxy and an asymmetric decline/recovery cerebral-flow index. It is not a Doppler reconstruction and lacks CO2 and vascular territories.
- `EQ-MET-001..002`: normalized metabolic and functional capacity with oxygen extraction. These are not direct mitochondrial or VO2 states.
- `EQ-RCV-001..004`: exertional load, delayed stress, thresholded PEM target, and asymmetric onset/recovery. The equations are phenomenological; they do not assert a molecular cause.

All 20 equation records and all 52 parameter fields have stable registry entries and source-code references.

## Numerical execution

`ComputationalPatient.simulate()` uses SciPy `solve_ivp` with DOP853, protocol-specific output sampling, maximum step, relative tolerance, and absolute tolerance. It rejects empty/overlapping protocols, invalid parameter domains, failed solver returns, non-finite states, negative stressed volumes, autonomic states outside [0, 1], and cerebral-flow-index values outside their declared bounds. Convergence tests independently tighten tolerances and step size. The current model is deterministic; the recorded seed is metadata for forward compatibility and no random numbers are consumed.

Each `SimulationResult` stores arrays plus parameters, protocol, configuration SHA-256, model/OCPE versions, Python/NumPy/SciPy versions, solver settings, and scientific status. This makes an output trace auditable without turning it into a large dataset.

## Validation architecture

Seven validation layers are separate from the five modeling layers. Software, mathematical, physiological, disease-phenotype, empirical, sensitivity/uncertainty, and scientific-traceability results cannot substitute for each other. Registry IDs connect tests to mechanisms and outputs; `scripts/run_validation.py` fails on an empty required test selection. Maturity M0–M4 is assigned per mechanism/phenotype, not inferred from suite success. The mathematical layer tests the exact supine fixed point of every one of the ten registered configurations and exact four-volume conservation including walking and sustained-contraction protocols; the disease-phenotype layer applies the **sustained** orthostatic criterion (mean HR over the final 120 s of the upright window minus the supine baseline), with the peak first-300-s rise reported separately as a secondary metric.

## Source-layout and packaging limits

The wheel contains Python code, while phenotype/protocol/domain-package discovery currently expects a source checkout or explicit root/package path. `OCPE_DM_ROOT` resolves simulation configuration discovery; OCPE adapter callers may need an explicit `package_dir` in a wheel-only deployment. This is an unresolved packaging limitation, not silent portable data packaging.
