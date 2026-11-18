# Stage 1.2 baseline reproduction

## Result

**REPRODUCED.** Before relying on any Stage 1.3 result, the available Stage 1.1 and Stage 1.2 source revisions were executed in fresh detached worktrees. The historical report was used only as a comparison target, never as a simulation input.

The comparison covers every numeric leaf in the historical protocol records, healthy summaries, POTS/Long-COVID-autonomic checks, Zaidi comparisons, retained misses, and cerebral pressure/CO₂ experiments:

| Check | Result |
|---|---:|
| Reported numeric fields compared | 957 |
| Numeric fields reproduced within tolerance | 957 |
| Maximum absolute numerical difference | 7.250436221797386 × 10⁻¹⁵ |
| Non-numeric identifiers/status fields compared | 277 |
| Non-numeric fields matched exactly | 277 |

The exhaustive field-level evidence, configuration hashes, solver metadata, tolerances, and environment are stored in `validation/stage1-3/baseline-reproduction.json`. Numerical reproduction establishes computational reproducibility, not physiological truth or clinical validity.

## Exact source and configuration provenance

| Role | Source revision | Execution |
|---|---|---|
| Stage 1.1 historical comparator | `f85360d8337144e118eb0d2aef317fd1b949b3dd` | Fresh detached-worktree execution |
| Stage 1.2 remediated baseline | `e48110e` | Fresh detached-worktree execution |
| Historical Stage 1.2 report | `validation/stage1-2/scientific-comparison-matrix.json` | SHA-256 recorded in the reproduction JSON |
| Pinned OCPE engine | `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d` | Unmodified |
| Solver | DOP853 | Protocol-declared tolerances and sampling retained |

The historical Stage 1.1 matrix embedded in the Stage 1.2 before/after report was also re-executed. This prevents the Stage 1.1 comparator from becoming an unverified copied number.

Representative reproduction commands were:

```bash
git worktree add --detach /tmp/ocpe-stage11-base f85360d8337144e118eb0d2aef317fd1b949b3dd
git worktree add --detach /tmp/ocpe-stage12-base e48110e
PYTHONPATH=/tmp/ocpe-stage11-base/src python /tmp/ocpe-stage11-base/scripts/run_stage1_1_validation.py
PYTHONPATH=/tmp/ocpe-stage12-base/src python /tmp/ocpe-stage12-base/scripts/run_stage1_1_validation.py
```

A second fresh execution recreated the historical record schema, including upright-end values, minimum upright MAP, regional volume changes, and the 120/300 s comparison points. Every result was then compared recursively with the preserved Stage 1.2 report.

## Key Stage 1.2 healthy results

The following are reproduced Stage 1.2 values, not Stage 1.3 outputs:

| Metric | Reproduced value |
|---|---:|
| Sustained 70° HR rise | 15.467102 bpm |
| Early minimum CO reduction | 14.569982% |
| CO reduction at 120 s | 18.731628% |
| CO reduction at 300 s | 18.730215% |
| SV reduction at 120 s | 33.439273% |
| SV reduction at 300 s | 33.437723% |
| End heart-level MAP | 108.846222 mmHg |
| Minimum upright MAP | 100.000000 mmHg |
| Caudal pooling | 302.962143 mL |
| Residual-systemic volume change | +162.152271 mL |
| Central-venous volume change | −478.383748 mL |
| End-CFI reduction | 4.406794% |
| Maximum five-volume drift | 3.638 × 10⁻¹² mL |

At direct 60° comparison, Stage 1.2 CO reductions were 15.800915% and 15.799697%, below the preserved 17–20% group band; SV reductions were 29.214900% and 29.213516%, within 28–34%. The 70° reuse of those ranges remained a model-specific comparison, not a separate 70° experiment.

All five cerebral pressure/CO₂ protocols and all historical phenotype criteria reproduced exactly at the reported precision. In particular, the four POTS and Long-COVID-autonomic sustained-HR results and their MAP-floor statuses were retained rather than rewritten.

## Source, fixture, and commit-diff verification

The `f85360d..e48110e` source/configuration diff agrees with the Stage 1.2 narrative:

- healthy splanchnic/lower-limb/other-systemic heights changed from 5.437737901/10.875475802/0 cm to 7/14/11 cm;
- the healthy cerebral autoregulation residual slope changed from 0.2 to 0.4;
- all four POTS configurations changed splanchnic/lower-limb heights from 6.797172376/13.594344753 cm to 8/16 cm;
- the Stage 1.2 regression-fixture change record documents those scientific changes and preserved criteria; and
- the architecture remains twelve states with five conserved stressed-blood-volume compartments.

The baseline allocation and all protocol/configuration hashes were checked during execution. Historical Stage 1.2 artifacts under `docs/stage1-2/` and `validation/stage1-2/` remain unchanged.

## Audit/repository discrepancies

1. The audit-named Stage 1.2 source object `6034d11d4737bca5d3b6d853900a69690ab90907` is not present in the available Git object database, and `2d1283f` is likewise unavailable. They cannot be claimed as executed revisions. The available branch revision `e48110e` was used instead; its fresh outputs reproduce the preserved Stage 1.2 report.
2. The historical report names `6034d11…` as its remediated source commit. Because that object is unavailable, this provenance statement cannot be independently resolved beyond the matching `e48110e` source, configurations, hashes, and numerical results.
3. The audit’s proposed Stage 1.3 numbers are not authoritative measurements. Fresh isolated/combined experiments did not reproduce the implied linear-proposal behavior; the complete executed comparison is in `validation/stage1-3/scientific-comparison-matrix.md`.
4. The historical record’s display schemas differ from the current time-resolved generator, but the underlying numerical fields reproduce. Schema renaming was not treated as a scientific discrepancy.

These discrepancies limit commit-level forensic claims, not the observed numerical reproducibility at the available revisions. They do not justify changing the 12-state/five-volume architecture or accepting the proposed Stage 1.3 values without independent experiments.
