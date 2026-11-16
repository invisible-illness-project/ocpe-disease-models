# Stage 1 literature and evidence-to-mechanism matrix

## Review method and interpretation

The focused review prioritized human controlled physiology, systematic or authoritative reviews, and established cardiovascular models. Animal and classical experimental work is identified separately. Evidence grades follow the repository policy: E1 hypothesis/indirect, E2 small or selected human evidence, E3 replicated/convergent human physiology, E4 systematic review/consensus, and E5 independently replicated high-quality evidence for the specific claim. A model citation supports structure or direction; it does not turn a nominal parameter into a measurement.

The review was deliberately bounded to shared cardiovascular, autonomic, vascular, orthostatic, muscle-pump, and cerebral mechanisms. It did not begin disease-specific Stage 2 mechanism development.

## Evidence-to-mechanism matrix

| Proposed mechanism | Best evidence | Evidence classification | Modeling decision | What the evidence does **not** establish |
|---|---|---|---|---|
| Pressure-driven venous return from a filling-pressure gradient | Guyton 1955; Magder 2016; Persichini 2022 | Established physiological framework; human MSFP estimates E3 | Retain reduced-order pressure-gradient returns | Classical dog values are not direct human regional parameters |
| Stressed and unstressed venous volume | Magder 2016; Rothe 1983; Gelman 2008 | Established concept; quantitative regional distribution uncertain | Keep explicit stressed volumes; defer dynamic unstressed reservoir | Does not justify invented regional unstressed volumes or venomotor gains |
| Separate splanchnic venous compartment | Rowell 1972; Taneja 2007; Stewart 2004; Tani 2000 | Strong controlled human evidence E3 | Add splanchnic volume, arterial inflow, venous return, and gravity offset | Does not supply absolute awake-human compliance/resistance values |
| Separate lower-limb venous compartment | Smith 1994; Heldt 2002; van Heusden 2006 | Established orthostatic redistribution plus human-calibrated models E3 | Add lower-limb volume and return path | Does not validate a linear compliance or constant gravity offset |
| Upright tilt differs from LBNP | Taneja 2007 | Small controlled human study E2, mechanistically important | Do not use LBNP and standing interchangeably in validation | Small impedance-based cohort; no absolute volumes |
| Gravitational pooling develops over time | Smith 1994; van Heusden 2006 | Human synthesis and computational validation E3 | Conservative compartment dynamics rather than instantaneous volume reassignment | No unique pooling time constant for every posture/person |
| Rhythmic skeletal-muscle pump augments venous return | Rowell 1986/1993; Heldt 2002 | Established human physiology E3 | Explicit pumped flow from lower-limb to central compartment | Does not identify a universal pump flow or effectiveness |
| Muscle pump is not the sole exercise CO mechanism | González-Alonso 2008 and associated debate | Controlled human evidence, contested/generalizability-limited E2 | Keep arterial vasodilation independent from pump input; no obligatory pump multiplier | One-legged exercise cannot be generalized to every upright activity |
| Sustained contraction impedes muscle venous flow | Classical human exercise physiology; Rowell synthesis | Established direction E3; magnitude uncertain | Increase lower-limb venous resistance with explicit sustained-contraction input | No precise universal resistance gain |
| Vagal cardiac control is faster than sympathetic control | Cohen & Taylor 2002; deBoer 1987; Cevese 2001 | Convergent human physiology E3 | Separate vagal state with shorter lag | Does not identify one constant across all people and conditions |
| Cardiac and vascular sympathetic pathways are distinguishable | Fagius 1985; Cevese 2001; Heldt 2002 | Human neural evidence and convergent models E3 | Separate cardiac and vascular sympathetic effector states | MSNA is not a direct measurement of cardiac or splanchnic outflow |
| Baroreflex delays affect stability | deBoer 1987; Hammer & Saul 2005; Olufsen 2006 | Human identification plus computational theory E3 | Use pathway-specific first-order lags; defer pure-delay DDE | Does not validate arbitrary delay/gain combinations |
| Regional resistance control matters during orthostasis | Rowell 1972; Taneja 2007; Heldt 2002 | Strong human and modeling evidence E3 | Separate splanchnic and lower-limb arterial resistances/gains | Does not justify one neuropathic gain for every vascular bed |
| Preload influences SV; CO equals HR times SV | Established human circulatory physiology; Heldt 2002; Olufsen 2005 | Established E3 | Retain reduced-order preload curve and exact CO identity | Central venous stressed volume is not ventricular end-diastolic volume |
| Brain-level CPP differs from brachial/systemic MAP | Levine 1994; Willie 2014 | Strong human evidence E3 | Subtract orthostatic hydrostatic offset and venous back pressure | Does not supply intracranial pressure or patient-specific CPP |
| Dynamic cerebral autoregulation buffers pressure changes | Aaslid 1989; Novak 1998; Claassen 2016 | Human physiology and methodological consensus E3–E4 | Bounded dynamic normalized pressure-flow proxy | Does not validate the selected curve or CFI as volumetric CBF |
| CO₂ materially regulates cerebral flow | Willie 2012/2014; Lewis 2014; Aaslid 1989 | Controlled human evidence E3 | Declare omission; do not hide CO₂ effects in an “autoregulation” gain | No CO₂ input means no hypocapnia mechanism can be inferred |
| Blood-volume regulation over longer horizons | Magder 2016; Smith 1994; existing POTS volume literature | Established direction, multi-timescale complexity | Keep fixed total stressed volume for short orthostatic protocols | No renal, endocrine, plasma-refill, or interstitial-fluid prediction |

