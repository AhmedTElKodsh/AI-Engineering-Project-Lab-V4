# Architecture and component design

> **Curriculum scope note:** This file describes destination product architecture and engineering options. Implement only the slice justified by the active J0-J5 mini-release; it is not a day-one checklist.

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
Streamlit UI ---> FastAPI: authentication, schema validation, rate limits
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

Knowledge upload -> ingestion service -> optional worker (later operational-depth trigger)
                                      -> versioned chunks + embeddings
Redis: job broker and short-lived coordination; not approval truth
PostgreSQL: cases, proposals, approvals, audit, durable graph checkpoints
```

Customer text and retrieved passages are untrusted content. They cannot supply actor identity, grant roles, change system instructions, activate policies, or approve actions. The principal comes from validated authentication. Every application/repository/tool method accepts the trusted principal separately from model-generated arguments.

A source URL is not an instruction to fetch arbitrary network content. MVP ingestion accepts uploaded bytes only. Future URL ingestion would need an allowlist, redirect limits, private-network blocking, and separate SSRF tests.

## 3. Request and ingestion flows

### Case turn

Validate actor and case access; append a message; create a run; analyze the ticket; obtain authorized operational facts; retrieve applicable policy; validate rules; generate a grounded draft; create a proposal when eligible; pause for review. A revision creates a new proposal. Execution rechecks current facts and authorization, performs the sandbox transaction, and produces a result-aware response.

### Ingestion

Authorize a knowledge administrator; validate MIME type and size; compute checksum; extract text and stable source locators; split by section; embed; validate an entire pending version; atomically activate it and retire the previous version. An incomplete version is never searchable. Keep `effective_from`, `effective_to`, `activated_at`, and version IDs distinct. A policy document and its deterministic rule configuration share a published policy version.

Use text-based PDF parsing only initially; encrypted, scanned, or malformed PDFs return a clear unsupported-input result. OCR is an extension with separate quality checks. Do not execute embedded content.

## 4. State and execution safety

### Case workflow states

`new -> analyzing -> awaiting_information | awaiting_approval | escalated | resolved | failed`

`awaiting_information` returns to `analyzing` after a new employee-entered message. `awaiting_approval` can return to analysis after rejection/revision, enter `executing` after validated approval, or become `failed` after a controlled permanent failure. `executing` becomes `resolved`, `reconciliation_required`, or `failed`. Only a confirmed action result or a completed read-only resolution leads to `resolved`.

### Proposal states

`pending -> approved | rejected | expired | superseded`

`approved -> executing -> succeeded | reconciliation_required | failed`

The proposal is immutable except status/audit metadata. Bind the approval to a hash of canonical action parameters, proposal ID, tenant, case, proposer, order version, and policy version. The approval response cannot contain replacement parameters. Check expiry and versions immediately before execution. Retrying graph nodes must not replay a non-idempotent write.

LangGraph interrupts require a checkpointer and stable thread identifier; code preceding an interrupt may run again on resume, so keep irreversible side effects out of that region. Use a durable production checkpointer and authorize every resume request. [S1]

### Local sandbox transaction

Lock proposal and relevant inventory/order-line rows in a consistent order. Revalidate approval and stock. Enforce a unique active/completed replacement per `(tenant_id, order_line_id)` and unique idempotency key per tenant. In one transaction: create replacement request, reserve one stock unit, mark outcome, and append audit. If a response is lost after commit, lookup by key returns the original result.

### External adapter extension within portfolio hardening

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

J0 proves the first model boundary. J1-J2 establish structured intake and transfer. J3 adds retrieval before generation. J4 adds scoped reads, bounded tools and the approved local write. J5 packages one reproducible release. Persistent databases, durable graph recovery, ML comparison and operations are selected depth work when a measured limitation or target role justifies them.

Do not introduce Kubernetes, a second vector database, or multi-agent collaboration without a recorded need. Keep sync functions when appropriate; use async I/O for concurrent network-bound calls without pretending CPU-heavy embedding work becomes faster merely by declaring it async. Choose worker offloading only when ingestion becomes heavy enough to justify a background-job boundary.

Sources: see `12_SOURCES_AND_VERSION_POLICY.md`, especially S1, S2, S3, and S4. Version-pin integrations at the task that introduces them and verify current APIs rather than copying an old import path.
