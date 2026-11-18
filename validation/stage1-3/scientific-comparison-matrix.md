# Stage 1.3 scientific comparison matrix

Deterministic research scenarios only. Numerical threshold passage is not scientific or clinical readiness. The 60° rows are direct experimental-angle comparisons; the 70° rows are explicitly extrapolated model-specific acceptance criteria.

## Isolated and combined healthy mechanism experiments

Every experiment starts from the reproduced Stage 1.2 healthy configuration. CO and SV values are reductions at 120 s upright.

| Experiment | Sustained HR rise (bpm) | End MAP (mmHg) | Caudal pooling (mL) | Residual ΔV (mL) | 60° CO (%) | 60° SV (%) | 70° CO (%) | 70° SV (%) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| stage1_2_reproduced_baseline | 15.467 | 108.846 | 302.962 | 162.152 | 15.801 | 29.215 | 18.732 | 33.439 |
| compliance_redistribution_only | 14.733 | 109.188 | 386.656 | 67.461 | 14.915 | 27.951 | 17.632 | 31.956 |
| common_anatomical_geometry_only | 20.000 | 82.243 | 771.254 | -155.401 | 36.278 | 50.437 | 44.276 | 56.659 |
| baroreflex_weighting_only | 14.816 | 107.424 | 302.719 | 162.036 | 16.230 | 29.070 | 19.133 | 33.259 |
| vascular_compensation_gains_only | 19.115 | 105.382 | 313.407 | 166.391 | 12.406 | 29.550 | 15.670 | 33.759 |
| cardiac_compensation_only | 12.072 | 107.318 | 293.145 | 158.111 | 19.453 | 30.012 | 22.660 | 34.036 |
| dependent_venous_elastance_only | 12.276 | 110.101 | 220.454 | 192.106 | 12.043 | 23.737 | 13.981 | 26.815 |
| cerebral_autoregulation_only | 15.467 | 108.846 | 302.962 | 162.152 | 15.801 | 29.215 | 18.732 | 33.439 |
| audit_linear_proposal_combined | 13.600 | 52.838 | 773.537 | -83.599 | 52.679 | 60.377 | 62.013 | 68.193 |
| stage1_3_nonlinear_combined | 13.298 | 102.253 | 469.395 | -17.931 | 17.081 | 29.677 | 19.816 | 32.617 |

## Preserved phenotype criteria

| Phenotype | Protocol | Sustained HR rise (bpm) | Criterion | Upright-end MAP (mmHg) | End-tilt CFI reduction (%) |
|---|---|---:|---|---:|---:|
| healthy-reference | passive-tilt-30 | 6.592 | n/a | 103.860 | 1.678 |
| healthy-reference | passive-tilt-45 | 9.945 | n/a | 104.727 | 2.647 |
| healthy-reference | passive-tilt-60 | 12.538 | n/a | 103.945 | 3.896 |
| healthy-reference | passive-tilt-70 | 13.298 | n/a | 102.253 | 4.961 |
| healthy-reference | head-up-tilt | 13.298 | n/a | 102.253 | 4.961 |
| healthy-reference | active-standing | 13.531 | n/a | 99.991 | 6.202 |
| healthy-reference | inactive-standing | 13.531 | n/a | 99.991 | 6.202 |
| healthy-reference | tilt-recovery | 13.298 | n/a | 102.253 | 4.961 |
| pots-neuropathic | head-up-tilt | 30.093 | PASS | 107.320 | 3.279 |
| pots-hyperadrenergic | head-up-tilt | 33.430 | PASS | 109.673 | 2.547 |
| pots-hypovolemic | head-up-tilt | 33.690 | PASS | 95.612 | 5.287 |
| pots-mixed | head-up-tilt | 33.396 | PASS | 102.391 | 3.869 |
| long-covid-autonomic | head-up-tilt | 32.368 | PASS | 108.150 | 10.308 |
| long-covid-exertional | head-up-tilt | 13.298 | n/a | 102.253 | 4.961 |
| eds-heds-vascular | head-up-tilt | 23.118 | n/a | 107.146 | 3.334 |
| mecfs-pem | head-up-tilt | 21.726 | n/a | 105.916 | 24.538 |

## Protocol-specific empirical comparisons

| Reference | Protocol | Offset (s) | Metric | Model (%) | Published/reused range (%) | Status | Comparison class |
|---|---|---:|---|---:|---|---|---|
| REF-ZAIDI-2000 | passive-tilt-60 | 120 | cardiac_output_change_pct | -17.081 | -20.0 to -17.0 | WITHIN | direct_experimental_angle_replication |
| REF-ZAIDI-2000 | passive-tilt-60 | 120 | stroke_volume_change_pct | -29.677 | -34.0 to -28.0 | WITHIN | direct_experimental_angle_replication |
| REF-ZAIDI-2000 | passive-tilt-60 | 300 | cardiac_output_change_pct | -17.081 | -20.0 to -17.0 | WITHIN | direct_experimental_angle_replication |
| REF-ZAIDI-2000 | passive-tilt-60 | 300 | stroke_volume_change_pct | -29.677 | -34.0 to -28.0 | WITHIN | direct_experimental_angle_replication |
| REF-ZAIDI-2000 | passive-tilt-70 | 120 | cardiac_output_change_pct | -19.816 | -20.0 to -17.0 | WITHIN | extrapolated_model_specific_acceptance_criterion |
| REF-ZAIDI-2000 | passive-tilt-70 | 120 | stroke_volume_change_pct | -32.617 | -34.0 to -28.0 | WITHIN | extrapolated_model_specific_acceptance_criterion |
| REF-ZAIDI-2000 | passive-tilt-70 | 300 | cardiac_output_change_pct | -19.816 | -20.0 to -17.0 | WITHIN | extrapolated_model_specific_acceptance_criterion |
| REF-ZAIDI-2000 | passive-tilt-70 | 300 | stroke_volume_change_pct | -32.617 | -34.0 to -28.0 | WITHIN | extrapolated_model_specific_acceptance_criterion |

## Interpretation

- Preserved CO/SV comparisons outside their bands: **0**.
- POTS/Long-COVID-autonomic sustained-HR criterion failures: **0**.
- The linear audit proposal and the nonlinear Stage 1.3 combination are separate rows; their numerical differences are retained rather than explaining them away.
- Passing these calibrated scenario checks does not identify patient parameters, validate the quadratic equation form, or establish general-purpose synthetic-data readiness.
