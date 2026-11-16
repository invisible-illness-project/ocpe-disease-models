# Scientific Traceability Audit Report

- Tool: `ocpe-traceability-audit` v1.0.0
- Generated at: 2026-11-16T17:15:21+00:00
- Git SHA: e87401ddd435d2fd1d5e15420308086051229851
- OCPE commit: unknown
- Schema validation: ran
- **Status: PASS** (0 errors, 0 warnings, 0 infos)

## Registries

| Registry | Path | Entries | Load errors |
| --- | --- | ---: | ---: |
| references | literature/references.yaml | 38 | 0 |
| evidence | literature/evidence_registry.yaml | 22 | 0 |
| mechanisms | literature/mechanism_registry.yaml | 19 | 0 |
| equations | literature/equation_registry.yaml | 18 | 0 |
| parameters | literature/parameter_registry.yaml | 35 | 0 |
| validation_tests | validation/validation_registry.yaml | 24 | 0 |
| simulations | simulations/simulation_registry.yaml | 8 | 0 |

## Completeness

| Registry | Metric | Passed | Total | Rate |
| --- | --- | ---: | ---: | ---: |
| references | entries_with_id | 38 | 38 | 100.0% |
| evidence | entries_with_id | 22 | 22 | 100.0% |
| evidence | claims_with_references | 22 | 22 | 100.0% |
| mechanisms | entries_with_id | 19 | 19 | 100.0% |
| mechanisms | mechanisms_with_claims_or_exploratory | 19 | 19 | 100.0% |
| mechanisms | implemented_mechanisms_with_tests | 11 | 11 | 100.0% |
| equations | entries_with_id | 18 | 18 | 100.0% |
| equations | equations_with_expression | 18 | 18 | 100.0% |
| equations | equations_with_assumptions | 18 | 18 | 100.0% |
| equations | equations_with_provenance | 18 | 18 | 100.0% |
| equations | equations_fully_documented | 18 | 18 | 100.0% |
| parameters | entries_with_id | 35 | 35 | 100.0% |
| parameters | parameters_with_source | 35 | 35 | 100.0% |
| parameters | parameters_with_estimation_method | 35 | 35 | 100.0% |
| parameters | parameters_with_provenance | 35 | 35 | 100.0% |
| parameters | parameters_fully_documented | 35 | 35 | 100.0% |
| validation_tests | entries_with_id | 24 | 24 | 100.0% |
| validation_tests | tests_with_expected_behavior | 24 | 24 | 100.0% |
| validation_tests | tests_with_acceptance_criteria | 24 | 24 | 100.0% |
| validation_tests | tests_with_justification | 24 | 24 | 100.0% |
| validation_tests | tests_fully_specified | 24 | 24 | 100.0% |
| simulations | entries_with_id | 8 | 8 | 100.0% |
| simulations | simulations_with_config | 8 | 8 | 100.0% |
| simulations | simulations_with_model_provenance | 8 | 8 | 100.0% |

## Findings

No findings. Full traceability achieved.
