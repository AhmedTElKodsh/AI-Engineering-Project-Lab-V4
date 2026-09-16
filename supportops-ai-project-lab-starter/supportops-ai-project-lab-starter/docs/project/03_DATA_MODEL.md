# Data model and invariants

> **Curriculum scope note:** This file describes destination product architecture and engineering options. Implement only the slice justified by the active J0-J5 mini-release; it is not a day-one checklist.

**Status:** logical design, not deployed migrations. Internal identifiers are UUIDs; human order references such as `1042` are scoped external references. Store instants in UTC with timezone-aware values. Derive calendar-day eligibility using the store's configured IANA timezone.

## Contents

1. Entity model
2. Core constraints and indexes
3. Proposal, approval, and transaction details
4. Knowledge lifecycle
5. Data fixtures and privacy

## 1. Entity model

| Entity | Essential fields | Relationships and behavior |
|---|---|---|
| `tenants` | `id`, `name`, `business_timezone` | Seed two synthetic tenants; timezone initially Africa/Cairo |
| `users` | `id`, `tenant_id`, `subject`, `roles`, `active` | Subject is mapped from trusted authentication; roles are not accepted from model output |
| `customers` | `id`, `tenant_id`, `external_reference`, `display_alias` | Synthetic aliases only; no real email or address required |
| `orders` | `id`, `tenant_id`, `customer_id`, `external_reference`, `status`, `delivered_at`, `version` | External reference unique within a tenant; optimistic version increments on material changes |
| `order_lines` | `id`, `tenant_id`, `order_id`, `sku`, `category`, `quantity` | MVP action supports quantity one; unsupported cases still exist as fixtures |
| `inventory` | `tenant_id`, `sku`, `available_quantity`, `version` | Quantity nonnegative; atomic reservation at execution |
| `shipments` | `id`, `tenant_id`, `order_id`, `status`, `delivered_at`, `version` | Latest read timestamp is returned with the factual result |
| `cases` | `id`, `tenant_id`, `created_by`, `customer_id`, `status`, `version`, `created_at`, `updated_at` | Customer reference may be initially unknown; case access is tenant-scoped |
| `messages` | `id`, `tenant_id`, `case_id`, `role`, `body`, `created_at` | Customer text, employee text, and draft responses are distinguished; none constitutes approval |
| `policy_versions` | `id`, `tenant_id`, `policy_key`, `version`, `status`, `effective_from`, `effective_to`, `activated_at`, `rules_json`, `checksum` | Version groups document evidence with administrator-reviewed deterministic rules |
| `documents` | `id`, `tenant_id`, `policy_version_id`, `source_name`, `mime_type`, `checksum`, `status`, `created_at` | MVP allows uploaded files only; exact duplicate ingestion does not create duplicate searchable chunks |
| `chunks` | `id`, `tenant_id`, `document_id`, `section_id`, `locator`, `text`, `token_count`, `embedding`, `embedding_model`, `embedding_dimension`, `index_version` | Locator is a page/section/paragraph reference; section ID is stable for evaluation |
| `runs` | `id`, `tenant_id`, `case_id`, `status`, `prompt_version`, `model_id`, `index_version`, `started_at`, `finished_at`, `usage_json`, `error_code` | Local metadata exists even when hosted tracing is disabled |
| `proposals` | `id`, `tenant_id`, `case_id`, `proposer_id`, `action`, `parameters_json`, `payload_hash`, `order_version`, `policy_version_id`, `status`, `expires_at`, `created_at` | Parameters are immutable; revising creates a new row |
| `approvals` | `id`, `tenant_id`, `proposal_id`, `approver_id`, `decision`, `payload_hash`, `decided_at` | At most one effective approval decision per proposal; approver differs from proposer |
| `action_executions` | `id`, `tenant_id`, `proposal_id`, `idempotency_key`, `payload_hash`, `status`, `downstream_reference`, `last_error`, `updated_at` | Replay and reconciliation ledger; not a substitute for downstream idempotency |
| `replacement_requests` | `id`, `tenant_id`, `order_line_id`, `proposal_id`, `status`, `created_at` | At most one active or succeeded replacement for a line in this demo |
| `outbox_events` | `id`, `tenant_id`, `execution_id`, `event_type`, `payload_json`, `attempts`, `next_attempt_at`, `status` | Portfolio adapter dispatch/reconciliation intent; deduplicated by execution and event type |
| `audit_events` | `id`, `tenant_id`, `actor_id`, `case_id`, `proposal_id`, `action`, `result`, `request_id`, `created_at` | Append-only through application role; redact payloads; no secrets |
| `ingestion_jobs` | `id`, `tenant_id`, `document_checksum`, `status`, `attempt_count`, `error_code`, `created_at`, `finished_at` | States: queued, running, succeeded, failed; permanent failures are quarantined |

