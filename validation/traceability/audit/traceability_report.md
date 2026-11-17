# Scientific Traceability Audit Report

- Tool: `ocpe-traceability-audit` v1.0.0
- Generated at: deterministic (suppressed)
- Git SHA: unknown
- OCPE commit: unknown
- Schema validation: ran
- **Status: PASS** (0 errors, 0 warnings, 0 infos)

## Registries

| Registry | Path | Entries | Load errors |
| --- | --- | ---: | ---: |
| references | literature/references.yaml | 69 | 0 |
| evidence | literature/evidence_registry.yaml | 41 | 0 |
| mechanisms | literature/mechanism_registry.yaml | 24 | 0 |
| equations | literature/equation_registry.yaml | 22 | 0 |
| parameters | literature/parameter_registry.yaml | 68 | 0 |
| validation_tests | validation/validation_registry.yaml | 29 | 0 |
| simulations | simulations/simulation_registry.yaml | 11 | 0 |

## Completeness

| Registry | Metric | Passed | Total | Rate |
| --- | --- | ---: | ---: | ---: |
| references | entries_with_id | 69 | 69 | 100.0% |
| evidence | entries_with_id | 41 | 41 | 100.0% |
| evidence | claims_with_references | 41 | 41 | 100.0% |
| mechanisms | entries_with_id | 24 | 24 | 100.0% |
| mechanisms | mechanisms_with_claims_or_exploratory | 24 | 24 | 100.0% |
| mechanisms | implemented_mechanisms_with_tests | 15 | 15 | 100.0% |
| equations | entries_with_id | 22 | 22 | 100.0% |
| equations | equations_with_expression | 22 | 22 | 100.0% |
| equations | equations_with_assumptions | 22 | 22 | 100.0% |
| equations | equations_with_provenance | 22 | 22 | 100.0% |
| equations | equations_fully_documented | 22 | 22 | 100.0% |
| parameters | entries_with_id | 68 | 68 | 100.0% |
| parameters | parameters_with_source | 68 | 68 | 100.0% |
| parameters | parameters_with_estimation_method | 68 | 68 | 100.0% |
| parameters | parameters_with_provenance | 68 | 68 | 100.0% |
| parameters | parameters_fully_documented | 68 | 68 | 100.0% |
| validation_tests | entries_with_id | 29 | 29 | 100.0% |
| validation_tests | tests_with_expected_behavior | 29 | 29 | 100.0% |
| validation_tests | tests_with_acceptance_criteria | 29 | 29 | 100.0% |
| validation_tests | tests_with_justification | 29 | 29 | 100.0% |
| validation_tests | tests_fully_specified | 29 | 29 | 100.0% |
| simulations | entries_with_id | 11 | 11 | 100.0% |
| simulations | simulations_with_config | 11 | 11 | 100.0% |
| simulations | simulations_with_model_provenance | 11 | 11 | 100.0% |

## Findings

No findings. Full traceability achieved.
