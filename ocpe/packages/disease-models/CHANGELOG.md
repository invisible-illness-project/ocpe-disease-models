# Changelog — ocpe:disease-models

## 0.4.0

- Added the Stage 1.3 one-sided quadratic elastance term for pooled splanchnic
  and lower-limb stressed volumes above their scaled supine references; zero
  recovers the Stage 1.2 linear constitutive law.
- Synchronized the redistributed dependent/residual venous compliances, common
  anatomical hydrostatic heights, cardiac and vascular compensation gains,
  baroreflex weights, cerebral autoregulation slope, and initial volumes.
- Preserved the twelve-state layout and exact five-volume conservation; all
  numerical values remain exploratory research assumptions.

## 0.3.0

- Added the Stage 1.1 twelve-state declaration with a fifth conserved
  other-systemic venous volume and a three-way systemic flow partition.
- Separated aortic and carotid baroreceptor pressures from brain arterial
  pressure; declared their distinct hydrostatic heights and integrated reflex.
- Added explicit tilt-angle, transition-duration and segment end-tidal-CO2
  inputs, plus bounded CO2-dependent cerebral vascular regulation.
- Declared the fixed effective cerebral outflow-pressure approximation without
  treating it as thoracic central venous pressure or resolved intracranial
  pressure.

## 0.2.0

- Replaced the legacy three-compartment declaration with the 11-state shared
  physiology architecture: four stressed-volume compartments, differentiated
  autonomic states, regional muscle-pump and sustained-contraction inputs,
  head-level cerebral perfusion, and the phenomenological PEM cascade.
- Added executable bindings for every state, parameter, protocol input and
  declared output. The model CURIE is now
  `ocpe:disease-models/shared-physiology`; the previous CURIE remains a legacy
  alias for archived observations.

## 0.1.0

- Initial OCPE 0.1 package: cardiovascular quantities (heart rate, mean
  arterial pressure, stroke volume, cardiac output, cerebral flow index,
  compartment blood volumes), latent constructs (metabolic capacity, PEM
  severity, sympathetic activation), disease concepts (ME/CFS, Long COVID,
  POTS, hypermobile EDS, PEM, orthostatic intolerance), measurement methods,
  a sigmoid functional form, relationships, and the declarative
  three-compartment cardiovascular ODE model
  `ocpe:disease-models/three-compartment-cardiovascular`.
