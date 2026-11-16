# Changelog — ocpe:disease-models

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
