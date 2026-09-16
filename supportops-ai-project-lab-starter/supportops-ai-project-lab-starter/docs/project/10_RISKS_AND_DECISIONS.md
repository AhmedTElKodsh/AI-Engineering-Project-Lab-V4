# Risks, assumptions, and architecture decisions

> **Curriculum scope note:** This file describes destination product architecture and engineering options. Implement only the slice justified by the active J0-J5 mini-release; it is not a day-one checklist.

**Decision owner:** learner. **Status:** initial choices, not measured findings.

## Risk register

| ID | Risk | Trigger / impact | Mitigation and owner action |
|---|---|---|---|
| R01 | Scope inflation | Multiple agents, providers, and workflows before one case works | Keep one workflow; new feature requires changed requirements and evaluation cases |
| R02 | Valid but false model output | Wrong order/evidence or invented facts | Validate schema, resolve IDs, inspect support, apply deterministic rules |
| R03 | Prompt injection | Customer/document text requests tools or authority | Treat content as untrusted; narrow tool allowlist; server-owned principal/approval |
| R04 | Cross-tenant disclosure | Missing filters in retrieval, resume, or repositories | Test each boundary with two tenants; fail closed before model context |
| R05 | Stale/forged approval | Edited parameters, policy update, expiry, revoked role | Bind immutable hash and versions; reauthorize/revalidate at execution |
| R06 | Duplicate or ambiguous write | Retry after timeout or concurrent execution | Database constraints, transaction, idempotency key, outbox/reconciliation |
| R07 | Evaluation leakage | Same templates or holdout examples used in training/prompts | Grouped splits; locked manifests; explicitly report contamination |
| R08 | Synthetic-data overclaim | High demo scores interpreted as real-world accuracy | Data card, separate real-user pilot, visible limitations |
| R09 | Spend surprise | Unbounded retries, large prompts, hosted judge calls | Fake-first defaults; user-approved caps; metered usage; enforced run limits |
| R10 | Provider/framework churn | Old import paths or removed model IDs | Verify primary docs when introduced; pin tested versions; contract tests |
| R11 | Local hardware constraints | Embeddings/reranker exhaust memory | Smaller verified model or omit reranker; record hardware and tradeoff |
| R12 | Trace leakage | Raw data or secrets exported to hosted tooling | Allowlisted/redacted events; opt-in export; secret scanning |
| R13 | False learning progress | Passing generated code is mistaken for understanding | Separate software status and mastery; evidence plus teach-back |
| R14 | Lost context between sessions | Coach relies on chat memory or stale template | Repository progress, session handoff, authoritative current docs |
| R15 | Unvalidated coach behavior | Host ignores skill or instructions drift | Run supplied behavioral scenarios in the chosen host; do not equate format validation with behavioral certification |

## Architecture decisions

### ADR-001 - Modular application, not microservices

Choose a modular Python application with a separate worker only when needed. This keeps boundaries visible without requiring service discovery and distributed deployment on day one. Revisit only for a measured scaling or isolation need.

### ADR-002 - PostgreSQL plus pgvector

Keep business data, metadata, and vector retrieval in one database to reduce infrastructure. Establish exact-search and authorization baselines before approximate indexing. A dedicated vector service is an alternative only if corpus/operations measurements justify it.

### ADR-003 - Direct model functions before LangChain/LangGraph

Teach provider calls, typed outputs, and tests before wrapping them. Add LangGraph when state, branching, checkpointing, and approval pause are needed. Avoid redundant orchestration layers.

### ADR-004 - Human approval is application state

Require a separate manager to approve an immutable proposal. Prompts and model-reported approval cannot authorize writes. Backend checks remain mandatory even if the UI hides controls.

### ADR-005 - Fake-first and sandbox-only

No paid account is required for early work. The final demo still uses a sandbox commerce adapter. Hosted LLMs and tracing require explicit data/budget permission. Real refunds and shipping are outside scope.

### ADR-006 - Simple ML baseline is a bounded experiment

Include TF-IDF plus logistic regression to learn supervised evaluation and cost tradeoffs. Do not force it into the product when measured quality does not justify it.

### ADR-007 - Evidence lives in the repository

Use `progress/current.json`, `progress/skills.json`, and append-only `progress/evidence.jsonl` instead of assumed conversation memory. Never overwrite active progress from a template.

### ADR-008 - Python compatibility baseline

Target Python 3.12 for the application as an initial compatibility choice, not a statement that it is the newest release. Verify dependency support when the first application environment is created and again when adding integrations. Record an approved change if current dependencies require a different maintained version. Skill helper scripts use only the standard library and require Python 3.10 or newer.

## Resolved scope assumptions

English-only text experience; small-appliance replacement; quantity one; two synthetic tenants; Africa/Cairo business dates; fifteen-minute approval expiry; no automated customer sending. These choices are explicit so the coach need not ask the learner to redesign the domain at every session.

## Decisions deferred to the relevant task

Actual operating system and installed tooling: J0 environment reconciliation. Hosted model ID, SDK, and authorized budget: J0 when a live call is selected. Embedding model/revision and license: J3. Identity provider and host with verified current pricing: only in a selected deployment extension. These are environment choices, not missing product behavior. The learner can complete earlier offline tasks without them.

## Change-control procedure

Record the proposed change and reason. Identify affected FR/NFR IDs, contracts, tests, tasks, and budget. Add a short decision entry. Keep IDs stable where possible, version the planning baseline, and update the affected J0-J5 curriculum/release contract and any progress capability mapping without renaming the stable J/E/Q identifiers. Preserve completed evidence; rerun affected regressions instead of marking old claims current without verification.
