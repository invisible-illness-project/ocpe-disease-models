# Stage 1.1 time-resolved scientific comparison matrix

Deterministic research scenarios only. Published group ranges are heterogeneous plausibility anchors, not fitted patient data or clinical validation. No parameter was adjusted to manufacture agreement.

## Preserved criterion outcomes

| Phenotype | Protocol | Sustained HR rise (bpm) | Criterion | Upright-end MAP (mmHg) | End-tilt CFI reduction (%) |
|---|---|---:|---|---:|---:|
| healthy-reference | passive-tilt-30 | 3.626 | n/a | 106.163 | 0.819 |
| healthy-reference | passive-tilt-45 | 5.417 | n/a | 108.642 | 1.192 |
| healthy-reference | passive-tilt-60 | 6.954 | n/a | 110.493 | 1.497 |
| healthy-reference | passive-tilt-70 | 7.723 | n/a | 111.332 | 1.645 |
| healthy-reference | head-up-tilt | 7.723 | n/a | 111.332 | 1.645 |
| healthy-reference | active-standing | 8.383 | n/a | 112.006 | 1.771 |
| healthy-reference | inactive-standing | 8.383 | n/a | 112.006 | 1.771 |
| healthy-reference | tilt-recovery | 7.723 | n/a | 111.332 | 1.645 |
| pots-neuropathic | head-up-tilt | 17.428 | FAIL | 111.093 | 1.702 |
| pots-hyperadrenergic | head-up-tilt | 19.659 | FAIL | 112.095 | 1.464 |
| pots-hypovolemic | head-up-tilt | 19.399 | FAIL | 100.937 | 2.628 |
| pots-mixed | head-up-tilt | 19.216 | FAIL | 106.530 | 1.991 |
| long-covid-autonomic | head-up-tilt | 18.931 | FAIL | 111.367 | 9.031 |
| long-covid-exertional | head-up-tilt | 7.723 | n/a | 111.332 | 1.645 |
| eds-heds-vascular | head-up-tilt | 12.448 | n/a | 111.195 | 1.678 |
| mecfs-pem | head-up-tilt | 9.964 | n/a | 111.273 | 22.913 |

## Predeclared healthy window summaries

Baseline is [0, t0−2 s]; early minima use [t0, t0+30 s]; peak HR uses [t0, t0+300 s], clipped to the continuous upright bout.

| Protocol | Early minimum CO change (%) | Early minimum SV change (%) | Peak HR rise (bpm) | Sustained HR rise (bpm) |
|---|---:|---:|---:|---:|
| passive-tilt-30 | -0.000 | -4.157 | 3.653 | 3.626 |
| passive-tilt-45 | 0.000 | -6.497 | 5.435 | 5.417 |
| passive-tilt-60 | 0.000 | -8.749 | 6.976 | 6.954 |
| passive-tilt-70 | -0.346 | -10.069 | 7.748 | 7.723 |
| head-up-tilt | -0.346 | -10.069 | 7.748 | 7.723 |
| active-standing | -3.114 | -13.513 | 9.697 | 8.383 |
| inactive-standing | -3.128 | -13.522 | 9.001 | 8.383 |
| tilt-recovery | -0.346 | -10.069 | 7.748 | 7.723 |

## Time-resolved healthy responses

Offsets are measured from the upright segment start; posture during the declared transition is explicitly reported in JSON.

