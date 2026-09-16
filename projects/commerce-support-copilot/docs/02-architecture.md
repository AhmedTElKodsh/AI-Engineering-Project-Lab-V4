# Architecture and component design

**Status:** proposed target architecture; introduce components by milestone, not all at once.

## Contents

1. Architecture choice
2. Runtime and trust boundaries
3. Request and ingestion flows
4. State and execution safety
5. Planned code organization
6. Implementation sequence and alternatives

## 1. Architecture choice

Use a modular Python application with FastAPI at the boundary. PostgreSQL owns transactional business data, policy metadata, document chunks, and vector search. A configurable model adapter isolates vendor-specific APIs. LangChain integrations are selective; LangGraph owns the bounded, persistent case workflow after the basic functions have been implemented and tested directly. Streamlit is the employee UI. Celery and Redis are added for ingestion and recovery jobs in the hardening milestone.

Start with a fake model and fake commerce adapter. Use the hosted model only in explicitly authorized live experiments. Keep model credentials on the backend. Use Sentence Transformers for initial local embeddings and optional reranking. Use LangSmith only after redaction and external-trace opt-in; keep a local JSON trace export available.

## 2. Runtime and trust boundaries

```text
Employee browser
    |
    v
Streamlit UI ---> FastAPI: authentication, schema validation, rate limits (NFR08)
                         |
                         v
                 case application service
                    |             |
                    v             v
               LangGraph     authorization + rules
                    |             |
             model adapter   read/write tool services
                    |             |
                    +---- PostgreSQL + pgvector
                    |             |
                    |        sandbox commerce adapter
                    v
           redacted trace/event sink

Knowledge upload -> 202 + job ID -> ingestion service (in-process until M6, Celery worker from M6)
                                      -> versioned chunks + embeddings
Redis: job broker and short-lived coordination; not approval truth
PostgreSQL: cases, proposals, approvals, audit, jobs, durable graph checkpoints
Redaction filter on every log handler from M0 (T002); hosted trace export only at M5 (T022)
```

Customer text and retrieved passages are untrusted content. They cannot supply actor identity, grant roles, change system instructions, activate policies, or approve actions. The principal comes from validated authentication. Every application/repository/tool method accepts the trusted principal separately from model-generated arguments.

A source URL is not an instruction to fetch arbitrary network content. MVP ingestion accepts uploaded bytes only. Future URL ingestion would need an allowlist, redirect limits, private-network blocking, and separate SSRF tests.

## 3. Request and ingestion flows

### Case turn

Validate actor, case access, and the per-principal rate limit; append a message; create a run; analyze the ticket; obtain authorized operational facts; bind the case to the resolved order and resolve the product mention to one order line in code; retrieve applicable policy; validate rules; generate a grounded draft; create a proposal when eligible; pause for review. A revision creates a new proposal. Execution rechecks current facts and authorization, performs the sandbox transaction, and produces a result-aware response. The allowed status values and transitions are defined in §4.

### Ingestion

Authorize a knowledge administrator; create an ingestion job and return its ID; validate MIME type and size; compute checksum; extract text and stable source locators; split by section; embed; validate an entire `staging` version; atomically activate it and retire the previous version. An incomplete version is never searchable. Keep `effective_from`, `effective_to`, `activated_at`, and version IDs distinct. A policy document and its deterministic rule configuration share a published policy version.

Use text-based PDF parsing only initially; encrypted, scanned, or malformed PDFs return a clear unsupported-input result. OCR is an extension with separate quality checks. Do not execute embedded content.

## 4. State and execution safety

The two tables below are the single source of truth for status values and transitions. Implement them as explicit transition functions with unit tests (T004 for the enums, T015-T018 for the transitions). Any transition not listed is rejected.

### Case workflow states

`new`, `analyzing`, `awaiting_information`, `awaiting_approval`, `executing`, `reconciliation_required`, `escalated`, `resolved`, `failed`

| From | Event | To | Actor / guard |
|---|---|---|---|
| `new` | run started | `analyzing` | support role; `expected_case_version` matches |
| `analyzing` | required fact missing | `awaiting_information` | rules/analysis result |
| `analyzing` | eligible and proposal created | `awaiting_approval` | proposal service; case bound to one order |
| `analyzing` | ineligible, manual review, no stock, conflicting evidence | `escalated` | deterministic rules |
| `analyzing` | read-only question answered with valid evidence | `resolved` | grounded draft passed validation |
| `analyzing` | budget exceeded or permanent typed failure | `failed` | run limits; case state preserved |
| `awaiting_information` | new employee-entered message | `analyzing` | support role |
| `awaiting_approval` | proposal `rejected`, `revision_requested`, `expired`, or `invalidated` | `analyzing` | a new run must create any new proposal |
| `awaiting_approval` | execution accepted for an approved proposal | `executing` | manager, not proposer; guards in BR06/BR07 |
| `executing` | local transaction or downstream result confirmed | `resolved` | confirmed result only |
| `executing` | downstream outcome unknown | `reconciliation_required` | persisted intent exists |
| `executing` | confirmed permanent failure with no effect | `failed` | typed error |
| `reconciliation_required` | lookup confirms success | `resolved` | reconciliation job or manual action |
| `reconciliation_required` | lookup confirms no effect | `failed` | never auto-retry an ambiguous write |
| `escalated`, `failed` | employee reopens with new message | `analyzing` | support role; new run ID |

