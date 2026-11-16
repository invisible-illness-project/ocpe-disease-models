# Scientific Change Management

How scientific content in this repository may be changed: what requires
review, what provenance must accompany a change, and how changes are rolled
back. This document governs *process*; the layer and maturity definitions it
references live in `docs/validation/validation-architecture.md`.

## Principles

1. **No silent weakening.** A criterion the model cannot meet is recorded as
   a strict, reasoned expected failure or an explicit limitation — never
   relaxed, widened, or deleted to make a run green (legacy precedent: the two
   strict `xfail` markers in `docs/validation/legacy-validation-audit.md`).
2. **Maturity is not execution, and neither is clinical validity.** A green
   CI run never raises a maturity rating, and no maturity rating — including
   M4 — implies clinical validity or diagnostic accuracy.
3. **Provenance before merge.** Every scientific claim must resolve through
   the registry graph (`REF-` → `CLM-` → `MEC-`/`EQ-`/`PAR-` → `VAL-`/`SIM-`)
   before the change is merged; the strict traceability audit is a CI gate.
4. **Rollback is revert, not deletion.** History — including failed
   validation reports and superseded fixtures — is preserved.

## Change classes

| Change | Registry artifacts touched | Minimum review |
|---|---|---|
| Model code (`src/`) | `SIM-` records if persisted outputs change | Code review + full CI |
| Equation (structure, dimensional form) | `EQ-` entry, linked `MEC-`, affected `PAR-`, layer-2 acceptance criteria | Scientific review (below) |
| Parameter (value, bounds, units, source) | `PAR-` entry, linked `CLM-`/`REF-`, sensitivity scenarios | Scientific review |
| Evidence or reference | `CLM-` / `REF-` entries, evidence grade, limitations | Scientific review |
| Validation criterion | `VAL-` entry (acceptance criteria, maturity) | Scientific review + fixture review if fixtures change |
| Validation fixture (regression data, empirical anchors, curated demonstration outputs) | `VAL-`/`SIM-` entries, configuration SHA | Reviewed fixture update (below) |
| Scope statement (what the models claim) | `VAL-SCOPE-FUTURE`, docs | Scientific review |

A single pull request must update code, registries, fixtures, and docs
**atomically** — a code change whose registry provenance lands in a later PR
leaves the audit red in between and is not acceptable.

## Reviewed fixture updates

Fixtures are regression data under `tests/regression/`, empirical anchor
values under `validation/fixtures/`, and curated demonstration outputs under
`examples/*/output/` (pinned by `simulations/simulation_registry.yaml`).

A fixture update requires:

- **Stated motivation**: bug fix, corrected source value, intended model
  change, or refreshed upstream data. "Make CI pass" is not a motivation.
- **Source and license**: empirical anchors enter only with a citable,
  licensed source recorded in the linked `CLM-`/`REF-` entries.
- **Registry update in the same PR**: acceptance criteria, configuration
  SHA, or maturity fields change together with the fixture.
- **Independent review**: at least one reviewer who did not author the
  fixture confirms the diff against the stated motivation.
- **Regeneration, not hand-editing**: curated demonstration outputs are
  regenerated with `python scripts/run_examples.py` from the committed
  configuration; the new `configuration_sha256` is expected to differ and is
  recorded. Hand-edited outputs are treated as corrupted provenance.
- **Preserved history**: superseded fixtures are replaced in the working
  tree but remain in git history; committed validation reports are never
  edited in place.

## Equation, parameter, and evidence changes

**Equations.** Any structural change gets a new or versioned `EQ-` entry with
derivation, units, and linked references; dependent parameters are
re-reviewed; layer-2 (mathematical) acceptance criteria are updated in the
same PR; the maturity rating of every affected mechanism is reassessed.

**Parameters.** Every value traces to a `PAR-` entry with source links
(`CLM-`/`REF-`), units, bounds, and explicit limitations. A parameter whose
best source is direction-only stays direction-only (M2) — quantitative
values are not manufactured from qualitative evidence. Sensitivity scenarios
(`scripts/run_sensitivity.py`) are re-run so assumption-uncertainty reports
reflect the change.

