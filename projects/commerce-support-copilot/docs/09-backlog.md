# Engineering backlog

**Thirty implementation work packages.** Nothing is marked complete. Planned file paths and test commands below do not imply those files exist yet. Machine-readable equivalent: `learning/backlog.json` (schema version 2). Change both together; `tools/validate_bundle.py` in the V4 bundle checks that they match.

## Per-task workflow

Read the referenced requirements and contracts; state one acceptance behavior; write a failing test; confirm the failure is meaningful; implement the smallest change; run the listed test and relevant regressions; review the diff; save evidence; then update progress under `learning/progress-protocol.md`. The first task has a worked implementation plan. Later tasks receive just-in-time detail from the coach, not an unsolicited complete solution.

## Field conventions

- **Dependencies** list only direct prerequisites; indirect ones follow from the chain.
- **Required for** names the lowest release level that needs the task (see `08-roadmap.md`).
- **Planned files** exclude the focused test and any additional tests, which are listed separately.

## Definition of ready

Dependencies are done or independently evidenced as already implemented; interfaces are understood; the needed environment and budget are available; a concrete acceptance test can be named.

## Definition of done

Acceptance criteria met; tests passing with saved output; review recorded; documentation/config updated when changed; no leaked secrets; no unreviewed scope expansion. Learning mastery remains a separate field.

## T001 - Create a reproducible service and health test

**Milestone:** M0 | **Dependencies:** none | **Requirements:** FR14, NFR06

**Required for:** Read-only demo (and every higher level)

**Planned files:** `pyproject.toml`, `.python-version`, `uv.lock`, `src/commerce_support/__init__.py`, `src/commerce_support/main.py`.

**Acceptance behaviors:**
- A clean environment resolves the committed lock and installs the `commerce_support` package through a declared build system; importing it works outside pytest.
- GET /health/live returns 200 and {"status":"ok"}; an unknown route returns 404.
- The health test runs with no API key, model call, database, or external service.

**Focused test:** `tests/unit/test_health.py`. After creation, run `uv run pytest tests/unit/test_health.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Python environment, packaging, HTTP, FastAPI, pytest, Git.

**Teach-back:** Explain the request/response path, why a virtual environment is needed, what the lockfile adds to pyproject.toml, and what the build-system table changes.

**Checkpoint:** evidence and review for T001 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T002 - Add quality checks, config boundaries, log redaction, and offline CI

**Milestone:** M0 | **Dependencies:** T001 | **Requirements:** FR14, NFR06, NFR07

**Required for:** Read-only demo (and every higher level)

**Planned files:** `.github/workflows/ci.yml`, `.gitignore`, `.env.example`, `src/commerce_support/config.py`, `src/commerce_support/observability/redaction.py`, `pyproject.toml`.

**Acceptance behaviors:**
- The default model mode is fake and no secret is required to run routine tests.
- Invalid configuration produces a clear startup validation error; .env and local data are ignored by Git.
- Lint, formatting, type checks, and unit tests run in a clean CI job; a deliberately broken test fails the job.
- A redaction filter on application log handlers removes customer message bodies, Authorization headers, and secret-like values; a test proves they never appear in captured log output.

**Focused test:** `tests/unit/test_config.py`. After creation, run `uv run pytest tests/unit/test_config.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Additional tests:** `tests/unit/test_log_redaction.py` (run together with the focused test and save their output in the same evidence file).

**Learning focus:** Ruff, type checking, Pydantic settings, CI, secrets, log redaction.

**Teach-back:** Explain the difference between a type checker, a runtime validator, and a test, and why CI should not require paid calls.

**Checkpoint:** evidence and review for T002 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T003 - Define synthetic commerce and policy fixtures

**Milestone:** M0 | **Dependencies:** T001 | **Requirements:** FR06, NFR06

**Required for:** Read-only demo (and every higher level)

**Planned files:** `tests/fixtures/commerce.json`, `tests/fixtures/policy_v1.json`, `tests/fixtures/policy_v2.json`, `tests/conftest.py`.

**Acceptance behaviors:**
- Fixtures cover two tenants, eligible/ineligible claims, missing delivery, empty stock, duplicates, a multi-line order, the same order reference in both tenants, two conflicting policy keys, and a policy change.
- All references resolve within a tenant, delivery time exists only on shipment records, and fixture creation is deterministic from a fixed clock.
- The seven-day boundary and a store-timezone date-boundary example have explicit expected outcomes.

