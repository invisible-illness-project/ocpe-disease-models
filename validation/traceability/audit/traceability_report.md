# Scientific Traceability Audit Report

- Tool: `ocpe-traceability-audit` v1.0.0
- Generated at: 2026-11-16T21:24:30+00:00
- Git SHA: fb13cb21aa811da9babff6b271f006b8c79ec30f
- OCPE commit: unknown
- Schema validation: ran
- **Status: PASS** (0 errors, 0 warnings, 0 infos)

## Registries

| Registry | Path | Entries | Load errors |
| --- | --- | ---: | ---: |
| references | literature/references.yaml | 64 | 0 |
| evidence | literature/evidence_registry.yaml | 37 | 0 |
| mechanisms | literature/mechanism_registry.yaml | 23 | 0 |
| equations | literature/equation_registry.yaml | 20 | 0 |
| parameters | literature/parameter_registry.yaml | 52 | 0 |
| validation_tests | validation/validation_registry.yaml | 26 | 0 |
| simulations | simulations/simulation_registry.yaml | 8 | 0 |

## Completeness

| Registry | Metric | Passed | Total | Rate |
| --- | --- | ---: | ---: | ---: |
| references | entries_with_id | 64 | 64 | 100.0% |
| evidence | entries_with_id | 37 | 37 | 100.0% |
| evidence | claims_with_references | 37 | 37 | 100.0% |
| mechanisms | entries_with_id | 23 | 23 | 100.0% |
| mechanisms | mechanisms_with_claims_or_exploratory | 23 | 23 | 100.0% |
| mechanisms | implemented_mechanisms_with_tests | 13 | 13 | 100.0% |
| equations | entries_with_id | 20 | 20 | 100.0% |
| equations | equations_with_expression | 20 | 20 | 100.0% |
| equations | equations_with_assumptions | 20 | 20 | 100.0% |
| equations | equations_with_provenance | 20 | 20 | 100.0% |
| equations | equations_fully_documented | 20 | 20 | 100.0% |
| parameters | entries_with_id | 52 | 52 | 100.0% |
| parameters | parameters_with_source | 52 | 52 | 100.0% |
| parameters | parameters_with_estimation_method | 52 | 52 | 100.0% |
| parameters | parameters_with_provenance | 52 | 52 | 100.0% |
| parameters | parameters_fully_documented | 52 | 52 | 100.0% |
| validation_tests | entries_with_id | 26 | 26 | 100.0% |
| validation_tests | tests_with_expected_behavior | 26 | 26 | 100.0% |
| validation_tests | tests_with_acceptance_criteria | 26 | 26 | 100.0% |
| validation_tests | tests_with_justification | 26 | 26 | 100.0% |
| validation_tests | tests_fully_specified | 26 | 26 | 100.0% |
| simulations | entries_with_id | 8 | 8 | 100.0% |
| simulations | simulations_with_config | 8 | 8 | 100.0% |
| simulations | simulations_with_model_provenance | 8 | 8 | 100.0% |

## Findings

No findings. Full traceability achieved.