**Evidence.** Claims are graded E0–E5 (below). An E0 assertion is not
eligible for implementation. Downgrading a claim's grade requires re-review
of every mechanism and parameter that links to it; upgrading requires the
stronger source in `literature/references.yaml`. Broken cross-registry links
fail the strict audit — they cannot drift silently.

## Maturity model (M0–M4) — and what it is not

Maturity rates how completely a mechanism, phenotype, or validation test is
*specified and evidenced*:

| Level | Meaning |
|---|---|
| M0 | Exploratory placeholder; registered so the gap is visible; must not be implemented numerically. |
| M1 | Scoped hypothesis; qualitative rationale only; no calibrated parameters claimed. |
| M2 | Directionally supported; literature supports direction, not values. |
| M3 | Mechanistic approximation; literature-grounded structure and sourced parameters; explicit limitations. |
| M4 | Fully specified and reproducible; quantitative deterministic acceptance criteria and complete provenance. |

Maturity is deliberately **separate from execution**: an M3 mechanism whose
test is not yet written is still M3 — the missing test appears as a layer
failure, not a maturity downgrade. Conversely, a passing test run never
raises maturity; only added evidence and specification do. And maturity is
**separate from clinical validity**: M4 does not mean clinically validated.
No maturity level, on its own or combined with green CI, establishes
diagnostic accuracy, individual-patient prediction, or fitness for clinical
use. This software is research-grade scenario validation only.

## Evidence grades (E0–E5)

| Grade | Meaning |
|---|---|
| E0 | Unsupported or contradicted assertion; not eligible for implementation. |
| E1 | Hypothesis, narrative mechanistic proposal, preprint, or indirect evidence. |
| E2 | Small, selected, or unreplicated human observational/physiological evidence. |
| E3 | Replicated human physiology or convergent controlled observational evidence with limitations. |
| E4 | Systematic review, meta-analysis, large controlled cohort, or formal consensus evidence. |
| E5 | Convergent high-quality evidence with independent prospective replication of the specific claim. |

Grades are recorded per claim in `literature/evidence_registry.yaml` and are
a property of the evidence for a *specific claim*, not of a reference in
general or of the model built on it.

## Required provenance for any scientific change

A pull request touching scientific content must include:

- New or updated registry entries (`REF-`, `CLM-`, `MEC-`, `EQ-`, `PAR-`,
  `VAL-`, `SIM-` as applicable) with working cross-registry links.
- Evidence grade and explicit limitations for every new or changed claim.
- Maturity rating (unchanged ratings are reaffirmed, not assumed).
- A passing strict traceability audit
  (`python scripts/audit_traceability.py --root . --strict`).
- For persisted runs: configuration SHA256, solver settings, dependency
  versions, and the pinned OCPE commit
  (`3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`), per
  `simulations/simulation_registry.yaml`.
- An honest statement of what the change does *not* establish.

## Rollback

- Roll back with `git revert` of the full change — code, registries,
  fixtures, and docs together — so the audit never sees a half-reverted
  provenance graph.
- Curated artifacts are restored by reverting their configuration and
  regenerating from the pinned configuration, never by editing outputs.
- Historical validation reports, legacy results, and `migration_archive/`
  content are provenance records: they are never deleted, "fixed", or
  rewritten during a rollback.
- After any rollback, re-run the full gate: `python -m pytest -q`, the strict
  audit, strict OCPE package validation, and
  `python scripts/run_validation.py`. A rollback that reopens a known
  limitation must say so in the commit message.

## CI enforcement

- `.github/workflows/ci.yml` (pull requests): Ruff, full pytest, strict
  traceability audit, strict OCPE package validation, pinned-commit check.
- `.github/workflows/validation.yml` (scheduled / main / manual): the six
  demonstrations, deterministic sensitivity analysis, and the seven-layer
  runner, which fails on any missing layer or empty test selection. Empty
  selections are failures by design and must not be silenced in CI.