### Proposal states

`pending`, `approved`, `rejected`, `revision_requested`, `expired`, `invalidated`, `superseded`, `executing`, `succeeded`, `reconciliation_required`, `failed`

| From | Event | To | Guard |
|---|---|---|---|
| `pending` | manager decision `approve` | `approved` | same tenant, active manager, not proposer, before `expires_at`, hash matches |
| `pending` | manager decision `reject` | `rejected` | same guards as `approve`; terminal |
| `pending` | manager decision `revise` | `revision_requested` | comment required |
| `pending`, `revision_requested` | a new proposal is created for the same case | `superseded` | new row references the old one |
| `pending`, `approved` | clock passes `expires_at` before execution starts | `expired` | checked lazily on every read/decision/execute |
| `pending`, `approved` | active policy version or order version changed | `invalidated` | checked on decision and execute; error `STALE_PROPOSAL` |
| `approved` | execute accepted | `executing` | revalidated role, tenant, expiry, versions, stock, duplicate state |
| `executing` | confirmed | `succeeded` | |
| `executing` | ambiguous downstream outcome | `reconciliation_required` | |
| `executing` | confirmed failure with no effect | `failed` | |
| `reconciliation_required` | lookup confirms success / no effect | `succeeded` / `failed` | |

The proposal is immutable except status/audit metadata. Bind the approval to a SHA-256 hash of the canonical approval envelope (see `03-data-model.md` §3): canonical action parameters, proposal ID, tenant, case, proposer, order version, and policy version. The approval request carries that hash and cannot contain replacement parameters. Check expiry and versions immediately before execution. Retrying graph nodes must not replay a non-idempotent write.

LangGraph interrupts require a checkpointer and stable thread identifier; code preceding an interrupt may run again on resume, so keep irreversible side effects out of that region. Use a durable production checkpointer and authorize every resume request. [S1]

### Local sandbox transaction

Lock proposal and relevant inventory/order-line rows in a consistent order (proposal, then order line, then inventory). Revalidate approval and stock. Enforce a unique active/succeeded replacement per `(tenant_id, order_line_id)`, one execution per `(tenant_id, proposal_id)`, and a unique idempotency key per tenant. In one transaction: create replacement request, reserve one stock unit, mark outcome, and append audit. If a response is lost after commit, lookup by key returns the original result.

### External adapter extension (portfolio level, T019)

This subsection is not required for the sandbox workflow MVP; see the backlog's **Required for** field.

A network write cannot be assumed atomic with the local database. Persist an action-intent/outbox record before dispatch, call the downstream idempotent endpoint with the same key, and record its outcome. On timeout, query downstream status before retrying. If downstream offers neither idempotency nor lookup, do not automatically retry an ambiguous write; require manual reconciliation. Redis locks and graph checkpoints are not substitutes for database constraints or downstream idempotency.

## 5. Planned code organization

These paths are a design map, not files already implemented.

```text
src/commerce_support/
  api/                 # HTTP routes, dependency injection, error translation
  auth/                # trusted principal, permissions, OIDC adapter
  cases/               # case/messages service and schemas
  knowledge/           # extraction, chunks, versions, retrieval, citations
  ai/                  # provider interface, fake adapter, prompts, usage
  workflow/            # state schema, graph nodes, resume coordination
  commerce/            # order reads, deterministic rules, sandbox adapter
  actions/             # immutable proposals, approvals, execution, outbox
  observability/       # redaction, traces, usage/cost accounting
  jobs/                # ingestion and reconciliation worker tasks
  ml/                  # routing data, training, artifacts, serving
  db/                  # models, sessions, migrations integration
  config.py            # validated environment configuration
  main.py              # application factory
ui/app.py              # employee console using API only
migrations/            # Alembic revisions
prompts/               # versioned extraction and drafting templates
scripts/               # seeding and experiment entrypoints
notebooks/             # exploration only, not production business logic
tests/unit/
tests/integration/
tests/contract/
tests/security/
tests/e2e/
evals/                 # separate development and locked test manifests
```

Use SQLAlchemy/Alembic for database access and migrations, pytest for tests, Ruff for lint/format checks, type checking for public boundaries, Docker Compose for the completed local system, and GitHub Actions for CI. These are project selections, not universal employer requirements.

## 6. Implementation sequence and alternatives

M0 creates a tiny service and reproducible environment. M1 teaches direct provider boundaries before frameworks. M2 adds PostgreSQL and retrieval. M3 adds tools and graph persistence. M4 adds approval and a safe write. M5 measures improvements and classical ML. M6 introduces durable jobs, deployment identity, and operations. M7 freezes evidence.

Do not introduce Kubernetes, a second vector database, or multi-agent collaboration without a recorded need. Keep sync functions when appropriate; use async I/O for concurrent network-bound calls without pretending CPU-heavy embedding work becomes faster merely by declaring it async. Choose worker offloading for heavy ingestion at M6.

Sources: see `12-sources-and-version-policy.md`, especially S1, S2, S3, and S4. Version-pin integrations at the task that introduces them and verify current APIs rather than copying an old import path.
