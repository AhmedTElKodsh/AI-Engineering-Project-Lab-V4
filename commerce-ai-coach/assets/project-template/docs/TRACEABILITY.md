# Requirements traceability

This map links PRD requirements to work packages and planned evidence. It is generated from `learning/backlog.json`: the task list is every task naming the requirement, and the representative tests are the focused tests of the first three of those tasks. Test files are to be implemented; this is not a passing-test report.

| Requirement | Tasks | Representative tests |
|---|---|---|
| FR01 | T004, T008, T011, T016 | `tests/unit/test_schemas.py`; `tests/integration/test_tenant_repositories.py`; `tests/contract/test_grounded_draft.py` |
| FR02 | T004, T005, T006 | `tests/unit/test_schemas.py`; `tests/contract/test_model_client.py`; `tests/unit/test_ticket_analysis.py` |
| FR03 | T009, T026 | `tests/integration/test_ingestion_versions.py`; `tests/integration/test_job_recovery.py` |
| FR04 | T010, T011, T012, T024 | `tests/integration/test_retrieval_scope.py`; `tests/contract/test_grounded_draft.py`; `tests/integration/test_hybrid_retrieval.py` |
| FR05 | T008, T013 | `tests/integration/test_tenant_repositories.py`; `tests/security/test_read_tools.py` |
| FR06 | T003, T014 | `tests/unit/test_fixture_contracts.py`; `tests/unit/test_replacement_rules.py` |
| FR07 | T006, T015, T016, T028 | `tests/unit/test_ticket_analysis.py`; `tests/integration/test_case_graph.py`; `tests/security/test_workflow_resume.py` |
| FR08 | T017, T020 | `tests/security/test_approval_binding.py`; `tests/e2e/test_replacement_journey.py` |
| FR09 | T018, T019, T020, T028 | `tests/integration/test_replacement_execution.py`; `tests/contract/test_action_reconciliation.py`; `tests/e2e/test_replacement_journey.py` |
| FR10 | T011, T020 | `tests/contract/test_grounded_draft.py`; `tests/e2e/test_replacement_journey.py` |
| FR11 | T005, T007, T012, T015, T021, T022, T024, T029 | `tests/contract/test_model_client.py`; `tests/unit/test_eval_scoring.py`; `tests/integration/test_hybrid_retrieval.py` |
| FR12 | T023, T024, T029 | `tests/unit/test_routing_pipeline.py`; `tests/unit/test_experiment_manifest.py`; `tests/contract/test_release_manifest.py` |
| FR13 | T026 | `tests/integration/test_job_recovery.py` |
| FR14 | T001, T002, T025, T027, T029, T030 | `tests/unit/test_health.py`; `tests/unit/test_config.py`; `tests/security/test_oidc_and_privacy.py` |
| NFR01 | T004, T008, T009, T010, T013, T014, T016, T017, T018, T021, T025, T029 | `tests/unit/test_schemas.py`; `tests/integration/test_tenant_repositories.py`; `tests/integration/test_ingestion_versions.py` |
| NFR02 | T016, T018, T019, T021, T026, T028, T029 | `tests/security/test_workflow_resume.py`; `tests/integration/test_replacement_execution.py`; `tests/contract/test_action_reconciliation.py` |
| NFR03 | T007, T010, T012, T021, T023, T024, T029 | `tests/unit/test_eval_scoring.py`; `tests/integration/test_retrieval_scope.py`; `tests/integration/test_hybrid_retrieval.py` |
| NFR04 | T007, T015, T022, T026, T027, T029 | `tests/unit/test_eval_scoring.py`; `tests/integration/test_case_graph.py`; `tests/unit/test_observability.py` |
| NFR05 | T005, T012, T015, T022, T024, T028, T029 | `tests/contract/test_model_client.py`; `tests/integration/test_hybrid_retrieval.py`; `tests/integration/test_case_graph.py` |
| NFR06 | T001, T002, T003, T005, T008, T023, T027, T029, T030 | `tests/unit/test_health.py`; `tests/unit/test_config.py`; `tests/unit/test_fixture_contracts.py` |
| NFR07 | T002, T009, T022, T025, T027, T029 | `tests/unit/test_config.py`; `tests/integration/test_ingestion_versions.py`; `tests/unit/test_observability.py` |
| NFR08 | T028, T029 | `tests/integration/test_chaos_recovery.py`; `tests/contract/test_release_manifest.py` |