**Focused test:** `tests/unit/test_fixture_contracts.py`. After creation, run `uv run pytest tests/unit/test_fixture_contracts.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Data modeling, fixtures, timezones, business rules.

**Teach-back:** Explain why fictional policy rules must be explicit and why a frozen clock prevents time-dependent tests.

**Checkpoint:** evidence and review for T003 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T004 - Implement the typed case and analysis contracts

**Milestone:** M1 | **Dependencies:** T002, T003 | **Requirements:** FR01, FR02, NFR01

**Required for:** Read-only demo (and every higher level)

**Planned files:** `src/commerce_support/cases/schemas.py`, `src/commerce_support/auth/principal.py`, `src/commerce_support/commerce/schemas.py`, `src/commerce_support/workflow/states.py`.

**Acceptance behaviors:**
- TicketAnalysis uses the six documented intent values, an order reference and product mention (never internal IDs), explicit nulls, and forbidden extra fields.
- Blank/oversized messages and invalid quantity or enum values are rejected.
- Principal is separate from model schemas; model fields cannot set tenant, roles, or approval.
- Case and proposal status enums match `02-architecture.md` §4 exactly, and the transition tables are encoded as data that rejects unlisted transitions.

**Focused test:** `tests/unit/test_schemas.py`. After creation, run `uv run pytest tests/unit/test_schemas.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Pydantic, JSON Schema, validation, trust boundaries.

**Teach-back:** Show an output that is schema-valid but factually wrong. Explain which layer must detect it.

**Checkpoint:** evidence and review for T004 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T005 - Build fake and hosted model adapter contracts

**Milestone:** M1 | **Dependencies:** T004 | **Requirements:** FR02, FR11, NFR05, NFR06

**Required for:** Read-only demo (and every higher level)

**Planned files:** `src/commerce_support/ai/client.py`, `src/commerce_support/ai/fake.py`, `src/commerce_support/ai/hosted.py`.

**Acceptance behaviors:**
- Fake and hosted adapters have the same typed response, usage, and error interfaces.
- Timeout, unavailable provider, invalid output, and zero-success cost handling have deterministic tests.
- Live execution requires an explicit mode and approved budget; SDK/model IDs are configuration, not scattered literals.

**Focused test:** `tests/contract/test_model_client.py`. After creation, run `uv run pytest tests/contract/test_model_client.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Model APIs, adapters, dependency injection, timeouts, token usage.

**Teach-back:** Explain dependency injection and show how the adapter lets you test an outage without calling a provider.

**Checkpoint:** evidence and review for T005 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T006 - Create the extraction prompt and baseline analysis

**Milestone:** M1 | **Dependencies:** T005 | **Requirements:** FR02, FR07

**Required for:** Read-only demo (and every higher level)

**Planned files:** `prompts/ticket_analysis_v1.md`, `src/commerce_support/ai/analysis.py`.

**Acceptance behaviors:**
- The damaged-item sample extracts order reference 1042, product mention "blender", and a replacement preference without emitting any internal ID.
- Missing identifiers remain null; injected instructions do not create privileged fields.
- At most one schema repair occurs within the model-attempt budget; repeated invalid output becomes a typed failure.

**Focused test:** `tests/unit/test_ticket_analysis.py`. After creation, run `uv run pytest tests/unit/test_ticket_analysis.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Prompting, few-shot examples, structured output, failure handling.

**Teach-back:** Explain why extraction is not eligibility assessment and what a repair attempt can and cannot guarantee.

**Checkpoint:** evidence and review for T006 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T007 - Start the evaluation harness and record a baseline

**Milestone:** M1 | **Dependencies:** T006 | **Requirements:** FR11, NFR03, NFR04

**Required for:** Read-only demo (and every higher level)

**Planned files:** `evals/development.jsonl`, `evals/run.py`, `evals/scorers.py`, `evals/manifest.json`.

**Acceptance behaviors:**
- The twelve development seeds run through a deterministic adapter and emit per-case results plus aggregates.
- Scorers handle missing evidence, zero claims, failed runs, and zero successful cases without misleading 100% scores.
- Every report names dataset, model/fake mode, prompt version, commit, and whether calls were actually live.

