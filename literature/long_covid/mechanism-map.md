# Long COVID Mechanism Map

IDs refer to `literature/*.yaml`, `validation/validation_registry.yaml`, and
`simulations/simulation_registry.yaml`. Legend: **[measured]** human data in a
cited reference; **[assumption]** calibrated/chosen value or structure;
**[exploratory]** hypothesis-grade or unimplemented M0/M1 mechanism.

## Heterogeneity-first structure

Long COVID has no single parameterization. The registry enforces this at three
levels:

1. **Claim level:** CLM-LC-HETEROGENEITY (E4; REF-THAWEETHAI-2023,
   REF-DAVIS-2023, REF-DURSTENFELD-2022) — `modeling_implications`: "Never use
   a single uniform Long COVID parameter set."
2. **Configuration level:** two disjoint phenotype files
   (`long-covid-autonomic`, `long-covid-exertional`) with distinct mechanism
   sets.
3. **Validation level:** VAL-LC-AUTONOMIC requires that the autonomic and
   exertional configurations remain distinct in the registry.

## Subgroup A — autonomic / POTS-overlap (`long-covid-autonomic`, M3)

```
upright input u ──► EQ-ORT-001 regional venous-return opposition (MEC-VASC-POOLING)
        splanchnic/lower-limb gravity offsets = 5.5/11.0 mmHg       [assumption]
        ▼
head-level pressure error ──► EQ-AUT-001/002 sigmoid + differentiated lags
                                                        (MEC-AUT-BAROREFLEX)
        ▼
EQ-AUT-003 HR: rest 70.0; cardiac-sympathetic/vagal gains 50.0/50.0 [assumption]
        ▼
EQ-CBF-001/002 CPP-based cerebral index: impairment 0.08            [assumption]
        +
MEC-RCV-PEM: PEM threshold 0.001, response gain 12.0                [assumption]
```

- Claims: CLM-LC-HETEROGENEITY (E4), CLM-LC-AUTONOMIC (E2), CLM-LC-PEM (E3).
- **[measured] basis:** chronotropic/autonomic abnormalities in some patients
  (REF-DAVIS-2023, REF-DURSTENFELD-2022); no measured gain exists — every
  override is calibrated.
- VAL-LC-AUTONOMIC: HR rise ≥ 30 bpm with MAP ≥ 70 mmHg for this subgroup
  scenario. SIM-LC-AUTONOMIC persists the run under the status "One autonomic
  subgroup only; not a uniform Long COVID model."

## Subgroup B — exertional / impaired extraction (`long-covid-exertional`, M3)

```
EQ-MET-002: E_a-v = clip(E_0·(1 − k_EO·PEM), 0, 0.99); F = C·E_a-v/0.78
   E_0 = PAR-OXYGEN-EXTRACTION-FRACTION = 0.49
        [measured anchor: 0.49±0.1 vs 0.78±0.1, REF-SINGH-2022, n=20 selected]
EQ-MET-001: C = max(0.05, C_0·(1 − k_C·PEM))
   C_0 = PAR-BASELINE-METABOLIC-CAPACITY = 0.8                      [assumption]
MEC-RCV-PEM: threshold 0.001, response gain 16.0                    [assumption]
Central cardiac output preserved separately (matches REF-SINGH-2022)
```

- Claims: CLM-LC-EXTRACTION (E2), CLM-LC-CPET (E4), CLM-LC-MUSCLE (E2).
- VAL-LC-EXTRACTION: lower functional capacity at matched PEM severity; **no
  POTS-like HR criterion** is imposed, keeping the subgroup orthogonal.
- Guardrails: 0.49 is not a population estimate; shunt, mitochondrial flux and
  ventilatory control remain lumped (MEC-MET-EXTRACTION limitations); the
  meta-analytic 4.9 mL/kg/min capacity deficit (REF-DURSTENFELD-2022) is a
  group-level empirical context, not a mapping to normalized capacity.

## PEM branch (shared, subgroup-tuned)

MEC-RCV-PEM is reused from ME/CFS with reduced response gains (12.0 / 16.0
versus 20.0 in `mecfs-pem`). **[measured]** PEM is a highly weighted PASC
feature (REF-THAWEETHAI-2023) and followed exertion by one day in a selected
provocation study (REF-APPELMAN-2024). **[assumption]** the kinetic form and
time constants are borrowed from the ME/CFS calibration and are disclosed as
such (CLM-LC-PEM `modeling_implications`); identical parameters to ME/CFS are
not asserted. Muscle-tissue findings (REF-APPELMAN-2024; CLM-LC-MUSCLE, E2)
motivate dynamic stress/capacity modeling but contribute **no molecular
equation** — microclot and mitochondrial interpretations remain debated.

## Unimplemented modules mapped to this document

| Mechanism | Maturity | Status | Registry note |
|---|---|---|---|
| MEC-MICROVASC | **M0** | hypothesis, unimplemented | No microclot resistance, shunt-flow or endothelial-biomarker equation is defensible from current registry evidence (CLM-LC-ENDOTHELIAL, E1; REF-HAFFKE-2022, REF-PRETORIUS-2021) |
| MEC-RESP-LC | **M1** | proposed, unimplemented | Ventilatory inefficiency is a distinct future module; **[exploratory]**; oxygen-extraction phenotypes must not be treated as respiratory simulations (claims CLM-LC-CPET, CLM-LC-EXTRACTION) |

MEC-INFL-SIGNAL (M0) is cross-disease and is mapped in
`literature/cross_disease/mechanism-map.md` per registry designation.

## Validation and simulation inventory

| ID | Role |
|---|---|
| VAL-LC-AUTONOMIC (M3) | Autonomic subgroup scenario criterion; enforces subgroup distinctness |
| VAL-LC-EXTRACTION (M3) | Extraction subgroup: reduced capacity without an HR criterion |
| VAL-ME-PEM (M3) | Shared PEM temporal validation reused by both subgroups |
| VAL-EMPIRICAL-ANCHORS | Ties extraction and CPET comparisons to cited group-level findings |
| SIM-LC-AUTONOMIC | Persisted autonomic-subgroup run |
| SIM-CROSS-DISEASE | Includes the autonomic configuration under non-equivalent-evidence caveats |

## Boundaries

- Two subgroups are implemented; the registry evidence supports heterogeneity
  (E4) but only low-to-moderate confidence in each subgroup's magnitudes.
- No viral-persistence, microclot, immune-signaling, or respiratory dynamics
  are encoded anywhere in the executable model.
- Long COVID configurations borrow shared mechanisms; borrowing is labeled in
  every configuration's limitations rather than hidden.
