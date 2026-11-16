# Stage 1 revised physiological architecture and design review

## Decision status

This proposal is the scientific design gate required before equation implementation. It selects the smallest architecture that separates mechanisms needed by Stage 2 without claiming patient-level validity. The original implementation and fixtures remain archived under `validation/baseline/stage0/`.

**Review disposition.** Independent analytical review initially returned REVISE. The blocking findings—head-level baroreflex reference, incomplete migration formulas, OCPE declarative divergence, and per-phenotype fixed-point coverage—are resolved in this revision. The review analytically confirmed conservation, units, healthy equilibrium, CFI curve properties, regional gravity/pump placement, minimality, and inclusion of the PEM configuration correction. Implementation is authorized only for the mechanisms and consistency corrections classified above.

## Architecture decision

The revised shared model contains four conservative stressed-volume compartments, three autonomic effector states, an explicit protocol-driven skeletal-muscle-pump flow, and a cerebral-perfusion-pressure-based normalized proxy. The phenomenological exertion/PEM equations are retained, while their contradictory onset/recovery configuration is corrected and revalidated explicitly.

```text
                         cardiac sympathetic ──> contractility ──> SV ──> CO
                         vagal + cardiac sympathetic ──> HR ────────╯
 arterial pressure ──> baroreflex
                         vascular sympathetic ──> splanchnic arterial R
                                                  lower-limb arterial R

 CO ──> arterial volume ──> splanchnic arterial flow ──> splanchnic venous volume
                      └──> lower-limb arterial flow ────> lower-limb venous volume
 central venous volume <── splanchnic venous return <── splanchnic volume + gravity
 central venous volume <── lower-limb venous return <── lower-limb volume + gravity
                                                       + rhythmic muscle-pump flow
                                                       / sustained-contraction R

 brain-level CPP = arterial P - orthostatic heart–brain offset - central venous P
 CPP ──> bounded autoregulation proxy ──> dynamic normalized cerebral-flow index
```

Splanchnic and lower-limb compartments are separate because human tilt studies show splanchnic filling and region-specific volume/resistance responses. No additional renal, pulmonary, interstitial, or cardiac pressure–volume compartment is introduced.

## Change classification

| Change | Classification | Rationale |
|---|---|---|
| Conserve volume across arterial, central, splanchnic, and lower-limb compartments | Necessary correction | Makes regional pooling and volume movement explicit |
| Separate splanchnic and lower-limb venous volumes and return paths | Evidence-supported improvement | Upright splanchnic loading differs from limb pooling and LBNP |
| Separate cardiac sympathetic, vascular sympathetic, and vagal states | Evidence-supported improvement | Prevents HR from proxying all autonomic activity |
| Give vagal, cardiac sympathetic, and vascular sympathetic pathways distinct lags | Evidence-supported improvement | Represents fast vagal versus slower sympathetic effects without a DDE |
| Add rhythmic muscle-pump flow based on contraction frequency, pumped volume, and venous volume | Evidence-supported improvement | Represents walking/light activity independently of metabolic exertion |
| Increase lower-limb venous resistance during sustained contraction | Evidence-supported improvement, calibrated magnitude | Represents mechanical impediment rather than treating all activity as beneficial |
| Use brain-level CPP and a bounded autoregulation proxy for CFI | Necessary correction to interpretation; evidence-supported structure | Systemic MAP alone is not cerebral perfusion pressure |
| Retain reduced-order preload-dependent SV | Deliberate retention | More detailed cardiac PV mechanics are not identifiable from current data |
| Retain stressed volumes only; no dynamic unstressed-volume reservoir | Deliberate retention | The concept is established, but regional human values and control laws are too uncertain for this scope |
| Retain disease-specific cerebral impairment multipliers | Exploratory hypothesis | Needed for existing ME/CFS/Long COVID scenario semantics; not a direct measurement |
| Retain PEM equations | Out of cardiovascular redesign scope | Avoids silent Stage 2 disease-mechanism changes |
| Correct ME/CFS onset/recovery time-constant inversion | Necessary consistency correction | The calibrated scenario currently makes recovery faster than onset despite claiming prolonged recovery |
| Align the OCPE declarative model with executable equations | Necessary consistency correction | The current package declares different HR, SV, venous-return, CFI, and PEM equations and different nominal values |
| Use sustained rather than peak HR rise for POTS scenario criteria | Necessary validation correction | The consensus scenario criterion concerns sustained tachycardia; peak HR remains secondary |
| Replace the hardcoded 0.78 functional-capacity normalizer and strengthen parameter bounds | Necessary software/scientific correction | Prevents silent normalization drift and rejects invalid regimes before integration |
| Add CO₂, renal/endocrine volume regulation, nonlinear venous compliance, venous valves, pure delays, afterload, and filling-time dependence | Deferred optional refinements | Each needs additional inputs, evidence, calibration, and validation |