**Focused test:** `tests/unit/test_eval_scoring.py`. After creation, run `uv run pytest tests/unit/test_eval_scoring.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Evaluation design, baselines, datasets, metrics, provenance.

**Teach-back:** Explain why a believable demo is not an evaluation and why development cases cannot become an untouched holdout.

**Checkpoint:** evidence and review for T007 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T008 - Add PostgreSQL migrations and tenant-scoped repositories

**Milestone:** M2 | **Dependencies:** T004 | **Requirements:** FR01, FR05, NFR01, NFR06

**Required for:** Read-only demo (and every higher level)

**Planned files:** `src/commerce_support/db/models.py`, `src/commerce_support/db/session.py`, `migrations/`, `src/commerce_support/cases/repository.py`.

**Acceptance behaviors:**
- Migrations create the case, commerce, policy, and version constraints (including one active policy version per key and the case-to-order binding) in a disposable PostgreSQL database.
- Case/order reads and writes require a principal and reject cross-tenant references without disclosure.
- Seed/reset commands are repeatable against the isolated test database and refuse production-like targets.

**Focused test:** `tests/integration/test_tenant_repositories.py`. After creation, run `uv run pytest tests/integration/test_tenant_repositories.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** SQL, PostgreSQL, SQLAlchemy, Alembic, authorization.

**Teach-back:** Explain a foreign key, a unique constraint, and why filtering only in the UI cannot enforce tenant isolation.

**Checkpoint:** evidence and review for T008 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T009 - Implement idempotent versioned knowledge ingestion

**Milestone:** M2 | **Dependencies:** T008 | **Requirements:** FR03, NFR01, NFR07

**Required for:** Read-only demo (and every higher level)

**Planned files:** `src/commerce_support/knowledge/ingest.py`, `src/commerce_support/knowledge/chunking.py`, `src/commerce_support/knowledge/versions.py`, `src/commerce_support/api/knowledge.py`.

**Acceptance behaviors:**
- Text/Markdown/text-based PDF ingestion preserves checksums, source locators, tenant, and version.
- Re-ingestion does not duplicate searchable chunks; an interrupted import stays nonsearchable.
- Unsupported or oversized files fail safely, and activation atomically retires the previous policy version.
- The upload endpoint returns 202 with a job ID; the in-process job ends as succeeded, failed, or quarantined and is readable through the job endpoint.

**Focused test:** `tests/integration/test_ingestion_versions.py`. After creation, run `uv run pytest tests/integration/test_ingestion_versions.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** ETL, document parsing, chunking, metadata, idempotency.

**Teach-back:** Explain why chunk IDs, source locations, and version IDs are different and how atomic activation prevents mixed policies.

**Checkpoint:** evidence and review for T009 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T010 - Build the semantic retrieval baseline

**Milestone:** M2 | **Dependencies:** T007, T009 | **Requirements:** FR04, NFR01, NFR03

**Required for:** Read-only demo (and every higher level)

**Planned files:** `src/commerce_support/knowledge/embeddings.py`, `src/commerce_support/knowledge/retrieval.py`, `evals/retrieval.py`.

**Acceptance behaviors:**
- Embeddings record their index version (model, revision, dimension, preprocessing) and retrieve authorized active-version sections.
- Old policies and foreign-tenant chunks never enter model context, including queries designed to match them exactly.
- Section-level recall@5 is measured against development gold sections using an exact-search baseline.

**Focused test:** `tests/integration/test_retrieval_scope.py`. After creation, run `uv run pytest tests/integration/test_retrieval_scope.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Embeddings, pgvector, vector search, recall@k, metadata filters.

**Teach-back:** Explain embeddings, similarity, why dimensions must match, and why duplicate chunks can inflate a retrieval metric.

**Checkpoint:** evidence and review for T010 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T011 - Draft grounded answers and build a read-only case view

**Milestone:** M2 | **Dependencies:** T010 | **Requirements:** FR01, FR04, FR10

**Required for:** Read-only demo (and every higher level)

**Planned files:** `prompts/resolution_draft_v1.md`, `src/commerce_support/ai/drafting.py`, `src/commerce_support/api/cases.py`, `ui/app.py`.