| Protocol | Offset (s) | HR rise (bpm) | CO change (%) | SV change (%) | MAP (mmHg) | CFI |
|---|---:|---:|---:|---:|---:|---:|
| passive-tilt-30 | 0 | -0.000 | -0.000 | -0.000 | 100.000 | 1.00000 |
| passive-tilt-30 | 10 | 1.259 | 1.103 | -0.684 | 102.063 | 0.99827 |
| passive-tilt-30 | 30 | 3.653 | 0.844 | -4.157 | 106.070 | 0.99294 |
| passive-tilt-30 | 60 | 3.631 | -0.716 | -5.611 | 106.162 | 0.99181 |
| passive-tilt-30 | 120 | 3.626 | -0.759 | -5.646 | 106.163 | 0.99181 |
| passive-tilt-30 | 300 | 3.626 | -0.759 | -5.646 | 106.163 | 0.99181 |
| passive-tilt-45 | 0 | 0.000 | 0.000 | 0.000 | 100.000 | 1.00000 |
| passive-tilt-45 | 10 | 1.885 | 1.613 | -1.053 | 103.072 | 0.99740 |
| passive-tilt-45 | 30 | 5.378 | 0.686 | -6.497 | 108.522 | 0.98964 |
| passive-tilt-45 | 60 | 5.425 | -1.560 | -8.641 | 108.640 | 0.98808 |
| passive-tilt-45 | 120 | 5.417 | -1.624 | -8.691 | 108.642 | 0.98808 |
| passive-tilt-45 | 300 | 5.417 | -1.624 | -8.691 | 108.642 | 0.98808 |
| passive-tilt-60 | 0 | 0.000 | 0.000 | 0.000 | 100.000 | 1.00000 |
| passive-tilt-60 | 10 | 2.502 | 2.085 | -1.438 | 104.054 | 0.99653 |
| passive-tilt-60 | 30 | 6.833 | 0.158 | -8.749 | 110.372 | 0.98678 |
| passive-tilt-60 | 60 | 6.965 | -2.494 | -11.317 | 110.492 | 0.98503 |
| passive-tilt-60 | 120 | 6.954 | -2.571 | -11.375 | 110.493 | 0.98503 |
| passive-tilt-60 | 300 | 6.954 | -2.570 | -11.375 | 110.493 | 0.98503 |
| passive-tilt-70 | 0 | 0.000 | 0.000 | 0.000 | 100.000 | 1.00000 |
| passive-tilt-70 | 10 | 2.906 | 2.376 | -1.704 | 104.692 | 0.99596 |
| passive-tilt-70 | 30 | 7.569 | -0.346 | -10.069 | 111.224 | 0.98524 |
| passive-tilt-70 | 60 | 7.735 | -3.027 | -12.676 | 111.330 | 0.98354 |
| passive-tilt-70 | 120 | 7.723 | -3.105 | -12.733 | 111.332 | 0.98355 |
| passive-tilt-70 | 300 | 7.723 | -3.105 | -12.733 | 111.332 | 0.98355 |
| head-up-tilt | 0 | 0.000 | 0.000 | 0.000 | 100.000 | 1.00000 |
| head-up-tilt | 10 | 2.906 | 2.376 | -1.704 | 104.692 | 0.99596 |
| head-up-tilt | 30 | 7.569 | -0.346 | -10.069 | 111.224 | 0.98524 |
| head-up-tilt | 60 | 7.735 | -3.027 | -12.676 | 111.330 | 0.98354 |
| head-up-tilt | 120 | 7.723 | -3.105 | -12.733 | 111.332 | 0.98355 |
| head-up-tilt | 300 | 7.723 | -3.105 | -12.733 | 111.332 | 0.98355 |
| active-standing | 0 | 0.000 | 0.000 | 0.000 | 100.000 | 1.00000 |
| active-standing | 10 | 7.708 | 1.130 | -8.902 | 111.946 | 0.98489 |
| active-standing | 30 | 8.417 | -3.114 | -13.513 | 111.996 | 0.98230 |
| active-standing | 60 | 8.388 | -3.581 | -13.899 | 112.005 | 0.98229 |
| active-standing | 120 | 8.383 | -3.592 | -13.903 | 112.006 | 0.98229 |
| active-standing | 300 | 8.383 | -3.592 | -13.903 | 112.006 | 0.98229 |
| inactive-standing | 0 | -0.000 | -0.001 | -0.000 | 100.000 | 1.00000 |
| inactive-standing | 10 | 7.833 | 0.943 | -9.216 | 111.936 | 0.98481 |
| inactive-standing | 30 | 8.414 | -3.128 | -13.522 | 111.997 | 0.98230 |
| inactive-standing | 60 | 8.387 | -3.581 | -13.897 | 112.005 | 0.98229 |
| inactive-standing | 120 | 8.383 | -3.592 | -13.903 | 112.006 | 0.98229 |
| inactive-standing | 300 | 8.383 | -3.592 | -13.903 | 112.006 | 0.98229 |
| tilt-recovery | 0 | 0.000 | 0.000 | 0.000 | 100.000 | 1.00000 |
| tilt-recovery | 10 | 2.906 | 2.376 | -1.704 | 104.692 | 0.99596 |
| tilt-recovery | 30 | 7.569 | -0.346 | -10.069 | 111.224 | 0.98524 |
| tilt-recovery | 60 | 7.735 | -3.027 | -12.676 | 111.330 | 0.98354 |
| tilt-recovery | 120 | 7.723 | -3.105 | -12.733 | 111.332 | 0.98355 |
| tilt-recovery | 300 | 7.723 | -3.105 | -12.733 | 111.332 | 0.98355 |