## Revised states

| State | Symbol | Unit | Definition |
|---|---|---|---|
| `arterial_volume` | $V_a$ | mL | Arterial stressed volume |
| `central_venous_volume` | $V_c$ | mL | Central venous stressed volume; remains a reduced-order preload proxy |
| `splanchnic_venous_volume` | $V_s$ | mL | Splanchnic venous stressed volume |
| `lower_limb_venous_volume` | $V_l$ | mL | Lower-limb venous stressed volume |
| `cardiac_sympathetic_state` | $S_c$ | 1 | Cardiac sympathetic effector state |
| `vascular_sympathetic_state` | $S_v$ | 1 | Vascular sympathetic effector state |
| `vagal_state` | $V$ | 1 | Vagal cardiac effector state |
| `exertional_load` | $L$ | 1 | Existing phenomenological load |
| `delayed_stress` | $D$ | 1 | Existing delayed stress |
| `pem_severity` | $PEM$ | 1 | Existing normalized PEM severity |
| `cerebral_flow_index` | $CFI$ | 1 | Normalized proxy, not direct CBF or MCA velocity |

The prior `sympathetic_state` output becomes the arithmetic mean of $S_c$ and $S_v$ solely as a labeled compatibility summary. It is no longer a state or a control input.

## Mathematical specification

### Pressure and regional hemodynamics

$$P_a=V_a/C_a,\quad P_c=V_c/C_c,\quad P_s=V_s/C_s,\quad P_l=V_l/C_l.$$

$$R_{s,a}=R_{s,a0}[1+g_{s,a}(S_v-0.5)],$$
$$R_{l,a}=R_{l,a0}[1+g_{l,a}(S_v-0.5)](1-k_{ex}e),$$
$$R_{l,v}=R_{l,v0}(1+k_{contract}c).$$

Here $e$ is normalized exertion and $c$ is explicit sustained muscle contraction. Exercise vasodilation applies only to the lower-limb arterial path, not automatically to the splanchnic bed. The regional $G_s$ and $G_l$ terms act only on venous return; arterial-side regional hydrostatic columns are not solved. $G_{head}$ corrects only the shared head-level baroreflex/cerebral pressure proxy.

$$Q_{s,a}=\max[0,(P_a-P_s)/R_{s,a}],\qquad Q_{l,a}=\max[0,(P_a-P_l)/R_{l,a}],$$
$$Q_{s,v}=\max[0,(P_s-P_c-G_su)/R_{s,v}],$$
$$Q_{pump}=f_{pump}SV_{pump}\eta_{pump}m\frac{V_l}{V_l+K_{pump}},$$
$$Q_{l,v}=\max[0,(P_l-P_c-G_lu)/R_{l,v}]+Q_{pump}.$$

The pressure-gradient floor is an ideal-valve approximation. Pump flow is added outside that floor so a negative passive gradient cannot cancel an explicitly declared contraction-induced volume transfer; the volume-dependent pump term tends to zero as available lower-limb stressed volume is depleted.

The input $m$ is rhythmic muscle activity, not exertion. Thus supine rest, inactive standing, walking, light rhythmic activity, and sustained contraction are independent protocol conditions. Pump magnitude is a computational assumption; its dependence on contraction frequency, pumped volume, effectiveness, and available venous volume is explicit.

### Volume conservation and cardiac output

$$\dot V_a=Q_{co}-Q_{s,a}-Q_{l,a},$$
$$\dot V_c=Q_{s,v}+Q_{l,v}-Q_{co},$$
$$\dot V_s=Q_{s,a}-Q_{s,v},$$
$$\dot V_l=Q_{l,a}-Q_{l,v}.$$

The four derivatives telescope exactly. Muscle pumping transfers volume from lower-limb to central venous compartments; it does not create blood.

