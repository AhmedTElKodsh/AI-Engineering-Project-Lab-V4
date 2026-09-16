# Product requirements document

**Product:** Commerce Support Copilot  
**Version:** 1.1.0  
**Prepared:** 2026-09-15  
**Owner:** learner acting as product engineer  
**Status:** implementation planning baseline; acceptance results not yet measured

## Contents

1. Problem and users
2. Goals and scope
3. Primary experience and business rules
4. Functional requirements
5. Nonfunctional requirements
6. Acceptance and release gates
7. Assumptions and changes

## 1. Problem and users

A support employee must combine policy, order status, inventory, and customer messages to resolve a complaint. A plausible response is insufficient: an operational action must also be authorized, policy-compliant, current, and correctly reported.

**Support agent:** creates a case, inspects evidence, edits a draft, and submits a proposal. **Support manager:** can do support work and approve or reject another employee's proposal. **Knowledge administrator:** ingests and activates policy documents; this role does not automatically grant action approval. **Evaluator/developer:** runs synthetic cases and inspects redacted traces. An individual may have several explicitly assigned roles.

For the demo, serve two seeded store tenants so cross-tenant access can be tested. Only one store's workflow needs a complete UI walkthrough. Authentication establishes the actor, roles, and tenant; a customer message or model output cannot establish them.

## 2. Goals and scope

### Goals

Provide a source-backed resolution draft; distinguish policy knowledge from current operational facts; require review before business writes; recover from missing data and integration failures; measure quality and cost; make the system explainable through visible evidence and logs.

### Release levels

| Level | Included | Explicitly absent |
|---|---|---|
| Read-only demo | Ticket analysis, document retrieval, citations, live-data sandbox reads | Replacement execution and public deployment |
| Sandbox workflow MVP | Read-only features plus durable case workflow, manager approval, one deduplicated replacement request, minimal UI | Real commerce integrations, full operations hardening |
| Portfolio release | MVP plus expanded evaluation, ML baseline, tracing, external-write reconciliation, queues, OIDC deployment, concurrency/recovery evidence | Claims of production readiness or measured business ROI |

The exact tasks required for each level are recorded in the backlog's **Required for** field (`required_for` in `learning/backlog.json`). Milestones group related work; they do not by themselves define a release level.

### Non-goals

No refunds, payments, real shipping, unrestricted SQL, customer-facing autonomous chat, agent-generated policy updates, multi-agent organization, arbitrary web browsing, or automatic use of historical tickets as authoritative policy. Scanned documents, photo analysis, MCP, and fine-tuning are extensions.

## 3. Primary experience and business rules

### Happy path

An agent opens a case containing: "The blender in order 1042 arrived yesterday with a cracked container. Please replace it." The application extracts the order reference and product mention without inventing missing ones. It retrieves the order within the authenticated store, binds the case to that order, resolves the mentioned product to one order line in deterministic code, locates the applicable policy, and checks stock. It displays the facts, citations, proposed replacement, and customer-response draft. A different authorized manager approves an immutable proposal and then triggers execution. The backend revalidates permissions, proposal expiry, policy version, current order version, stock, and duplicate state. The sandbox service creates one replacement request and the UI reports its identifier. It does not say that a parcel has shipped.

### Fictional policy for the first workflow

These are project fixtures, not legal or industry guidance.

