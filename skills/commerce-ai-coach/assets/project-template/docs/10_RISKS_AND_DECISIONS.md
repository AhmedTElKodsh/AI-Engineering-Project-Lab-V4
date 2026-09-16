# Risks, assumptions, and architecture decisions

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
| R16 | Two curricula for one product | The SupportOps J0-J5 starter and this M0-M7 plan are both opened by an assistant | V4 root README names this plan as the active track; the SupportOps starter is marked reference-only; progress lives only in `learning/progress.json` |
| R17 | Duplicated skill copies drift | The standalone skill, the repository-installed copy, and the template snapshot are edited separately | `tools/verify_v4.py` compares them; edit the standalone skill first and re-copy |

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

### ADR-009 - Delivery time comes only from shipments

`shipments.delivered_at` (latest delivered shipment) is the only delivery source for BR03. `orders` has no delivery timestamp, which removes a second, possibly conflicting, source of truth.

### ADR-010 - The model never emits internal IDs

Extraction returns an order reference and a product mention. Code resolves them to the order and order line within the principal's tenant, binds the order to the case, and rejects proposals for lines outside that order.

### ADR-011 - Release levels are task lists, not milestone ranges

Each task declares `required_for` (`read_only_demo`, `sandbox_mvp`, or `portfolio`). T012 (hybrid retrieval) and T019 (external-write reconciliation) are portfolio work even though they sit in M2 and M4.

### ADR-007 - Evidence lives in the repository

Use `learning/progress.json`, evidence files, and session notes instead of assumed conversation memory. The standalone skill's bundled snapshot initializes new workspaces only. Never overwrite active progress from the template.

### ADR-008 - Python compatibility baseline

Target Python 3.13 for the application. As of 2026-09-15, Python 3.12 accepts security fixes only (no new binary releases), while 3.13 and 3.14 are in bugfix support. 3.13 is the conservative choice for the ML and embedding stack; move to 3.14 once T001/T010 confirm wheels for every dependency. Verify dependency support at T001 and when adding integrations. Record an approved change if current dependencies require a different maintained version. Skill helper scripts use only the standard library and require Python 3.10 or newer.

## Resolved scope assumptions

English-only text experience; small-appliance replacement; quantity one; two synthetic tenants; Africa/Cairo business dates; fifteen-minute proposal expiry counted from creation; any non-proposer manager may execute an approved proposal; no automated customer sending. These choices are explicit so the coach need not ask the learner to redesign the domain at every session.

## Decisions deferred to the relevant task

Actual operating system and installed tooling: T001. Hosted model ID, SDK, and authorized budget: T005. Embedding model/revision and license: T010. Identity provider (tests use a local JWKS fixture) and host with verified current pricing: T025/T027. These are environment choices, not missing product behavior. The learner can complete earlier offline tasks without them.

## Change-control procedure

Record the proposed change and reason. Identify affected FR/NFR IDs, contracts, tests, tasks, and budget. Add a short decision entry. Keep IDs stable where possible, version the planning baseline, and update both `docs/09_BACKLOG.md` and `learning/backlog.json`. Preserve completed evidence; rerun affected regressions instead of marking old claims current without verification.