**Acceptance behaviors:**
- A draft cites only authorized retrieved section IDs and distinguishes customer statements from observed facts.
- Missing/conflicting policy produces clarification or escalation rather than fabricated support.
- The read-only UI shows message, draft, sources, run ID, and errors; it does not offer commerce execution.

**Focused test:** `tests/contract/test_grounded_draft.py`. After creation, run `uv run pytest tests/contract/test_grounded_draft.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** RAG generation, citations, Streamlit, API integration, abstention.

**Teach-back:** Explain the difference between citation validity and factual support, and show an abstention that is a correct result.

**Checkpoint:** evidence and review for T011 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T012 - Compare hybrid retrieval and optional reranking

**Milestone:** M2 | **Dependencies:** T010 | **Requirements:** FR04, FR11, NFR03, NFR05

**Required for:** Complete portfolio only

**Planned files:** `src/commerce_support/knowledge/hybrid.py`, `src/commerce_support/knowledge/reranking.py`, `evals/compare_retrieval.py`.

**Acceptance behaviors:**
- A generated tsvector column with a GIN index supplies keyword rankings; keyword and vector rankings combine with documented fusion parameters after authorization filtering.
- Semantic, hybrid, and optional reranked results use the same development queries and section-level metric.
- The report includes latency and failure examples; adopt reranking only when the measured tradeoff is worthwhile.

**Focused test:** `tests/integration/test_hybrid_retrieval.py`. After creation, run `uv run pytest tests/integration/test_hybrid_retrieval.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Full-text search, rank fusion, cross-encoder, controlled experiments.

**Teach-back:** Explain a query where keyword search can help and a case where reranking adds latency without a useful gain.

**Checkpoint:** evidence and review for T012 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T013 - Implement narrow authorized business-read tools

**Milestone:** M3 | **Dependencies:** T005, T008 | **Requirements:** FR05, NFR01

**Required for:** Sandbox workflow MVP (and complete portfolio)

**Planned files:** `src/commerce_support/commerce/read_tools.py`, `src/commerce_support/commerce/sandbox.py`.

**Acceptance behaviors:**
- Order, stock, shipment, and replacement-history tools validate arguments with strict schemas and inject the authenticated principal server-side.
- Unknown and inaccessible orders return the same safe external error.
- Timeouts and missing records have typed outcomes; each result carries a timestamp/version.
- lookup_order returns every order line and the delivery time from the latest delivered shipment, and binds the case to that order on first success.

**Focused test:** `tests/security/test_read_tools.py`. After creation, run `uv run pytest tests/security/test_read_tools.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Function calling, tool schemas, permissions, service integration.

**Teach-back:** Explain why tool arguments cannot supply trusted roles and why a tool result needs freshness metadata.

**Checkpoint:** evidence and review for T013 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T014 - Implement deterministic replacement eligibility

**Milestone:** M3 | **Dependencies:** T004 | **Requirements:** FR06, NFR01

**Required for:** Sandbox workflow MVP (and complete portfolio)

**Planned files:** `src/commerce_support/commerce/rules.py`, `src/commerce_support/commerce/policy.py`.

**Acceptance behaviors:**
- BR01-BR08 map to explicit eligible, needs-information, ineligible, or manual-review reason codes.
- Seven-day/eight-day, negative age, missing delivery, wrong category, multi-line order, ambiguous or unmatched product mention, quantity, duplicate, and no-stock cases are tested.
- The rule and line-resolution functions are pure (no I/O or clock reads); the model cannot override rule outcomes or supply a different policy version.

**Focused test:** `tests/unit/test_replacement_rules.py`. After creation, run `uv run pytest tests/unit/test_replacement_rules.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Rule engines, date arithmetic, pure functions, boundary tests.

**Teach-back:** Explain which decisions belong in ordinary code and implement a changed boundary without editing the prompt.

**Checkpoint:** evidence and review for T014 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T015 - Create the bounded LangGraph case workflow

**Milestone:** M3 | **Dependencies:** T011, T013, T014 | **Requirements:** FR07, FR11, NFR04, NFR05

**Required for:** Sandbox workflow MVP (and complete portfolio)

**Planned files:** `src/commerce_support/workflow/state.py`, `src/commerce_support/workflow/graph.py`, `src/commerce_support/workflow/nodes.py`.