$$SV=SV_{max}\max[0.2,1+k_E(S_c-0.5)]\frac{V_c}{V_c+K_{SV}},$$
$$Q_{co}=HR\,SV/60.$$

Central venous stressed volume remains a deliberately reduced-order Frank–Starling proxy. It is not labeled ventricular end-diastolic volume.

### Autonomic regulation

$$P_{baro}=\max[0,P_a-G_{head}u],\qquad B=\sigma[(P_{set}-P_{baro})/\sigma_P],$$
$$\dot S_c=(B-S_c)/\tau_{S_c},\qquad \dot S_v=(B-S_v)/\tau_{S_v},$$
$$V_{target}=1-B,\qquad \dot V=(1-B-V)/\tau_V,$$
$$HR=\operatorname{clip}[HR_{rest}+g_{S_c}(S_c-0.5)+g_V(0.5-V)+g_{ex}eC,30,220].$$

First-order effector lags approximate distributed neural and neuroeffector dynamics. They are not pure neural transmission delays. The baroreflex senses a head-level pressure proxy rather than an uncorrected heart-level pressure; $G_{head}$ is shared with the cerebral heart–brain correction as a minimal heart-to-head hydrostatic assumption, not a claim that carotid and cerebral heights are identical. Healthy defaults start at $B=S_c=S_v=V=0.5$, so $HR_{rest}$ is the actual supine resting operating point rather than the old intercept.

### Cerebral perfusion proxy

$$CPP=\max[0,P_a-G_{head}u-P_c],\qquad x=CPP/CPP_{ref},$$
$$CFI_{pressure}=\frac{x}{s_{AR}+(1-s_{AR})x},$$
$$CFI_{target}=CFI_{pressure}\max(0,1-\beta u),$$
$$\dot{CFI}=(CFI_{target}-CFI)/\tau_{CBF}.$$

For $0<s_{AR}\leq1$, the pressure curve passes through $(1,1)$, tends to zero as CPP approaches zero, is bounded as CPP rises, and has local normalized slope $s_{AR}$ at the reference point. This is a phenomenological autoregulation curve, not a fitted cerebral vascular resistance. CPP subtracts central venous pressure as the reduced-order downstream/back-pressure proxy; intracranial pressure is not separately modeled. CO₂-dependent vasomotor effects are explicitly absent, so orthostatic hyperventilation cannot be inferred from this index.

## Parameter specification and healthy operating point

New values below are computational operating-point assumptions, not direct human measurements. Existing PEM values are unchanged and remain in the parameter registry.

| Parameter | Value | Unit | Provenance class |
|---|---:|---|---|
| $C_a,C_c,C_s,C_l$ | 1.5, 140, 70, 50 | mL/mmHg | Assumed; regional structure literature-guided |
| $R_{s,a0},R_{l,a0}$ | 2.2040816327 each | mmHg·s/mL | Derived from resting flow split and pressures |
| $R_{s,v0},R_{l,v0}$ | 0.1224489796 each | mmHg·s/mL | Derived from resting return split and pressures |
| $g_{s,a},g_{l,a}$ | 0.8 each | 1 | Assumed/calibrated regional gains |
| $G_s,G_l$ | 4, 8 | mmHg | Phenomenological regional gravity offsets |
| $V_a(0),V_c(0)$ | 150, 700 | mL | Retained assumptions |
| $P_s(0),P_l(0)$ | 10, 10 | mmHg | Constant-pressure regional initialization |
| $V_s(0),V_l(0)$ | 700, 500 | mL | Derived as $P_s(0)C_s$ and $P_l(0)C_l$; healthy sum preserves 2050 mL |
| $SV_{max},K_{SV}$ | 100, 300 | mL/beat, mL | Retained assumptions |
| $HR_{rest}$ | 70 | bpm | Resting operating-point assumption |
| $g_{S_c},g_V$ | 20, 20 | bpm | Split of prior healthy chronotropic gain |
| $\tau_{S_c},\tau_{S_v},\tau_V$ | 6, 10, 1 | s | Human-dynamics-guided computational choices |
| $SV_{pump},f_{pump},\eta_{pump}$ | 20, 1, 1 | mL, 1/s, 1 | Explicit muscle-pump assumptions |
| $K_{pump}$ | 500 | mL | Assumed volume half-saturation |
| $k_{contract}$ | 3 | 1 | Assumed sustained-contraction impediment |
| $CPP_{ref}$ | 95 | mmHg | Derived healthy supine $P_a-P_c$ |
| $G_{head}$ | 20 | mmHg | Assumed full-upright heart-to-head hydrostatic correction shared by baroreflex and CPP |
| $s_{AR}$ | 0.2 | 1 | Assumed normalized residual pressure slope |