LangGraph checkpoint tables are managed by the selected durable checkpointer. Maintain an application-owned mapping from `(tenant_id, case_id)` to graph thread identity. Do not expose raw checkpoint lookup without authorization.

## 2. Core constraints and indexes

Every tenant-owned primary identifier is paired with `tenant_id` in foreign-key relationships or equivalently enforced repository constraints; a reference must not link two tenants. Repository methods require a trusted principal. Add PostgreSQL row-level security only with an explicit migration/test decision; do not claim it exists merely because repository filtering exists.

Create unique indexes on `(tenant_id, external_reference)` for orders; `(tenant_id, sku)` for inventory; `(tenant_id, idempotency_key)` for executions; and the demo's active/completed replacement uniqueness. Add checks for nonnegative stock, positive order quantities, nonempty action parameters, and valid enum states. Index cases by tenant and updated time; chunks by tenant/document/version; pending outbox jobs by state and next attempt.

Use exact vector search as the baseline on a small corpus. Add approximate indexing only after checking recall against exact search. Metadata/tenant filtering must apply within retrieval, not after returning private chunks to the model. The pgvector project supports exact and approximate vector search and describes combining vector retrieval with PostgreSQL full-text search. [S2]

## 3. Proposal, approval, and transaction details

Canonical proposal parameters contain `order_line_id`, `sku`, `quantity` fixed to 1, and `reason_code` fixed to `damaged_item`. Hash a JSON representation with sorted keys, compact separators, UTF-8 encoding, and no floating-point values. Include action, proposal ID, tenant ID, case ID, proposer ID, order version, and policy version ID in the signed-off envelope. The server creates the hash; the model cannot provide a trusted hash.

The approval binds to that hash. Check manager role, tenant, separate approver, expiry, and unmodified proposal state before accepting it. At execution, refresh the actor's current authorization and business facts. A policy or order-version change yields `STALE_PROPOSAL`, not a best-effort write. A new proposal requires a new approval.

For the local sandbox, one database transaction reserves stock and writes the replacement, execution result, proposal state, and audit event. Unique constraints arbitrate concurrent requests. Treat a uniqueness violation as a replay/duplicate condition and return the existing authorized result when appropriate; do not expose another tenant's identifiers.

For network writes, keep the intent/result ledger and reconcile ambiguous outcomes. No distributed exactly-once claim is made. The intended guarantee is deduplicated effects for the implemented adapters under the stated idempotency assumptions.

## 4. Knowledge lifecycle

A version moves from `staging` to `active` only after extraction, chunking, embedding, rules validation, and index checks succeed. Atomic activation retires the previous active version of the same policy key. A failed import remains nonsearchable. Re-ingesting the same content and version is a no-op with the original job/document reference.

Retiring a document removes it from new retrieval but preserves evidence needed to explain past runs. A privacy deletion operation, when added for real data, must purge content from source storage, chunks, embeddings, caches, and traces according to the chosen retention policy; simple retirement is not erasure. The MVP uses synthetic content only.

Keep the embedding model ID, revision, dimensionality, preprocessing, and index version together. Changing embedding dimension requires a separate index/migration and full re-embedding, not mixing incompatible vectors.

## 5. Data fixtures and privacy

The relevant J-stage creates repeatable synthetic fixtures: a valid replacement, missing order reference, non-delivered order, exact seven-day boundary, eight-day case, empty stock, an existing replacement, mismatched tenant, and a policy change. Fixtures use fixed times and a frozen clock. Include a daylight-saving/calendar-boundary case to ensure local-date arithmetic is tested.

`examples/evaluation_seed.jsonl` contains development scenarios only. It is not training data or a held-out acceptance set. Keep generated routing templates grouped when splitting; records sharing a conversation, paraphrase template, or source case must stay in one partition.
