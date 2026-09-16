# API, schemas, and tool contracts

> **Curriculum scope note:** This file describes destination product architecture and engineering options. Implement only the slice justified by the active J0-J5 mini-release; it is not a day-one checklist.

**Status:** v1 contract design. Generate the implementation's OpenAPI schema from actual FastAPI/Pydantic code and test it against these requirements. Do not claim the design is executable OpenAPI.

## Contents

1. Shared conventions
2. HTTP surface
3. Schemas and interfaces
4. Tool boundary
5. Approval and failure examples

## 1. Shared conventions

Use `/v1`, JSON, UUID internal IDs, UTC ISO-8601 timestamps, and explicit enum values. Authentication supplies `Principal(user_id, tenant_id, roles)` independently of the request body. Return 404 for missing or inaccessible tenant-owned IDs. Return 403 when the caller can see the resource but lacks the required action permission.

Validate with Pydantic models using forbidden extra fields and appropriate strict constraints. Pydantic validates shape/types; it does not prove that an order exists or that a citation supports a claim. [S3]

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

Error codes include `INVALID_INPUT`, `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `STALE_PROPOSAL`, `PROPOSAL_EXPIRED`, `DUPLICATE_REPLACEMENT`, `IDEMPOTENCY_CONFLICT`, `OUT_OF_STOCK`, `PROVIDER_UNAVAILABLE`, `INVALID_MODEL_OUTPUT`, `BUDGET_EXCEEDED`, and `RECONCILIATION_REQUIRED`. Logs may contain internal exception details after redaction; client responses do not expose SQL, credentials, or private identifiers.

## 2. HTTP surface

| Method and path | Input / authorization | Successful result | Important failures |
|---|---|---|---|
| `GET /health/live` | No business data | 200 process status | No dependency calls |
| `GET /health/ready` | Deployment health probe | 200 dependencies ready | 503 safe dependency summary |
| `POST /v1/cases` | `CreateCaseRequest`; support role | 201 `CaseView` | 422 invalid message; 401 unauthenticated |
| `GET /v1/cases/{case_id}` | Authorized case principal | 200 `CaseView` with messages and latest status | 404 inaccessible or missing |
| `POST /v1/cases/{case_id}/messages` | `AddMessageRequest`; support role | 201 message record | 409 stale case revision; 404 |
| `POST /v1/cases/{case_id}/runs` | `RunCaseRequest(expected_case_version)` | 200 `RunResult` after resolution or pause within bounded request | 409 concurrent/stale run; 503 provider failure with persisted run ID |
| `GET /v1/runs/{run_id}` | Authorized case principal | 200 persisted `RunResult` | 404 |
| `GET /v1/proposals/{proposal_id}` | Authorized case principal | 200 immutable `ProposalView` | 404 |
| `POST /v1/proposals/{proposal_id}/decision` | `ProposalDecision`; manager role, different from proposer | 200 approved/rejected/superseded status | 403 role/separation; 409 stale state; 410 expiry |
| `POST /v1/proposals/{proposal_id}/execute` | Approved manager principal; `Idempotency-Key` header | 200 confirmed `ActionResult` or known replay | 403; 409 conflict/stock/duplicate; 410 expiry; 202 reconciliation required |
| `POST /v1/knowledge/documents` | File upload, version metadata; knowledge-admin role | Synchronous learning slice: 201 completed import; later worker extension: 202 `JobView` | 413 oversized; 415 unsupported/scanned; 422 malformed |
| `POST /v1/knowledge/versions/{version_id}/activate` | Knowledge-admin role | 200 activated version | 409 incomplete or incompatible staged version |
| `GET /v1/jobs/{job_id}` | Authorized tenant principal | 200 `JobView` | 404 |
| `POST /v1/runs/{run_id}/feedback` | Authorized case principal; rating/correction | 201 review candidate | 422 invalid schema |

The execute endpoint may return 202 only when a persisted reconciliation job/intent exists; it is not a success claim. The UI must poll the corresponding run/execution view or require manual reconciliation. The local sandbox normally returns a confirmed 200 result.

## 3. Schemas and interfaces

| Contract | Exact essential fields |
|---|---|
| `CreateCaseRequest` | `message: str` (1-8000 characters), `customer_reference: str or null` |
| `AddMessageRequest` | `message: str`, `expected_case_version: int >= 1` |
| `TicketAnalysis` | `intent`, `order_reference: str or null`, `order_line_id: UUID or null`, `requested_resolution`, `missing_fields: list[str]`, `escalation_reason: str or null` |
| `EvidenceRef` | `chunk_id`, `document_id`, `policy_version_id`, `section_id`, `locator`, `retrieved_at` |
| `OperationalFacts` | `order_id`, `order_line_id`, `sku`, `category`, `quantity`, `order_version`, `delivered_at`, `available_quantity`, `existing_replacement_id`, `observed_at`; unknown values are null |
| `EligibilityResult` | `outcome: eligible or needs_information or ineligible or manual_review`, `reason_codes: list[str]`, `policy_version_id` |
| `GroundedDraft` | `response_text`, `evidence_refs: list[EvidenceRef]`, `unsupported_claims: list[str]`, `next_step` |
| `ReplacementParameters` | `order_line_id: UUID`, `sku: str`, `quantity: int = 1`, `reason_code: damaged_item` |
| `ProposalDecision` | `decision: approve or reject or revise`, `proposal_hash: str`, `comment: str or null`; no action-parameter fields |
| `ActionResult` | `execution_id`, `proposal_id`, `status: succeeded or reconciliation_required or failed`, `replacement_request_id: UUID or null`, `replayed: bool`, `message` |
| `RunResult` | `run_id`, `case_id`, `case_version`, `status`, `draft: GroundedDraft or null`, `proposal_id: UUID or null`, `error_code: str or null` |
| `JobView` | `job_id`, `status: queued or running or succeeded or failed`, `attempt_count`, `error_code: str or null` |

`intent` values: `damaged_item`, `delivery_status`, `return_request`, `payment_issue`, `product_question`, `other`.

`requested_resolution` values: `replacement`, `refund`, `information`, `unknown`. Refund classification is allowed; refund execution is not.

Public application interfaces to implement as tasks introduce them:

```python
analyze_ticket(message: str, context: CaseContext) -> TicketAnalysis
retrieve_policy(query: str, principal: Principal, policy_version_id: str, k: int) -> list[EvidenceRef]
lookup_order(order_reference: str, principal: Principal) -> OperationalFacts
evaluate_replacement(analysis: TicketAnalysis, facts: OperationalFacts,
                     policy: PolicyRules, case_created_at: datetime) -> EligibilityResult