**Acceptance behaviors:**
- Graph nodes reuse tested functions and follow defined clarification, proposal, escalation, and error branches.
- A run respects four model attempts, eight read attempts, and the wall-time ceiling.
- Per-node trace IDs and state transitions are persisted without exposing credentials or hidden reasoning.

**Focused test:** `tests/integration/test_case_graph.py`. After creation, run `uv run pytest tests/integration/test_case_graph.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** LangChain, LangGraph, state machines, bounded agents, orchestration.

**Teach-back:** Explain when a graph adds value over functions and why adding more autonomous agents would not solve these requirements.

**Checkpoint:** evidence and review for T015 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T016 - Persist and authorize pause/resume across restarts

**Milestone:** M3 | **Dependencies:** T015 | **Requirements:** FR01, FR07, NFR01, NFR02

**Required for:** Sandbox workflow MVP (and complete portfolio)

**Planned files:** `src/commerce_support/workflow/checkpoints.py`, `src/commerce_support/workflow/resume.py`.

**Acceptance behaviors:**
- An interrupted case resumes from a durable checkpoint after process restart.
- Foreign-tenant thread IDs and stale case versions cannot resume or disclose a case.
- Node replay before an interrupt performs no unguarded irreversible side effect.

**Focused test:** `tests/security/test_workflow_resume.py`. After creation, run `uv run pytest tests/security/test_workflow_resume.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Persistence, interrupts, resume authorization, optimistic concurrency.

**Teach-back:** Explain the difference between conversational memory, a checkpoint, an approval record, and current business truth.

**Checkpoint:** evidence and review for T016 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T017 - Bind manager decisions to immutable proposals

**Milestone:** M4 | **Dependencies:** T016 | **Requirements:** FR08, NFR01

**Required for:** Sandbox workflow MVP (and complete portfolio)

**Planned files:** `src/commerce_support/actions/proposals.py`, `src/commerce_support/actions/approval.py`, `src/commerce_support/api/proposals.py`.

**Acceptance behaviors:**
- Proposal hash binds exact parameters, identities, case, order version, and policy version.
- Self-approval, wrong tenant/role, expiry 15 minutes after creation, changed hash, and stale versions are rejected; a policy or order-version change marks pending and approved proposals invalidated.
- Decision revise sets revision_requested and a new proposal supersedes it; a proposal for a line outside the case's bound order is rejected; a message claiming approval never creates an approval record.

**Focused test:** `tests/security/test_approval_binding.py`. After creation, run `uv run pytest tests/security/test_approval_binding.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Human-in-the-loop, canonicalization, authorization, TOCTOU.

**Teach-back:** Explain why approving a case is weaker than approving an immutable action and demonstrate a stale-proposal failure.

**Checkpoint:** evidence and review for T017 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T018 - Execute one transactional idempotent sandbox write

**Milestone:** M4 | **Dependencies:** T017 | **Requirements:** FR09, NFR01, NFR02

**Required for:** Sandbox workflow MVP (and complete portfolio)

**Planned files:** `src/commerce_support/actions/execution.py`, `src/commerce_support/actions/ledger.py`, `migrations/`.

**Acceptance behaviors:**
- One transaction reserves stock, creates the request, records the execution, and appends audit.
- Same-key replay returns the original result; changed payload conflicts; a different-key duplicate cannot create another replacement.
- Concurrent last-unit requests never produce negative stock; a lost response after commit is recovered by key lookup.
- Only an active same-tenant manager who is not the proposer can execute; each proposal has at most one execution; the application database role cannot update or delete audit rows.

**Focused test:** `tests/integration/test_replacement_execution.py`. After creation, run `uv run pytest tests/integration/test_replacement_execution.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Transactions, row locks, idempotency, unique constraints, race conditions.

**Teach-back:** Explain why a retry loop or Redis lock alone does not prevent duplicates, and what the database constraint guarantees.

**Checkpoint:** evidence and review for T018 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T019 - Model external write uncertainty and reconciliation

**Milestone:** M4 | **Dependencies:** T018 | **Requirements:** FR09, NFR02

**Required for:** Complete portfolio only