## Tilt-back recovery

Offsets are measured from the start of the supine recovery segment; the declared 30-second return transition is included.

| Protocol | Offset (s) | HR rise vs supine baseline (bpm) | CO change (%) | SV change (%) | CFI | Tilt (deg) |
|---|---:|---:|---:|---:|---:|---:|
| tilt-recovery | 0 | 7.723 | -3.105 | -12.733 | 0.98355 | 70.00 |
| tilt-recovery | 10 | 5.584 | -3.856 | -10.959 | 0.98497 | 46.67 |
| tilt-recovery | 30 | -0.382 | -3.458 | -2.927 | 0.99384 | 0.00 |
| tilt-recovery | 60 | -0.011 | -0.083 | -0.067 | 0.99951 | 0.00 |
| tilt-recovery | 120 | -0.000 | 0.000 | 0.000 | 1.00000 | 0.00 |
| tilt-recovery | 300 | -0.000 | 0.000 | 0.000 | 1.00000 | 0.00 |

## Protocol-specific empirical comparisons

| Reference | Protocol | Offset (s) | Metric | Model (%) | Published range (%) | Status |
|---|---|---:|---|---:|---|---|
| REF-ZAIDI-2000 | passive-tilt-60 | 120 | cardiac_output_change_pct | -2.571 | -20.0 to -17.0 | MISS |
| REF-ZAIDI-2000 | passive-tilt-60 | 120 | stroke_volume_change_pct | -11.375 | -34.0 to -28.0 | MISS |
| REF-ZAIDI-2000 | passive-tilt-60 | 300 | cardiac_output_change_pct | -2.570 | -20.0 to -17.0 | MISS |
| REF-ZAIDI-2000 | passive-tilt-60 | 300 | stroke_volume_change_pct | -11.375 | -34.0 to -28.0 | MISS |
| REF-ZAIDI-2000 | passive-tilt-70 | 120 | cardiac_output_change_pct | -3.105 | -20.0 to -17.0 | MISS |
| REF-ZAIDI-2000 | passive-tilt-70 | 120 | stroke_volume_change_pct | -12.733 | -34.0 to -28.0 | MISS |
| REF-ZAIDI-2000 | passive-tilt-70 | 300 | cardiac_output_change_pct | -3.105 | -20.0 to -17.0 | MISS |
| REF-ZAIDI-2000 | passive-tilt-70 | 300 | stroke_volume_change_pct | -12.733 | -34.0 to -28.0 | MISS |

## Cerebral isolation experiments

| Protocol | Final brain arterial pressure (mmHg) | Final ETCO2 (mmHg) | Pressure target | CO2 factor | CFI |
|---|---:|---:|---:|---:|---:|
| pressure-reduction | 92.668 | 40.0 | 0.98355 | 1.00000 | 0.98355 |
| co2-reduction | 100.000 | 30.0 | 1.00000 | 0.70469 | 0.70469 |
| combined-pressure-co2-reduction | 92.668 | 30.0 | 0.98355 | 0.70469 | 0.69310 |
| pressure-recovery-persistent-hypocapnia | 100.000 | 30.0 | 1.00000 | 0.70469 | 0.70469 |
| co2-recovery-persistent-pressure-reduction | 92.668 | 40.0 | 0.98355 | 1.00000 | 0.98355 |

## Readiness interpretation

- Empirical CO/SV comparisons outside their preserved published ranges: **8**.
- POTS/Long-COVID-autonomic sustained-HR criterion failures: **5**.
- Software execution and exact volume conservation do not resolve these physiological discrepancies.
- Stage 1.1 readiness therefore remains limited even when mathematical and traceability checks pass.