## Key sources and quantitative constraints

### Human orthostatic and vascular physiology

1. **Taneja I, Moran C, Medow MS, Glover JL, Montgomery LD, Stewart JM (2007).** “Differential effects of lower body negative pressure and upright tilt on splanchnic blood volume.” *American Journal of Physiology-Heart and Circulatory Physiology* 292:H1420–H1426. DOI: [10.1152/ajpheart.01096.2006](https://doi.org/10.1152/ajpheart.01096.2006). In small controlled human cohorts, splanchnic segmental volume increased during 70° tilt but decreased during LBNP; impedance measurements are relative, not absolute regional blood volumes.
2. **Stewart JM, Montgomery LD (2004).** “Regional blood volume and peripheral blood flow in postural tachycardia syndrome.” *American Journal of Physiology-Heart and Circulatory Physiology* 287:H1319–H1327. PMCID: [PMC4515760](https://pmc.ncbi.nlm.nih.gov/articles/PMC4515760/). Adolescent POTS and control tilt data support regional rather than uniform pooling; adolescent values are not healthy-adult parameter defaults.
3. **Smith JJ, Porth CM, Erickson M (1994).** “Hemodynamic response to the upright posture.” *Journal of Clinical Pharmacology* 34:375–386. PMID: [8089249](https://pubmed.ncbi.nlm.nih.gov/8089249/). The review synthesizes roughly 500–800 mL redistribution below the diaphragm and an approximately 20% early CO reduction; protocol and population differences preclude using these as exact model targets.
4. **Rowell LB, Detry JMR, Blackmon JR, Wyss C (1972).** “Importance of the splanchnic vascular bed in human blood pressure regulation.” *Journal of Applied Physiology* 32:213–220. DOI: [10.1152/jappl.1972.32.2.213](https://doi.org/10.1152/jappl.1972.32.2.213). Controlled pharmacologic interventions support splanchnic vasoconstriction in pressure defense; small invasive cohort.
5. **Tani H et al. (2000).** “Splanchnic-mesenteric capacitance bed in the postural tachycardia syndrome (POTS).” *Autonomic Neuroscience* 86:107–113. PMID: [11269915](https://pubmed.ncbi.nlm.nih.gov/11269915/). Supports exaggerated splanchnic pooling in a POTS subgroup, not a universal disease value.

### Venous return and capacitance

6. **Persichini R et al. (2022).** “Venous return and mean systemic filling pressure: physiology and clinical applications.” *Critical Care* 26:150. DOI: [10.1186/s13054-022-04024-x](https://doi.org/10.1186/s13054-022-04024-x). Human bedside estimates support the importance of small filling-pressure gradients; estimates remain model-dependent.
7. **Magder S (2016).** “Volume and its relationship to cardiac output and venous return.” *Critical Care* 20:271. DOI: [10.1186/s13054-016-1438-7](https://doi.org/10.1186/s13054-016-1438-7). Narrative synthesis of stressed/unstressed volume; human fractions are inferred. The 2017 erratum must accompany use.
8. **Rothe CF (1983).** “Reflex control of veins and vascular capacitance.” *Physiological Reviews* 63:1281–1342. PMID: [6361810](https://pubmed.ncbi.nlm.nih.gov/6361810/). Authoritative venous capacitance review; much quantitative venomotor evidence is animal-derived and is not promoted to human parameter truth.
9. **Guyton AC, Lindsey AW, Kaufmann BN (1955).** “Effect of mean circulatory filling pressure and other peripheral circulatory factors on cardiac output.” *American Journal of Physiology* 180:463–468. DOI: [10.1152/ajplegacy.1955.180.3.463](https://doi.org/10.1152/ajplegacy.1955.180.3.463). Classical animal/right-heart-bypass origin of the analytical framework; explicitly indirect for human parameter values.

### Muscle pump and exercise

10. **González-Alonso J et al. (2008).** “Haemodynamic responses to exercise, ATP infusion and thigh compression in humans: insight into the role of muscle mechanisms on cardiovascular function.” *Journal of Physiology* 586:2405–2417. DOI: [10.1113/jphysiol.2008.152058](https://doi.org/10.1113/jphysiol.2008.152058). Shows that small-muscle-mass exercise CO can rise without obligatory muscle-pump action; prevents an oversimplified pump-only exercise model.
11. **Rowell LB (1986).** *Human Circulation: Regulation During Physical Stress*. Oxford University Press. ISBN 0-19-504075-4; and **Rowell LB (1993).** *Human Cardiovascular Control*. Oxford University Press. Classical human syntheses support rhythmic pump and regional vascular distinctions. Quantitative values require consultation of the underlying experiments rather than blind transfer.

### Autonomic control

12. **Cohen MA, Taylor JA (2002).** “Short-term cardiovascular oscillations in man: measuring and modelling the physiologies.” *Journal of Physiology* 542:669–683. DOI: [10.1113/jphysiol.2002.017483](https://doi.org/10.1113/jphysiol.2002.017483). Supports faster vagal than sympathetic HR effects and separate transfer elements.
13. **Cevese A et al. (2001).** “Baroreflex and oscillation of heart period at 0.1 Hz studied by α-blockade and cross-spectral analysis in healthy humans.” *Journal of Physiology* 531:235–244. PMCID: [PMC2278442](https://pmc.ncbi.nlm.nih.gov/articles/PMC2278442/). Pharmacologic human evidence distinguishes vascular sympathetic and vagal cardiac contributions.
14. **deBoer RW, Karemaker JM, Strackee J (1987).** “Hemodynamic fluctuations and baroreflex sensitivity in humans: a beat-to-beat model.” *American Journal of Physiology* 253:H680–H689. DOI: [10.1152/ajpheart.1987.253.3.H680](https://doi.org/10.1152/ajpheart.1987.253.3.H680). Supports delayed baroreflex coupling; linear open-loop identification limits parameter transfer.
15. **Fagius J et al. (1985).** “Sympathetic outflow in man after anaesthesia of the glossopharyngeal and vagus nerves.” *Brain* 108:423–438. DOI: [10.1093/brain/108.2.423](https://doi.org/10.1093/brain/108.2.423). Human microneurography supports baroreflex control of vascular sympathetic outflow; MSNA does not measure every regional bed.

### Cerebral circulation

16. **Levine BD et al. (1994).** “Cerebral versus systemic hemodynamics during graded orthostatic stress in humans.” *Circulation* 90:298–306. DOI: [10.1161/01.CIR.90.1.298](https://doi.org/10.1161/01.CIR.90.1.298). Supports distinction between systemic pressure and cerebral hemodynamics; TCD velocity is not volumetric flow.
17. **Aaslid R et al. (1989).** “Cerebral autoregulation dynamics in humans.” *Stroke* 20:45–52. DOI: [10.1161/01.STR.20.1.45](https://doi.org/10.1161/01.STR.20.1.45). Thigh-cuff steps establish dynamic autoregulation over seconds and CO₂ dependence; the stimulus and TCD surrogate limit direct calibration.
18. **Claassen JAHR et al. (2016).** “Transfer function analysis of dynamic cerebral autoregulation: a white paper from the International Cerebral Autoregulation Research Network.” *Journal of Cerebral Blood Flow & Metabolism* 36:665–680. DOI: [10.1177/0271678X15626425](https://doi.org/10.1177/0271678X15626425). Consensus methods; not a new physiological parameter source.
19. **Willie CK, Tzeng YC, Fisher JA, Ainslie PN (2014).** “Integrative regulation of human brain blood flow.” *Journal of Physiology* 592:841–859. DOI: [10.1113/jphysiol.2013.268953](https://doi.org/10.1113/jphysiol.2013.268953). Integrates CPP, blood gases, autonomic and CO influences; explains why a pressure-only CFI is incomplete.
20. **Lewis NCS et al. (2014).** “Impact of hypocapnia and cerebral perfusion on orthostatic tolerance.” *Journal of Physiology* 592:5203–5219. DOI: [10.1113/jphysiol.2014.280586](https://doi.org/10.1113/jphysiol.2014.280586). Controlled human evidence that hypocapnia amplifies cerebral hypoperfusion while tolerance can be buffered by extraction; do not equate lower CFI with syncope.

### Established computational models

21. **Heldt T, Shim EB, Kamm RD, Mark RG (2002).** “Computational modeling of cardiovascular response to orthostatic stress.” *Journal of Applied Physiology* 92:1239–1254. DOI: [10.1152/japplphysiol.00241.2001](https://doi.org/10.1152/japplphysiol.00241.2001). Population-calibrated regional compartments and distinct effector pathways. Its values are model assumptions, not direct measurements for this model.
22. **Olufsen MS et al. (2005).** “Blood pressure and blood flow variation during postural change from sitting to standing: model development and validation.” *Journal of Applied Physiology* 99:1523–1537. DOI: [10.1152/japplphysiol.00177.2005](https://doi.org/10.1152/japplphysiol.00177.2005). Coupled gravity, autonomic and cerebral regulation; detailed calibration relied on limited subjects.
23. **van Heusden K et al. (2006).** “Mathematical modeling of gravitational effects on the circulation: importance of the time course of venous pooling and blood volume changes in the lungs.” *American Journal of Physiology-Heart and Circulatory Physiology* 291:H2152–H2165. DOI: [10.1152/ajpheart.01268.2004](https://doi.org/10.1152/ajpheart.01268.2004). Supports explicit pooling time course; lung-volume dynamics remain outside this revision.

## Negative and constraining findings retained

- LBNP and upright tilt are not interchangeable splanchnic stressors.
- Muscle pump is not obligatory for every exercise-associated CO increase.
- Regional impedance and TCD measures are surrogates, not absolute regional blood volume or volumetric brain flow.
- Human evidence does not identify unique regional compliances, pump effectiveness, autonomic gains, or autoregulation-curve parameters for this reduced-order model.
- The absence of a CO₂ state prevents attribution of modeled CFI changes to hyperventilation.
- Adding compartments does not create independent validation. Existing disease calibrations and group-level anchors remain overlapping evidence.

## Evidence gaps requiring Stage 2 caution

Stage 2 disease configurations may perturb shared regional compliances, regional resistance gains, autonomic pathway gains/lags, pump effectiveness, initial stressed volume, or exploratory cerebral impairment only with phenotype-specific evidence and sensitivity analysis. Disease labels must not be hard-coded into shared equations. No disease-specific CO₂, venomotor, inflammatory, or connective-tissue mechanism should be inferred from the shared structure alone.