**Planned files:** `src/commerce_support/actions/outbox.py`, `src/commerce_support/actions/reconcile.py`, `tests/fixtures/fake_downstream.py`.

**Acceptance behaviors:**
- A scripted downstream adapter can commit and then time out; the app records reconciliation_required.
- Status lookup with the original key recovers a known result without a second effect.
- An adapter without idempotency/status lookup requires manual reconciliation rather than blind retry.

**Focused test:** `tests/contract/test_action_reconciliation.py`. After creation, run `uv run pytest tests/contract/test_action_reconciliation.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Outbox, distributed failure, reconciliation, adapter contracts.

**Teach-back:** Explain why a network timeout is not proof that a write failed and why this design does not promise universal exactly-once execution.

**Checkpoint:** evidence and review for T019 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T020 - Finish the employee review and approval experience

**Milestone:** M4 | **Dependencies:** T018 | **Requirements:** FR08, FR09, FR10

**Required for:** Sandbox workflow MVP (and complete portfolio)

**Planned files:** `ui/app.py`, `src/commerce_support/api/proposals.py`, `src/commerce_support/api/runs.py`.

**Acceptance behaviors:**
- Agent and separate manager complete the case, source review, approval, and execution journey; the proposer sees no approve/execute controls, and the backend rejects those calls anyway.
- Reject/revise, expiry, no-stock, and reconciliation statuses are visibly distinct.
- The UI says request created only after confirmation and never claims shipment or sends customer email.

**Focused test:** `tests/e2e/test_replacement_journey.py`. After creation, run `uv run pytest tests/e2e/test_replacement_journey.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Human review UX, stateful UI, end-to-end tests, truthful status.

**Teach-back:** Explain which UI controls help users and which backend checks actually enforce safety.

**Checkpoint:** evidence and review for T020 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T021 - Expand regression, safety, and locked evaluation sets

**Milestone:** M5 | **Dependencies:** T019, T020 | **Requirements:** FR11, NFR01, NFR02, NFR03

**Required for:** Complete portfolio only

**Planned files:** `evals/development.jsonl`, `evals/acceptance_locked.jsonl`, `evals/manifest.json`, `tests/security/`.

**Acceptance behaviors:**
- There are 60 reviewed development and 120 separately frozen acceptance cases using the documented primary_category enum and counts, including multi-actor and multi-step scenarios.
- Prompt-injection, access control, approval tampering, replays, and failure paths have deterministic release-blocking tests.
- All metrics expose counts/denominators; fake and live outcomes are never mixed without labels.

**Focused test:** `tests/security/test_release_safety.py`. After creation, run `uv run pytest tests/security/test_release_safety.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Red teaming, evaluation splits, rubrics, regression suites.

**Teach-back:** Explain how tuning on a test failure changes what can honestly be claimed about that test set.

**Checkpoint:** evidence and review for T021 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T022 - Instrument redacted traces, usage, and latency

**Milestone:** M5 | **Dependencies:** T015 | **Requirements:** FR11, NFR04, NFR05, NFR07

**Required for:** Complete portfolio only

**Planned files:** `src/commerce_support/observability/traces.py`, `src/commerce_support/observability/redaction.py`, `src/commerce_support/observability/costs.py`.

**Acceptance behaviors:**
- Local runs include versions, timing, usage, safe errors, and trace IDs for each component.
- Hosted LangSmith export is opt-in and passes an allowlist/redaction test, building on the T002 log filter, before export.
- Cost reports include retries/failures in the numerator and use a dated price basis or explicitly report tokens only.

**Focused test:** `tests/unit/test_observability.py`. After creation, run `uv run pytest tests/unit/test_observability.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** LangSmith, observability, redaction, cost accounting, profiling.

**Teach-back:** Given a slow failed case, identify whether retrieval, provider, or tool latency dominated and what evidence supports that diagnosis.

**Checkpoint:** evidence and review for T022 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T023 - Train and benchmark the classical ticket router

**Milestone:** M5 | **Dependencies:** T007 | **Requirements:** FR12, NFR03, NFR06

**Required for:** Complete portfolio only

**Planned files:** `notebooks/01_ticket_eda.ipynb`, `src/commerce_support/ml/train.py`, `src/commerce_support/ml/predict.py`, `evals/routing.py`.