| Rule | Exact demo rule |
|---|---|
| BR01 | Intent is damaged item and requested resolution is replacement. Other intents are routed or escalated without this write. |
| BR02 | Exactly one identifiable order line, quantity one, category `small_appliance`, and a known delivery timestamp are required. Multiple lines or quantities require manual handling. |
| BR03 | Complaint age is the difference between the case-created local calendar date and the delivered local calendar date in the store timezone (Africa/Cairo). The delivered instant comes from the latest `delivered` shipment record for the order; it is the only delivery source of truth. Eligible range is 0 through 7 days inclusive. Negative or missing age requires clarification or escalation. |
| BR04 | The demo accepts the customer's recorded damage statement; no image or fraud determination is required. Do not claim damage was independently verified. |
| BR05 | Available stock must be at least one; no active or succeeded replacement may already exist for the same tenant and order line. |
| BR06 | Use the active policy version at proposal creation. If the active policy version or the order version changes before execution, the proposal becomes `invalidated` (whether pending or approved) and a fresh proposal and review are required. |
| BR07 | A proposal expires 15 minutes after its creation (`expires_at`). Approval and the start of execution must both happen before `expires_at`. Approval requires an active manager in the same tenant who is not the proposer. Execution may be triggered by any active same-tenant manager who is not the proposer (normally the approver); role, tenant, and expiry are checked again at execution. |
| BR08 | A customer reply is a draft only. The application does not send email or initiate shipping. |

### Alternate outcomes

Missing order identifier: ask one targeted question. Unknown or unauthorized order: return the same non-disclosing not-found response. No applicable policy or conflicting evidence: escalate. Out-of-window claim or unsupported quantity: explain the constraint and escalate. No stock: propose manual follow-up, not a fabricated replacement. Provider or integration failure: retain case state and distinguish retryable failure from confirmed outcome. Unknown write outcome: reconcile before retrying.

## 4. Functional requirements

Each acceptance criterion becomes named tests in the backlog and traceability file.

| ID | Requirement | Acceptance criteria |
|---|---|---|
| FR01 | Create and resume cases | An authenticated employee can create a case with a nonblank message, add customer-text or employee-note messages, and resume its persisted state; once an order is resolved the case is bound to it; foreign-tenant case IDs reveal no content. |
| FR02 | Produce validated ticket analysis | Return intent, optional order reference, optional product mention, requested resolution, missing fields, and escalation reason; reject extra or invalid fields; unknown facts remain null; the model never supplies internal IDs. |
| FR03 | Manage knowledge lifecycle | Ingest supported text, Markdown, or text-based PDF; retain source location, checksum, tenant, version, effective interval, and status; re-ingestion is idempotent; activation is atomic; retired documents are excluded from new searches. |
| FR04 | Answer using eligible evidence | Return source references that resolve to authorized retrieved chunks; distinguish quoted policy from live facts; flag unsupported claims; ask or escalate when evidence is inadequate. Compare semantic and hybrid retrieval for the portfolio release. |
| FR05 | Read current business data safely | Order, inventory, and shipment reads use narrow tools and backend scope; model-supplied identity cannot broaden access; volatile facts are refreshed before action execution. |
| FR06 | Apply deterministic eligibility | Evaluate BR01-BR08 using typed facts and versioned rule configuration; return eligible, needs-information, ineligible, or manual-review with machine-readable reasons; do not delegate authorization or arithmetic to the model. |
| FR07 | Run a bounded persistent workflow | Persist analysis, evidence IDs, proposal ID, version, current node, and typed failures; pause for clarification or approval; resume after restart without duplicate writes; enforce call and time budgets. |
| FR08 | Review an exact proposal | Display action, arguments, evidence, expiry, and proposer; allow approve, reject, or request revision; modifying action parameters creates a new proposal, marks the old one `superseded`, and voids any previous approval; a proposal can only target an order line of the order bound to its case. |
| FR09 | Execute and reconcile one safe write | Execute only a current approved proposal; same idempotency key and same payload return the same result; key reuse with changed payload fails; concurrent requests cannot overdraw inventory or create a second replacement; unknown external outcome enters reconciliation. |
| FR10 | Provide an inspectable employee UI | Show case messages, source links, current facts, draft, proposal controls, action outcome, and error/recovery status; hide approval controls from non-managers, while backend enforcement remains authoritative. |
| FR11 | Evaluate and trace behavior | Preserve redacted run IDs, prompt/model/index versions, component latency, usage, tool results, and evaluation outputs; run deterministic CI fixtures plus opt-in live evaluations; user corrections become reviewed regression candidates. |
| FR12 | Benchmark ticket routing | Train a TF-IDF plus logistic-regression baseline using grouped splits; compare with an LLM on the same held-out routing inputs; report macro-F1, per-class metrics, confusion matrix, and measured cost/latency. |
| FR13 | Process ingestion asynchronously | The upload contract returns a job ID from the start; the portfolio release runs jobs in a durable worker, exposes job status, retries safe jobs within a bound, and quarantines permanent failures; worker restart does not duplicate active document versions or business actions. |
| FR14 | Package and operate the demo | Provide containerized deployment, migrations, config validation, health/readiness endpoints, CI checks, rollback and restore instructions, and an authenticated demonstration with no live commerce side effects. |