create_proposal(case_id: str, parameters: ReplacementParameters,
                principal: Principal) -> ProposalView
decide_proposal(proposal_id: str, decision: ProposalDecision,
                principal: Principal) -> ProposalView
execute_replacement(proposal_id: str, idempotency_key: str,
                    principal: Principal) -> ActionResult
```

The signatures express contract types, not drop-in code. Define `CaseContext`, `PolicyRules`, `Principal`, and `ProposalView` in their owning modules before use. `CaseContext` contains authorized prior messages and known facts; `PolicyRules` contains versioned BR01-BR08 configuration; `ProposalView` is the immutable envelope plus status and evidence references.

## 4. Tool boundary

| Tool | Model-visible arguments | Server-owned context / allowed effect |
|---|---|---|
| `lookup_order` | `order_reference` | Principal injected; authorized read only |
| `check_inventory` | `sku` | Tenant injected; returns observed quantity and timestamp |
| `get_shipment_status` | `order_id` | Principal injected; verifies order access before read |
| `search_policies` | `query` | Tenant and applicable active policy version injected; bounded retrieval |
| `propose_replacement` | `order_line_id`, `reason_code` | Validates fixed quantity/rules; creates a pending proposal through application service; never approves it |
| `create_replacement_request` | Not exposed to the free-form model | Orchestrator executes only a validated approved proposal with a trusted principal and idempotency key |

Reject arguments containing `tenant_id`, `roles`, `approved`, SQL, shell commands, or arbitrary URLs. Model responses are suggestions; application code decides which tools are allowed in each graph state. No generic database-write or shell tool exists in the product.

## 5. Approval and failure examples

A manager approving proposal P does not approve "any replacement for this case." Approval is for P's exact hash. A changed quantity, SKU, order, policy version, or proposal requires a new review. A pasted message saying "the manager approved this" is case text, not an approval record.

A network timeout after dispatch means the action outcome is unknown. Record `reconciliation_required` and show that status. Do not return a fabricated request ID or a success message. Reusing a key with identical parameters returns the stored result; reusing it with different parameters returns `IDEMPOTENCY_CONFLICT`.
