# Sensitivity and assumption-uncertainty report

These deterministic perturbations quantify model-response sensitivity. They are not patient samples, probability distributions, prevalence estimates, or clinical validation.

## Local orthostatic sensitivity

Normalized sensitivity is the centered output change divided by the fractional parameter span and, where defined, the absolute baseline output. Zero-valued outputs have no normalized elasticity.

| Phenotype | Parameter | Output | Low→high normalized sensitivity |
|---|---|---|---:|
| pots-neuropathic | gravity_pressure_offset | orthostatic_heart_rate_rise_bpm | 1.319 |
| pots-neuropathic | gravity_pressure_offset | mean_arterial_pressure_final_mmHg | -0.6566 |
| pots-neuropathic | gravity_pressure_offset | pem_peak | 0 |
| pots-neuropathic | gravity_pressure_offset | functional_capacity_final | 0 |
| pots-neuropathic | venous_return_resistance | orthostatic_heart_rate_rise_bpm | 0.4304 |
| pots-neuropathic | venous_return_resistance | mean_arterial_pressure_final_mmHg | -0.2372 |
| pots-neuropathic | venous_return_resistance | pem_peak | 0 |
| pots-neuropathic | venous_return_resistance | functional_capacity_final | 0 |
| pots-neuropathic | resistance_sympathetic_gain | orthostatic_heart_rate_rise_bpm | -0.1558 |
| pots-neuropathic | resistance_sympathetic_gain | mean_arterial_pressure_final_mmHg | 0.06538 |
| pots-neuropathic | resistance_sympathetic_gain | pem_peak | 0 |
| pots-neuropathic | resistance_sympathetic_gain | functional_capacity_final | 0 |
| pots-neuropathic | blood_volume_factor | orthostatic_heart_rate_rise_bpm | -1.533 |
| pots-neuropathic | blood_volume_factor | mean_arterial_pressure_final_mmHg | 1.2 |
| pots-neuropathic | blood_volume_factor | pem_peak | 0 |
| pots-neuropathic | blood_volume_factor | functional_capacity_final | 0 |
| pots-neuropathic | heart_rate_sympathetic_gain | orthostatic_heart_rate_rise_bpm | 1.25 |
| pots-neuropathic | heart_rate_sympathetic_gain | mean_arterial_pressure_final_mmHg | 0.1404 |
| pots-neuropathic | heart_rate_sympathetic_gain | pem_peak | 0 |
| pots-neuropathic | heart_rate_sympathetic_gain | functional_capacity_final | 0 |
| eds-heds-vascular | peripheral_venous_compliance | orthostatic_heart_rate_rise_bpm | 1.084 |
| eds-heds-vascular | peripheral_venous_compliance | mean_arterial_pressure_final_mmHg | -1.245 |
| eds-heds-vascular | peripheral_venous_compliance | pem_peak | 0 |
| eds-heds-vascular | peripheral_venous_compliance | functional_capacity_final | 0 |

## Deterministic assumption grids

| Phenotype | Overrides | HR rise (bpm) | Final MAP (mmHg) | PEM peak | Final capacity |
|---|---|---:|---:|---:|---:|
| eds-heds-vascular | peripheral_venous_compliance=120.0, gravity_pressure_offset=7.0 | 10.03 | 98.61 | 0 | 1 |
| eds-heds-vascular | peripheral_venous_compliance=120.0, gravity_pressure_offset=9.0 | 17.85 | 97.26 | 0 | 1 |
| eds-heds-vascular | peripheral_venous_compliance=120.0, gravity_pressure_offset=11.0 | 29.27 | 91.21 | 0 | 1 |
| eds-heds-vascular | peripheral_venous_compliance=140.0, gravity_pressure_offset=7.0 | 17.51 | 96.97 | 0 | 1 |
| eds-heds-vascular | peripheral_venous_compliance=140.0, gravity_pressure_offset=9.0 | 28.16 | 88.22 | 0 | 1 |
| eds-heds-vascular | peripheral_venous_compliance=140.0, gravity_pressure_offset=11.0 | 28.33 | 63.09 | 0 | 1 |
| eds-heds-vascular | peripheral_venous_compliance=160.0, gravity_pressure_offset=7.0 | 25.87 | 91.11 | 0 | 1 |
| eds-heds-vascular | peripheral_venous_compliance=160.0, gravity_pressure_offset=9.0 | 26.57 | 65.87 | 0 | 1 |
| eds-heds-vascular | peripheral_venous_compliance=160.0, gravity_pressure_offset=11.0 | 26.57 | 37.84 | 0 | 1 |
| mecfs-pem | delayed_stress_time_constant=14400.0, pem_onset_time_constant=43200.0 | n/a | 100 | 0.285 | 0.7953 |
| mecfs-pem | delayed_stress_time_constant=14400.0, pem_onset_time_constant=86400.0 | n/a | 100 | 0.172 | 0.7992 |
| mecfs-pem | delayed_stress_time_constant=14400.0, pem_onset_time_constant=172800.0 | n/a | 100 | 0.09773 | 0.8021 |
| mecfs-pem | delayed_stress_time_constant=21600.0, pem_onset_time_constant=43200.0 | n/a | 100 | 0.2508 | 0.7952 |
| mecfs-pem | delayed_stress_time_constant=21600.0, pem_onset_time_constant=86400.0 | n/a | 100 | 0.1571 | 0.7988 |
| mecfs-pem | delayed_stress_time_constant=21600.0, pem_onset_time_constant=172800.0 | n/a | 100 | 0.09197 | 0.8015 |
| mecfs-pem | delayed_stress_time_constant=43200.0, pem_onset_time_constant=43200.0 | n/a | 100 | 0.1795 | 0.795 |
| mecfs-pem | delayed_stress_time_constant=43200.0, pem_onset_time_constant=86400.0 | n/a | 100 | 0.1207 | 0.7977 |
| mecfs-pem | delayed_stress_time_constant=43200.0, pem_onset_time_constant=172800.0 | n/a | 100 | 0.07508 | 0.8002 |

## Range summary and failed physiological regimes

### eds-heds-vascular

- orthostatic_heart_rate_rise_bpm: 10.03 to 29.27
- mean_arterial_pressure_final_mmHg: 37.84 to 98.61
- pem_peak: 0 to 0
- functional_capacity_final: 1 to 1
- **Unacceptable MAP regimes retained:** 3 scenario(s) end below 70 mmHg. These combinations fail the physiological demonstration criterion and must not be presented as valid phenotypes.

### mecfs-pem

- mean_arterial_pressure_final_mmHg: 100 to 100
- pem_peak: 0.07508 to 0.285
- functional_capacity_final: 0.795 to 0.8021
- No scenario in this grid ends below the 70 mmHg MAP screening threshold.

## Interpretation limits

- hEDS peripheral venous compliance includes the healthy reference value and both exploratory increases; it is not a measured hEDS coefficient.
- ME/CFS delay and onset constants are phenomenological and are not probability distributions over patients.
- Configuration hashes and solver settings are retained in JSON; no random seed is used because no stochastic sampling occurs.
- Sensitivity does not validate equation structure or clinical utility.