At the healthy supine initial condition: $P_a=100$ mmHg, $P_c=5$ mmHg, $P_s=P_l=10$ mmHg, $SV=70$ mL/beat, $HR=70$ bpm, and $Q_{co}=81.6667$ mL/s (4.9 L/min). Each regional arterial and venous path carries 40.8333 mL/s, so the initial state is a steady state before protocol changes. Every phenotype uses $S_c=S_v=V=0.5$ and $L=D=PEM=0$ initially. Regional initial volumes are computed from their reference pressures and compliances, then all four volumes are multiplied by `blood_volume_factor` $f$.

Uniform volume scaling alone does **not** generally preserve the full supine fixed point. With $V_{c0}=700f$ mL, the resting cardiac output is

$$Q_{co0}=\frac{HR_{rest}}{60}SV_{max}\frac{V_{c0}}{V_{c0}+K_{SV}}.$$

For the implemented equal regional flow split, exact resting balances require

$$R_{s,a0}=R_{l,a0}=\frac{2(P_{a0}-10)}{Q_{co0}},\qquad R_{s,v0}=R_{l,v0}=\frac{2(10-P_{c0})}{Q_{co0}},$$

where $P_{a0}=100f$ mmHg and $P_{c0}=5f$ mmHg under the retained nominal volume/compliance assumptions. The pressure setpoint is $P_{a0}$ when a non-default volume factor is used, so the initial baroreflex target remains 0.5. The initial CFI is calculated from the same pressure curve as the dynamic target, with $u=e=0$:

$$CFI_0=\frac{x_0}{s_{AR}+(1-s_{AR})x_0},\qquad x_0=\frac{\max(0,P_{a0}-P_{c0})}{CPP_{ref}}.$$

Thus CFI is one at the healthy reference pressure but is 0.982906 for `pots-hypovolemic` and 0.991736 for `pots-mixed`; it is not hard-coded to one for every phenotype. The hyperadrenergic configuration also applies these flow-balance formulas with its resting HR of 71.5 bpm. All ten configurations are tested for a complete initial RHS maximum absolute component below $10^{-9}$.

## Protocol specification

`ProtocolSegment` gains two normalized inputs, both defaulting to zero:

- `rhythmic_muscle_activity` ($m$): 0 for supine rest/inactive standing; 1 for the reference walking scenario; intermediate values only as declared light-activity scenarios.
- `sustained_muscle_contraction` ($c$): 0 for rest/walking; positive only for an explicit sustained-contraction scenario.

Metabolic exertion $e$ is not used as a proxy for either input. Protocols must declare all three independently.

## Expected computational and disease-configuration consequences

- State vector and persisted traces change from 8 to 11 states; metadata model version advances to 0.2.0.
- Resting healthy outputs remain at their original operating point by construction.
- Upright regional volumes and returns change; previous regression values are not expected to remain numerically identical.
- Chronotropic migration is exact at the supine operating point: $HR_{rest,new}=HR_{base,old}+0.5g_{HR,old}$ and $g_{S_c}+g_V=g_{HR,old}$. The default equal split $g_{S_c}=g_V=g_{HR,old}/2$ is unidentified and must be sensitivity-tested at sympathetic fractions 0, 0.5, and 1 with total gain fixed.

### Post-implementation scenario calibration and retained negative result

The initial migration formula did not make every revised disease scenario meet the predeclared **sustained** final-120-second-upright HR-rise criterion. The following equal cardiac-sympathetic/vagal gains were therefore reviewed as explicit scenario calibrations, not literature measurements or newly identified physiology. Resting HR, stroke volume, cardiac output, and volume conservation were preserved by the fixed-point derivation above.

| Configuration | Each chronotropic gain (bpm) | Total gain (bpm) | Sustained HR rise (bpm) |
|---|---:|---:|---:|
| `pots-neuropathic` | 40 | 80 | 31.63 |
| `pots-hyperadrenergic` | 70 | 140 | 30.38 |
| `pots-hypovolemic` | 60 | 120 | 30.66 |
| `pots-mixed` | 50 | 100 | 32.84 |
| `long-covid-autonomic` | 50 | 100 | 31.14 |

