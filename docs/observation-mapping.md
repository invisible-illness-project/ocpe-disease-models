# OCPE observation mapping

## Boundary

Simulation states and derived outputs are not automatically clinical observations. The mapping layer performs three explicit operations:

1. select a declared simulator output;
2. resolve its OCPE quantity and compatible UCUM unit;
3. construct and strictly validate an observation record with subject, time, value, unit, method, and evidence provenance.

No waveform or wearable dataset is generated.

## Native names and units

| Simulator output | OCPE interpretation | Unit/scale |
|---|---|---|
| `heart_rate` | Heart rate | beats/min |
| `mean_arterial_pressure` | Mean arterial pressure | mmHg |
| `stroke_volume` | Stroke volume | mL/beat |
| `cardiac_output_l_min` | Cardiac output | L/min |
| `cerebral_flow_index` | Reduced-order normalized cerebral-flow index | normalized index |
| `metabolic_capacity` | Normalized metabolic-capacity construct | normalized fraction |
| `pem_severity` | Phenomenological PEM severity | normalized 0–1 |

The internal derived `cardiac_output` is mL/s, but persisted simulator output uses `cardiac_output_l_min`. `SIMULATOR_OUTPUT_ALIASES` maps that native name to the OCPE cardiac-output specification without another conversion. This prevents both a missing-key failure and an accidental ×60/1000 double conversion.

## Validation

`tests/integration/test_simulation_observation_mapping.py` executes a real short healthy simulation, maps seven final-time values, and requires strict OCPE observation validation with zero errors and warnings. Unit tests independently check alias targets, units, required provenance, and record construction.

Each demonstration output directory contains `observations.json` with final-time records. The full compact `trace.npz` remains the numerical validation artifact; observation JSON is not a longitudinal clinical record.

## Unsupported mappings

ECG, PPG, HRV, respiratory rate, skin temperature, electrodermal activity, accelerometry, symptom scores, blood biomarkers, and volumetric cerebral blood flow have no validated mapping here. Normalized cerebral, metabolic, extraction, and PEM constructs must not be relabeled as direct clinical measurements. Future sensor work requires its own observation equations, noise/error model, sampling specification, evidence, and independent validation.
