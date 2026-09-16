# API, schemas, and tool contracts

**Status:** v1 contract design (planning baseline 1.1.0). Generate the implementation's OpenAPI schema from actual FastAPI/Pydantic code and test it against these requirements. Do not claim the design is executable OpenAPI.

## Contents

1. Shared conventions
2. HTTP surface
3. Schemas and interfaces
4. Tool boundary
5. Approval and failure examples

## 1. Shared conventions

Use `/v1`, JSON, UUID internal IDs, UTC ISO-8601 timestamps, and explicit enum values. Authentication supplies `Principal(user_id, tenant_id, roles)` independently of the request body. Return 404 for missing or inaccessible tenant-owned IDs. Return 403 when the caller can see the resource but lacks the required action permission.

Validate with Pydantic models using `extra="forbid"` and appropriate strict constraints (types, lengths, patterns, enums). Pydantic validates shape/types; it does not prove that an order exists or that a citation supports a claim. [S3]

Use this safe error shape:

```json
{
  "error": {
    "code": "STALE_PROPOSAL",
    "message": "The order or policy changed. Prepare a new proposal.",
    "retryable": false,
    "request_id": "req-demo-001"
  }
}
```

Error codes: `INVALID_INPUT`, `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `STALE_PROPOSAL`, `PROPOSAL_EXPIRED`, `DUPLICATE_REPLACEMENT`, `IDEMPOTENCY_CONFLICT`, `OUT_OF_STOCK`, `RATE_LIMITED`, `PROVIDER_UNAVAILABLE`, `INVALID_MODEL_OUTPUT`, and `BUDGET_EXCEEDED`.

An unknown downstream outcome is **not** an error code. It is reported as `ActionResult.status = reconciliation_required` with HTTP 202 (see §2). Logs may contain internal exception details after redaction; client responses do not expose SQL, credentials, or private identifiers.

## 2. HTTP surface

| Method and path | Input / authorization | Successful result | Important failures |
|---|---|---|---|
| `GET /health/live` | No business data | 200 `{"status":"ok"}` | No dependency calls |
| `GET /health/ready` | Deployment health probe | 200 dependencies ready | 503 safe dependency summary |
| `POST /v1/cases` | `CreateCaseRequest`; support role | 201 `CaseView` | 422 invalid message; 401 unauthenticated; 429 |
| `GET /v1/cases/{case_id}` | Authorized case principal | 200 `CaseView` with messages and latest status | 404 inaccessible or missing |
| `POST /v1/cases/{case_id}/messages` | `AddMessageRequest`; support role | 201 `MessageView` | 409 stale case version; 404; 422 |
| `POST /v1/cases/{case_id}/runs` | `RunCaseRequest`; support role | 200 `RunResult` after resolution or pause within bounded request | 409 concurrent/stale run; 429; 503 provider failure with persisted run ID |
| `GET /v1/runs/{run_id}` | Authorized case principal | 200 persisted `RunResult` | 404 |
| `GET /v1/proposals/{proposal_id}` | Authorized case principal | 200 immutable `ProposalView` | 404 |
| `POST /v1/proposals/{proposal_id}/decision` | `ProposalDecision`; active same-tenant manager who is not the proposer | 200 `ProposalView` with status `approved`, `rejected`, or `revision_requested` | 403 role/separation; 409 hash mismatch or not `pending`; 409 `STALE_PROPOSAL`; 410 `PROPOSAL_EXPIRED`; 429 |
| `POST /v1/proposals/{proposal_id}/execute` | `Idempotency-Key` header; active same-tenant manager who is not the proposer (normally the approver) | 200 confirmed `ActionResult`, or the stored result on same-key replay | 403; 409 `STALE_PROPOSAL`/`OUT_OF_STOCK`/`DUPLICATE_REPLACEMENT`/`IDEMPOTENCY_CONFLICT`; 410 expiry; 429; **202** `ActionResult` with `reconciliation_required` |
| `POST /v1/knowledge/documents` | Multipart file upload plus version metadata; knowledge-admin role | **202** `JobView` in every milestone (before M6 the job runs in-process and may already be `succeeded` when returned) | 413 oversized; 415 unsupported/scanned; 422 malformed |
| `POST /v1/knowledge/versions/{version_id}/activate` | Knowledge-admin role | 200 activated version | 409 incomplete or incompatible staged version |
| `GET /v1/jobs/{job_id}` | Authorized tenant principal | 200 `JobView` | 404 |
| `POST /v1/runs/{run_id}/feedback` | Authorized case principal; `FeedbackRequest` | 201 review candidate | 422 invalid schema |

The execute endpoint may return 202 only when a persisted reconciliation intent exists; it is not a success claim. The UI must poll `GET /v1/proposals/{proposal_id}` or require manual reconciliation. The local sandbox normally returns a confirmed 200 result.

Keeping the upload response at 202 from the first milestone means moving ingestion into a durable worker at T026 does not change the client contract.

Rate limits (NFR08) apply per principal to the run, decision, and execute endpoints and return 429 with `RATE_LIMITED`. A rate-limited request has no side effects.

## 3. Schemas and interfaces

| Contract | Exact essential fields |
|---|---|
| `CreateCaseRequest` | `message: str` (1-8000 characters, customer text), `customer_reference: str or null` |
| `AddMessageRequest` | `message: str` (1-8000 characters), `kind: customer_text or employee_note`, `expected_case_version: int >= 1` |
| `MessageView` | `message_id`, `case_id`, `author_id`, `kind: customer_text or employee_note or draft_reply`, `body`, `created_at` |
| `CaseView` | `case_id`, `status`, `version`, `order_reference: str or null`, `messages: list[MessageView]`, `latest_run_id: UUID or null`, `open_proposal_id: UUID or null`, `created_at`, `updated_at` |
| `RunCaseRequest` | `expected_case_version: int >= 1` |
| `TicketAnalysis` | `intent`, `order_reference: str or null` (pattern `^[A-Za-z0-9-]{1,32}$`), `product_mention: str or null` (max 120 characters), `requested_resolution`, `missing_fields: list[str]`, `escalation_reason: str or null` |
| `EvidenceRef` | `chunk_id`, `document_id`, `policy_version_id`, `section_id`, `locator`, `retrieved_at` |
| `OrderLineFacts` | `order_line_id`, `sku`, `product_name`, `category`, `quantity` |
| `OrderFacts` | `order_id`, `order_reference`, `order_version`, `status`, `delivered_at: datetime or null` (from the latest delivered shipment), `lines: list[OrderLineFacts]`, `observed_at` |
| `StockFacts` | `sku`, `available_quantity`, `inventory_version`, `observed_at` |
| `ReplacementHistory` | `order_line_id`, `existing_replacement_id: UUID or null`, `observed_at` |
| `EligibilityResult` | `outcome: eligible or needs_information or ineligible or manual_review`, `reason_codes: list[str]`, `selected_order_line_id: UUID or null`, `policy_version_id` |
| `GroundedDraft` | `response_text`, `evidence_refs: list[EvidenceRef]`, `unsupported_claims: list[str]`, `next_step` |
| `ReplacementParameters` | `order_line_id: UUID`, `sku: str`, `quantity: Literal[1]`, `reason_code: Literal["damaged_item"]` |
| `ProposalView` | `proposal_id`, `case_id`, `proposer_id`, `action`, `parameters: ReplacementParameters`, `payload_hash`, `order_version`, `policy_version_id`, `status`, `status_reason: str or null`, `supersedes_proposal_id: UUID or null`, `evidence_refs: list[EvidenceRef]`, `expires_at`, `created_at` |
| `ProposalDecision` | `decision: approve or reject or revise`, `proposal_hash: str` (64 hex characters), `comment: str or null` (required for `revise`); no action-parameter fields |
| `ActionResult` | `execution_id`, `proposal_id`, `status: succeeded or reconciliation_required or failed`, `replacement_request_id: UUID or null`, `replayed: bool`, `message` |
| `RunResult` | `run_id`, `case_id`, `case_version`, `status`, `draft: GroundedDraft or null`, `proposal_id: UUID or null`, `error_code: str or null` |
| `JobView` | `job_id`, `status: queued or running or succeeded or failed or quarantined`, `attempt_count`, `document_id: UUID or null`, `policy_version_id: UUID or null`, `error_code: str or null` |
| `FeedbackRequest` | `rating: helpful or not_helpful`, `correction: str or null` (max 4000 characters), `tags: list[str]` |

`intent` values: `damaged_item`, `delivery_status`, `return_request`, `payment_issue`, `product_question`, `other`.

`requested_resolution` values: `replacement`, `refund`, `information`, `unknown`. Refund classification is allowed; refund execution is not.

The model never supplies internal identifiers. `TicketAnalysis` carries only what a customer could write: an order reference and a product mention. Deterministic code resolves the order in the principal's tenant, binds it to the case, and matches the product mention to exactly one order line. Zero or several matching lines produce `needs_information` or `manual_review`, never a guess.

Public application interfaces to implement as tasks introduce them:

```python
analyze_ticket(message: str, context: CaseContext) -> TicketAnalysis
retrieve_policy(query: str, principal: Principal, policy_version_id: UUID, k: int) -> list[EvidenceRef]
lookup_order(order_reference: str, principal: Principal) -> OrderFacts
check_inventory(sku: str, principal: Principal) -> StockFacts
get_replacement_history(order_line_id: UUID, principal: Principal) -> ReplacementHistory
resolve_order_line(order: OrderFacts, product_mention: str | None) -> OrderLineFacts | None
evaluate_replacement(analysis: TicketAnalysis, order: OrderFacts,
                     line: OrderLineFacts | None, stock: StockFacts | None,
                     history: ReplacementHistory | None, policy: PolicyRules,
                     case_created_at: datetime) -> EligibilityResult