**Acceptance behaviors:**
- The label guide covers six intents; grouped splits prevent template/conversation leakage.
- TF-IDF is fit on training data only; macro-F1, per-class metrics, and confusion matrix include all label supports.
- An LLM comparison uses the same held-out initial messages and the challenge slice, only within an approved budget (otherwise reported as not measured); the result decides whether to use or simply document the baseline.
- Every record names its generator; a hand-written challenge slice of at least 60 messages is reported separately from the generated test split.

**Focused test:** `tests/unit/test_routing_pipeline.py`. After creation, run `uv run pytest tests/unit/test_routing_pipeline.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** pandas, EDA, scikit-learn, TF-IDF, logistic regression, ML evaluation.

**Teach-back:** Explain data leakage, macro versus weighted F1, and why a simple classifier might be preferable to a larger model.

**Checkpoint:** evidence and review for T023 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T024 - Run measured retrieval, prompt, and model comparisons

**Milestone:** M5 | **Dependencies:** T012, T021, T022, T023 | **Requirements:** FR04, FR11, FR12, NFR03, NFR05

**Required for:** Complete portfolio only

**Planned files:** `evals/compare.py`, `reports/experiments/`, `reports/model_card.md`.

**Acceptance behaviors:**
- Every comparison fixes the dataset and records one main changed variable plus model/prompt/index versions.
- Baseline and candidate reports include quality, latency, cost, failure examples, and a keep/reject decision.
- No paid run exceeds the approved cap; insufficient budget is reported as unmeasured, not estimated success.

**Focused test:** `tests/unit/test_experiment_manifest.py`. After creation, run `uv run pytest tests/unit/test_experiment_manifest.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Ablation, experiment tracking, model selection, cost-quality tradeoffs.

**Teach-back:** Defend one improvement and one rejected change using measured results rather than framework popularity.

**Checkpoint:** evidence and review for T024 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T025 - Replace local identity and harden privacy boundaries

**Milestone:** M6 | **Dependencies:** T020, T022 | **Requirements:** FR14, NFR01, NFR07

**Required for:** Complete portfolio only

**Planned files:** `src/commerce_support/auth/oidc.py`, `src/commerce_support/auth/permissions.py`, `src/commerce_support/config.py`.

**Acceptance behaviors:**
- OIDC signature, issuer, audience, expiry, tenant mapping, and current roles are validated; tests use a locally generated key and JWKS fixture, not a live identity provider.
- Development identity is rejected in nonlocal deployment settings; role revocation blocks execution of old approvals.
- Secrets and raw personal data do not enter Git, error responses, or hosted trace payloads.

**Focused test:** `tests/security/test_oidc_and_privacy.py`. After creation, run `uv run pytest tests/security/test_oidc_and_privacy.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** OIDC, JWT validation, RBAC, privacy, deployment security.

**Teach-back:** Explain authentication versus authorization, token validation, and why an old approval must not bypass revoked permissions.

**Checkpoint:** evidence and review for T025 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T026 - Move ingestion and recovery into durable jobs

**Milestone:** M6 | **Dependencies:** T019, T022 | **Requirements:** FR03, FR13, NFR02, NFR04

**Required for:** Complete portfolio only

**Planned files:** `src/commerce_support/jobs/app.py`, `src/commerce_support/jobs/ingestion.py`, `src/commerce_support/jobs/reconciliation.py`.

**Acceptance behaviors:**
- Celery/Redis jobs keep the existing 202 job contract and persisted status; retries are bounded to three total attempts for ingestion.
- Worker interruption does not activate incomplete documents or duplicate replacement effects.
- Permanent or exhausted failures move to quarantined with diagnostics and require deliberate retry or repair.

**Focused test:** `tests/integration/test_job_recovery.py`. After creation, run `uv run pytest tests/integration/test_job_recovery.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Celery, Redis, queues, retry/backoff, background processing.

**Teach-back:** Explain at-least-once delivery and why a durable queue still requires idempotent job handlers.

**Checkpoint:** evidence and review for T026 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T027 - Containerize, deploy, and document recovery

**Milestone:** M6 | **Dependencies:** T025, T026 | **Requirements:** FR14, NFR04, NFR06, NFR07

**Required for:** Complete portfolio only

