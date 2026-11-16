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
Protocols: rest | tilt | recovery | exertion | repeated exertion
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

1. **Core physiology.** Three conserved stressed-volume compartments, resistance-driven flows, preload/sympathetic stroke volume, and sigmoidal pressure feedback.
2. **Disease mechanisms.** Parameterized reductions in volume or vascular compensation, altered chronotropic feedback, exploratory venous compliance, cerebral impairment, oxygen extraction, and PEM recovery.
3. **Phenotypes.** YAML records combine coherent mechanisms, evidence links, parameter overrides, maturity, and limitations. Conflicting ad hoc composition raises an error; it never depends on override order.
4. **Stress and recovery.** Normalized upright and exertional inputs drive ordinary differential equations. PEM uses an explicit delayed-state approximation rather than an immediate fatigue multiplier.
5. **Observations.** Latent/derived values remain distinct from observation records. The mapper resolves native output names and units before strict OCPE validation.

## State and input model

Time is seconds, volumes are mL, pressures are mmHg, and internal flows are mL/s. Heart rate is beats/min and exported cardiac output is L/min.

| State | Meaning | Initial condition |
|---|---|---|
| `arterial_volume` | Arterial stressed volume | `arterial_volume_initial × blood_volume_factor` |
| `central_venous_volume` | Central venous stressed volume/preload surrogate | `central_venous_volume_initial × blood_volume_factor` |
| `peripheral_venous_volume` | Peripheral venous stressed volume | `peripheral_venous_volume_initial × blood_volume_factor` |
| `sympathetic_state` | Bounded autonomic feedback state | 0.5 |
| `exertional_load` | Capacity-normalized exertional load | 0 |
| `delayed_stress` | Delayed exertional stress | 0 |
| `pem_severity` | Normalized phenomenological PEM severity | 0 |
| `cerebral_flow_index` | Normalized cerebral-flow approximation | Pressure-derived initial target |

`ProtocolSegment` supplies bounded `upright` and `exertion` inputs over ordered, non-overlapping intervals. The upright input is not an angle-specific hydrostatic solution. The exertion input is normalized and is not a measured watt or VO2 value.

## Conservative hemodynamics

The implementation follows `EQ-CV-001` through `EQ-CV-005` and `EQ-ORT-001`:

```text
Pa = Va/Ca                 Pc = Vc/Cc                 Pp = Vp/Cp
Qsys = max(0, (Pa-Pp)/Rsys_effective)
Qvr  = max(0, (Pp-Pc-G×upright)/Rvr)
Qco  = HR/60 × SV

dVa/dt = Qco-Qsys
dVp/dt = Qsys-Qvr
dVc/dt = Qvr-Qco
```

Consequently `d(Va+Vc+Vp)/dt = 0` analytically. Nonnegative flow clamps are constitutive boundary choices, not evidence of venous valve or collapsible-vessel behavior.

## Autonomic, cerebral, metabolic, and recovery subsystems

- `EQ-AUT-001..003`: a sigmoidal arterial-pressure target, first-order sympathetic lag, and HR from base/sympathetic/exertion terms.
- `EQ-VASC-001`: effective systemic resistance modulated by sympathetic state and exertion.
- `EQ-CBF-001..002`: a normalized pressure/orthostatic cerebral target with asymmetric decline and recovery. It is not a Doppler reconstruction and lacks CO2 and vascular territories.
- `EQ-MET-001..002`: normalized metabolic and functional capacity with oxygen extraction. These are not direct mitochondrial or VO2 states.
- `EQ-RCV-001..004`: exertional load, delayed stress, thresholded PEM target, and asymmetric onset/recovery. The equations are phenomenological; they do not assert a molecular cause.

All 18 equation records and all 35 parameter fields have stable registry entries and source-code references.

## Numerical execution

`ComputationalPatient.simulate()` uses SciPy `solve_ivp` with DOP853, protocol-specific output sampling, maximum step, relative tolerance, and absolute tolerance. It rejects empty/overlapping protocols, invalid parameter domains, failed solver returns, and non-finite states. Convergence tests independently tighten tolerances and step size. The current model is deterministic; the recorded seed is metadata for forward compatibility and no random numbers are consumed.

Each `SimulationResult` stores arrays plus parameters, protocol, configuration SHA-256, model/OCPE versions, Python/NumPy/SciPy versions, solver settings, and scientific status. This makes an output trace auditable without turning it into a large dataset.

## Validation architecture

Seven validation layers are separate from the five modeling layers. Software, mathematical, physiological, disease-phenotype, empirical, sensitivity/uncertainty, and scientific-traceability results cannot substitute for each other. Registry IDs connect tests to mechanisms and outputs; `scripts/run_validation.py` fails on an empty required test selection. Maturity M0–M4 is assigned per mechanism/phenotype, not inferred from suite success.

## Source-layout and packaging limits

The wheel contains Python code, while phenotype/protocol/domain-package discovery currently expects a source checkout or explicit root/package path. `OCPE_DM_ROOT` resolves simulation configuration discovery; OCPE adapter callers may need an explicit `package_dir` in a wheel-only deployment. This is an unresolved packaging limitation, not silent portable data packaging.