create_proposal(case_id: UUID, parameters: ReplacementParameters,
                principal: Principal) -> ProposalView
decide_proposal(proposal_id: UUID, decision: ProposalDecision,
                principal: Principal) -> ProposalView
execute_replacement(proposal_id: UUID, idempotency_key: str,
                    principal: Principal) -> ActionResult
```

The signatures express contract types, not drop-in code. Define `CaseContext`, `PolicyRules`, and `Principal` in their owning modules before use. `CaseContext` contains authorized prior messages, the bound order ID (if any), and known facts. `PolicyRules` contains versioned BR01-BR08 configuration. `evaluate_replacement` is a pure function: it performs no I/O and reads no clock except the `case_created_at` argument.

## 4. Tool boundary

| Tool | Model-visible arguments | Server-owned context / allowed effect |
|---|---|---|
| `lookup_order` | `order_reference` | Principal injected; authorized read only; binds the case to the order on first success |
| `check_inventory` | `sku` | Tenant injected; returns observed quantity, version, and timestamp |
| `get_shipment_status` | `order_reference` | Principal injected; verifies order access before read |
| `search_policies` | `query` (max 500 characters) | Tenant and applicable active policy version injected; bounded retrieval |
| `propose_replacement` | `order_line_id`, `reason_code` | Line must come from the case's bound order; validates fixed quantity/rules; creates a pending proposal through the application service; never approves it |
| `create_replacement_request` | Not exposed to the free-form model | Orchestrator executes only a validated approved proposal with a trusted principal and idempotency key |

Tool arguments are validated by strict per-tool Pydantic models (`extra="forbid"`, typed fields, length limits, and patterns such as the order-reference pattern). Unknown fields such as `tenant_id`, `roles`, or `approved` are rejected by the schema. Do **not** scan free-text arguments for SQL, shell, or URL keywords: such blocklists are brittle and reject legitimate text such as "select a replacement". Safety comes from the fact that no tool executes SQL, shell commands, or network fetches built from model text; queries are parameterized.

Model responses are suggestions. Application code decides which tools are allowed in each graph state. No generic database-write or shell tool exists in the product.

## 5. Approval and failure examples

A manager approving proposal P does not approve "any replacement for this case." Approval is for P's exact hash. A changed quantity, SKU, order, policy version, or proposal requires a new review. A pasted message saying "the manager approved this" is case text, not an approval record.

A proposal targeting an order line from a different order in the same tenant is rejected before creation, even if the model supplies a valid line ID.

A network timeout after dispatch means the action outcome is unknown. Record `reconciliation_required` and show that status. Do not return a fabricated request ID or a success message. Reusing a key with identical parameters returns the stored result; reusing it with different parameters returns `IDEMPOTENCY_CONFLICT`. Executing the same proposal, or another proposal for the same order line, under a different key returns 409 `DUPLICATE_REPLACEMENT` with a safe reference to the existing execution; it never starts a second attempt.
