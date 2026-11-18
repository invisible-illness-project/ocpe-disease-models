# Corrected Stage 1.3 causal dependency graph

## System graph

```mermaid
flowchart LR
    subgraph Inputs[Declared protocol inputs]
      A[tilt_angle_deg]
      E[exertion and muscle inputs]
      CO2[end_tidal_co2_mmHg]
    end

    subgraph Geometry[Common anatomy, not phenotype severity]
      Hs[splanchnic height 13.3 cm]
      Hl[lower-limb height 26.6 cm]
      Ho[other-systemic height 4.5 cm]
      Ha[aortic 0 cm / carotid 25 cm / brain 27 cm]
    end

    A --> HYD[0.7356 height sin angle]
    Hs --> HYD
    Hl --> HYD
    Ho --> HYD
    Ha --> SENSORP[Aortic and carotid sensed pressures]
    Ha --> CPP[Brain arterial pressure and cerebral perfusion pressure]

    HYD --> PSTAT[Regional effective pressures]
    V[Five stressed volumes] --> ELAST[V/C plus one-sided k_d excess-volume squared]
    C[Regional compliances] --> ELAST
    K[dependent venous k_d] --> ELAST
    BV[blood-volume factor] --> ELAST
    PSTAT --> GRAD[Pressure gradients]
    ELAST --> GRAD
    R[Regional resistances and sympathetic gains] --> GRAD
    GRAD --> F[Systemic and venous flows]
    F --> VDOT[Five volume derivatives; sum exactly zero]
    VDOT --> V

    Vc[Central-venous stressed volume] --> SV[Preload-dependent stroke volume]
    CS[Cardiac-sympathetic state] --> CONTRACT[Contractility]
    CONTRACT --> SV
    CS --> HR[Heart rate]
    VS[Vagal state] --> HR
    SV --> CO[Cardiac output]
    HR --> CO
    CO --> MAP[Systemic arterial pressure]

    MAP --> SENSORP
    SENSORP --> ERR[Weighted aortic/carotid error; weights sum to one]
    ERR --> AUT[Three independent autonomic states]
    AUT --> CS
    AUT --> VASC[Vascular-sympathetic state]
    AUT --> VS
    VASC --> R

    CPP --> AR[Bounded pressure autoregulation]
    SLOPE[cerebral residual slope 0.25] --> AR
    CO2 --> CO2F[Independent bounded CO2 factor]
    AR --> TARGET[Cerebral-flow target]
    CO2F --> TARGET
    TARGET --> CFI[Cerebral-flow index state]

    E --> MP[Rhythmic pump transfer or sustained-contraction resistance]
    MP --> VDOT
    E --> PEM[Load, delayed stress, PEM and capacity constructs]
```

## Corrections relative to the Stage 1.2 interpretation

1. **Gravity acts through common anatomy.** Disease YAML files modify physiological mechanisms; they no longer assign different splanchnic or lower-limb anatomical heights. This removes the unsupported causal claim that neuropathic, mixed, or other phenotypes possess different hydrostatic columns.
2. **Dependent pressure is nonlinear above the scaled supine stressed volume.** Volume and compliance determine the linear term; excess dependent volume activates the quadratic term. The causal direction is volume/configuration → pressure → flow → volume derivative, not a direct phenotype-specific volume injection.
3. **The residual bed is a real flow path.** Other-systemic volume has its own compliance, hydrostatic pressure, arterial/venous resistances, and sympathetic resistance gain. It is not a pressure-free blood sink.
4. **Conservation is independent of elastance.** The five volume derivatives telescope exactly. Changing compliance or `k_d` changes the constitutive pressure relation and allocation, not the conservation identity.
5. **Sensor weighting is coupled.** Aortic and carotid weights are one paired degree of freedom. Their perturbations must preserve `w_a + w_c = 1`; they are not two independently identifiable weights from the present outputs.
6. **Cardiac and vascular compensation are distinct.** Cardiac sympathetic activity affects HR and contractility; vascular sympathetic activity affects regional arterial resistance; vagal activity separately affects HR. Isolated experiments quantify their different downstream effects before combination.
7. **Cerebral CO₂ is an independent declared input.** Tilt changes brain hydrostatic pressure but never infers hypocapnia. CFI does not feed back into systemic pressure in this reduced-order model.
8. **PEM remains phenomenological and separate.** Exertion/delayed-stress/capacity states are not relabeled as measured molecular, symptom, or patient-level causal processes.

## Feedback and non-additivity

The graph contains feedback: posture changes regional pressures and volumes; volumes/flows alter preload, SV, CO, and MAP; MAP changes baroreflex error; autonomic states alter HR, contractility, and resistances; those changes alter flows and volumes. Consequently, isolated parameter effects are not expected to sum to the combined response.

The fresh mechanism matrix demonstrates this non-additivity. Common geometry alone causes excessive output loss under the Stage 1.2 compensation structure, while dependent elastance alone reduces pooling and CO loss. The final result arises from their interaction with compensation changes, not from any single parameter or a linear sum of isolated effects.