**Planned files:** `Dockerfile`, `compose.yaml`, `.github/workflows/ci.yml`, `docs/runbooks/DEPLOYMENT.md`, `docs/runbooks/RESTORE.md`.

**Acceptance behaviors:**
- API/UI/worker/database/broker start from documented pinned configuration with private database access.
- CI runs offline checks and database tests; hosted deployment is authenticated and sandbox-only.
- Health/readiness, migration backup, restore to an isolated database, and application rollback have recorded evidence.

**Focused test:** `tests/integration/test_deployment_smoke.py`. After creation, run `uv run pytest tests/integration/test_deployment_smoke.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Docker, CI/CD, migrations, deployment, backup/restore.

**Teach-back:** Explain the difference between a container image, a running container, a database volume, and a backup.

**Checkpoint:** evidence and review for T027 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T028 - Exercise concurrent load, restarts, and spending limits

**Milestone:** M6 | **Dependencies:** T027 | **Requirements:** FR07, FR09, NFR02, NFR05, NFR08

**Required for:** Complete portfolio only

**Planned files:** `scripts/load_cases.py`, `tests/integration/test_chaos_recovery.py`, `reports/performance.md`.

**Acceptance behaviors:**
- At least 100 attempts at five concurrent sessions report p50/p95, failures, machine/network, and fake/live mode.
- Crash-after-commit, broker loss, provider timeouts, and paused-approval restart preserve safe outcome semantics.
- Configured token/call/spend caps stop runaway requests; no universal uptime or throughput claim is made.
- Per-principal rate limits on run, decision, and execute endpoints return 429 RATE_LIMITED without side effects; limits come from configuration.

**Focused test:** `tests/integration/test_chaos_recovery.py`. After creation, run `uv run pytest tests/integration/test_chaos_recovery.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Load testing, fault injection, SLOs, budgets, resilience.

**Teach-back:** Explain a p95 result, distinguish a latency target from a timeout, and show what happens after an ambiguous write.

**Checkpoint:** evidence and review for T028 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T029 - Freeze and review the final release evidence

**Milestone:** M7 | **Dependencies:** T024, T028 | **Requirements:** FR11, FR12, FR14, NFR01, NFR02, NFR03, NFR04, NFR05, NFR06, NFR07, NFR08

**Required for:** Complete portfolio only

**Planned files:** `reports/final_evaluation.md`, `reports/data_card.md`, `reports/model_card.md`, `reports/release_checklist.md`.

**Acceptance behaviors:**
- The report states every target as met, missed, or not measured with a supporting artifact and denominator.
- Safety tests pass, remaining limitations are visible, and locked-data contamination status is explicit.
- A clean checkout reproduces the documented deterministic suite and locates all report artifacts.

**Focused test:** `tests/contract/test_release_manifest.py`. After creation, run `uv run pytest tests/contract/test_release_manifest.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Release review, reproducibility, data/model cards, technical communication.

**Teach-back:** Explain the strongest claim your evidence supports and one important claim it does not support.

**Checkpoint:** evidence and review for T029 go in `learning/evidence/`; update only this task's record after inspecting the evidence.

## T030 - Prepare the portfolio demo and engineering narrative

**Milestone:** M7 | **Dependencies:** T029 | **Requirements:** FR14, NFR06

**Required for:** Complete portfolio only

**Planned files:** `README.md`, `reports/demo_script.md`, `reports/architecture_walkthrough.md`, `reports/failure_casebook.md`.

**Acceptance behaviors:**
- Demo shows a grounded answer, an approved request, an unsafe request blocked, and a recovered failure.
- The narrative includes measured comparisons, ten failure/correction examples, limitations, and setup instructions.
- Claims of business savings, real-user accuracy, or production certification are absent unless separately evidenced.

**Focused test:** `tests/e2e/test_portfolio_demo.py`. After creation, run `uv run pytest tests/e2e/test_portfolio_demo.py -q`; expected final outcome: pass. Save the actual output, including failures before the fix.

**Learning focus:** Portfolio storytelling, engineering tradeoffs, demo design, interview readiness.

**Teach-back:** Give a five-minute architecture explanation and diagnose one failure without relying on the coach to supply the reasoning.

**Checkpoint:** evidence and review for T030 go in `learning/evidence/`; update only this task's record after inspecting the evidence.