Threshold agreement is calibration overlap, not independent validation. Peak HR rise remains reported separately. The fixed-total chronotropic-split analysis changes peak but not sustained HR rise in the neuropathic scenario, demonstrating why the split remains unidentified.

The healthy early-CO soft-anchor check remains a **negative result**: the early reduction is approximately **5.64%**, below the broad 10–30% literature-derived plausibility band. Caudal stressed-volume accumulation is approximately **336.55 mL**, inside the broad 300–900 mL soft band. Neither band is a hard fitted target. The CO miss is retained as a warning and a structural limitation rather than tuned away or converted into a pass.

### Migration details

- Each old gravity override $G_{old}$ maps to $G_s=G_{old}/2$ and $G_l=G_{old}$; this includes healthy 8→(4,8), hEDS/ME/CFS 9→(4.5,9), POTS 10→(5,10), and Long COVID autonomic 11→(5.5,11).
- Each old vascular gain maps to both regional arterial gains unless regional impairment is explicitly declared. `blood_volume_factor` scales all four initial volumes. The exploratory cerebral multiplier $\beta$ is unchanged and multiplies the new CPP-based target.
- Existing `peripheral_venous_compliance` scenarios migrate to `lower_limb_venous_compliance` using $C_{l,new}=C_{p,old}(50/120)$; hEDS 140 therefore becomes 58.3333 mL/mmHg. Initialization holds supine $P_l=10$ mmHg, so $V_l(0)$ changes with compliance and total stressed volume is intentionally not volume-matched to healthy. This is an exploratory constant-pressure compliance scenario, not an hEDS blood-volume claim, and remains M2.
- No disease-specific conditional branches are added to shared equations. Disease mechanisms enter only through registered parameters and protocol inputs.
- More states and discontinuous max/clip boundaries increase computational cost modestly and require renewed convergence, bounds, and regime-failure testing.

## Validation strategy

1. Preserve the original fixture unchanged in `validation/baseline/stage0/`; generate a reviewed Stage 1 fixture with a scientific change record.
2. Test exact RHS telescoping and integrated conservation for all four volumes, including walking and sustained contraction.
3. Test the supine fixed point for **every phenotype**, plus dimensional consistency, parameter bounds, state bounds, non-finite failures, step-size/tolerance convergence, and flow boundary behavior.
4. Test initial upright venous-return reduction, splanchnic/lower-limb pooling, compensatory HR and sympathetic responses, and supine recovery. Report early CO reduction against a broad 10–30% soft plausibility band and caudal stressed-volume accumulation against a broad 300–900 mL soft band around the heterogeneous 500–800 mL literature synthesis; these are anchors, not fitted patient targets.
5. Compare inactive standing, walking, light activity, and sustained contraction at matched inputs. Verify that pumping transfers rather than creates volume and that rhythmic activity differs from metabolic exertion.
6. Independently perturb cardiac sympathetic, vascular sympathetic, and vagal gains/time constants to demonstrate non-conflation.
7. Verify $CO=HR\cdot SV/60$, steady-state $CO=Q_{s,v}+Q_{l,v}$, pressure–flow consistency, CPP calculation, bounded CFI, and recovery.
8. Rewrite `ocpe/packages/disease-models/models.yaml` to cover all 11 states, regional flows, three autonomic lags, both muscle inputs, CPP/CFI, PEM dynamics, current nominal values, and units; add an executable/declarative consistency test. Re-run every disease scenario, sensitivity grid, strict traceability audit, and OCPE structural validation. Retain failed physiological regimes in reports.
9. Include regional compliances, regional gains, gravity offsets, pump parameters, $s_{AR}$, autonomic lags, and the arbitrary chronotropic split in deterministic sensitivity analyses. These values are not individually identifiable from current evidence.

## Known limitations and rejection criteria

The model remains a beat-averaged research approximation with linear compliances, nonnegative clipped flows, phenomenological gravity offsets, no pulmonary/interstitial compartments, no CO₂ input, no venous-valve state, no pure neural delays, and no patient identification. Regional parameter magnitudes are not direct measurements. A converged conserved solution that produces negative volumes, non-finite outputs, cerebral proxy outside its declared bounds, or an intended healthy/phenotype scenario outside its predeclared physiological range is a failed result, not a successful calibration.