## 5. Nonfunctional requirements

| ID | Requirement and initial target | How to verify |
|---|---|---|
| NFR01 | No unauthorized business writes or cross-tenant data disclosure in the defined mandatory test suite | Negative authorization tests at HTTP, repository, retrieval, workflow-resume, and execution boundaries; all must pass |
| NFR02 | No duplicate replacement and no negative stock in replay/concurrency tests | Parallel requests, same-key replay, different-key duplicate attempt, crash-after-commit, and reconciliation fixtures |
| NFR03 | Initial locked-test targets: workflow success >=85%; supported-claim precision >=95%; retrieval section recall@5 >=85% on eligible retrieval cases; required-escalation recall >=95% | Fixed rubric and dataset version; counts and denominators reported; targets are project choices, not observed results |
| NFR04 | Every evaluated interaction has a run ID and model/prompt/retrieval versions; every write has an audit record | Trace completeness and transaction-level audit tests; never record credentials or raw personal data |
| NFR05 | Initial aspirations: p95 draft latency <=15 seconds at five concurrent sessions, excluding human wait; average metered model cost <=USD 0.10 per successful evaluated case | Record machine, network, provider, versions, cold/warm state, errors, and at least 100 attempts; revise only through a documented decision |
| NFR06 | Clean checkout is reproducible; routine tests require no paid calls | Locked dependencies and image references, documented commands, deterministic fixtures, clean-environment CI |
| NFR07 | Synthetic data only by default; no credentials or unredacted customer payloads in Git, application logs, or external traces | Secret scans, log-redaction tests from M0, configured trace allowlist, and explicit opt-in for hosted traces/live models |
| NFR08 | Abuse and runaway-request protection: per-principal rate limits on run, decision, and execute endpoints (initial target: 30 run requests per principal per minute) return a safe `RATE_LIMITED` error without side effects | Rate-limit tests at the HTTP boundary, including a limit hit during an approval flow; limits are configuration, not code literals |

Budget and latency numbers are engineering targets, not provider prices or promises. Report model cost separately from embeddings, evaluation judges, storage, and hosting. Counts from a small synthetic suite do not establish universal safety or real-world accuracy.

## 6. Acceptance and release gates

A task is done only when its acceptance behavior is implemented, required tests pass, evidence is saved, and a review is recorded. Learning mastery is recorded separately.

Before the first sandbox write, pass approval, permission, expiry, duplicate, and concurrency tests for the implemented path. Before any public deployment, disable demo authentication, enforce OIDC, verify role/tenant claims, redact traces, configure spending limits, and complete the release checklist. Before calling the project a complete portfolio release, complete all thirty tasks and present the evaluation report, failure analysis, and demo evidence.

No acceptance measurements exist in this planning pack. The twelve example cases are development seeds, not the promised locked acceptance dataset.

## 7. Assumptions and changes

Assumptions and risks live in `10_RISKS_AND_DECISIONS.md`. The learner is the decision owner until another owner is explicitly assigned. A scope change must update affected requirement IDs, contracts, tasks, tests, and learning checkpoints. Preserve the previous baseline in version control. A new tool must solve a documented problem or test an explicit hypothesis.
