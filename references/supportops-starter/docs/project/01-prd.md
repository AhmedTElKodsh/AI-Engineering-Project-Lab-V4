# Product requirements document

> **Curriculum scope note:** This file describes destination product architecture and engineering options. Implement only the slice justified by the active J0-J5 mini-release; it is not a day-one checklist.

**Product:** SupportOps AI  
**Version:** 1.0.0  
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
| Portfolio release | MVP plus expanded evaluation, ML baseline, tracing, queues, OIDC deployment, concurrency/recovery evidence | Claims of production readiness or measured business ROI |

### Non-goals

No refunds, payments, real shipping, unrestricted SQL, customer-facing autonomous chat, agent-generated policy updates, multi-agent organization, arbitrary web browsing, or automatic use of historical tickets as authoritative policy. Scanned documents, photo analysis, MCP, and fine-tuning are extensions.

## 3. Primary experience and business rules

### Happy path

An agent opens a case containing: "The blender in order 1042 arrived yesterday with a cracked container. Please replace it." The application extracts the relevant identifiers without inventing missing ones. It retrieves the order within the authenticated store, locates the applicable policy, and checks stock. It displays the facts, citations, proposed replacement, and customer-response draft. A different authorized manager approves an immutable proposal. The backend revalidates permissions, proposal expiry, policy version, current order version, stock, and duplicate state. The sandbox service creates one replacement request and the UI reports its identifier. It does not say that a parcel has shipped.

### Fictional policy for the first workflow

These are project fixtures, not legal or industry guidance.

| Rule | Exact demo rule |
|---|---|
| BR01 | Intent is damaged item and requested resolution is replacement. Other intents are routed or escalated without this write. |
| BR02 | Exactly one identifiable order line, quantity one, category `small_appliance`, and a known delivery timestamp are required. Multiple lines or quantities require manual handling. |
| BR03 | Complaint age is the difference between the case-created local calendar date and delivered local calendar date in Africa/Cairo. Eligible range is 0 through 7 days inclusive. Negative or missing age requires clarification or escalation. |
| BR04 | The demo accepts the customer's recorded damage statement; no image or fraud determination is required. Do not claim damage was independently verified. |
| BR05 | Available stock must be at least one; no active or completed replacement may already exist for the same tenant and order line. |
| BR06 | Use the active policy version at proposal creation. If the active version changes before execution, invalidate the proposal and require a fresh review. |
| BR07 | A proposal expires after 15 minutes. Approval requires the manager role in the same tenant, and approver must differ from proposer. Authorization is checked again at execution. |
| BR08 | A customer reply is a draft only. The application does not send email or initiate shipping. |

### Alternate outcomes

Missing order identifier: ask one targeted question. Unknown or unauthorized order: return the same non-disclosing not-found response. No applicable policy or conflicting evidence: escalate. Out-of-window claim or unsupported quantity: explain the constraint and escalate. No stock: propose manual follow-up, not a fabricated replacement. Provider or integration failure: retain case state and distinguish retryable failure from confirmed outcome. Unknown write outcome: reconcile before retrying.

## 4. Functional requirements

Each acceptance criterion becomes named tests in the backlog and traceability file.

| ID | Requirement | Acceptance criteria |
|---|---|---|
| FR01 | Create and resume cases | An authenticated employee can create a case with a nonblank message, add messages, and resume its persisted state; foreign-tenant case IDs reveal no content. |
| FR02 | Produce validated ticket analysis | Return intent, optional order reference, optional line identifier, requested resolution, missing fields, and escalation reason; reject extra or invalid fields; unknown facts remain null. |
| FR03 | Manage knowledge lifecycle | Ingest supported text, Markdown, or text-based PDF; retain source location, checksum, tenant, version, effective interval, and status; re-ingestion is idempotent; activation is atomic; retired documents are excluded from new searches. |
| FR04 | Answer using eligible evidence | Return source references that resolve to authorized retrieved chunks; distinguish quoted policy from live facts; flag unsupported claims; ask or escalate when evidence is inadequate. Compare semantic and hybrid retrieval for the portfolio release. |
| FR05 | Read current business data safely | Order, inventory, and shipment reads use narrow tools and backend scope; model-supplied identity cannot broaden access; volatile facts are refreshed before action execution. |
| FR06 | Apply deterministic eligibility | Evaluate BR01-BR08 using typed facts and versioned rule configuration; return eligible, needs-information, ineligible, or manual-review with machine-readable reasons; do not delegate authorization or arithmetic to the model. |
| FR07 | Run a bounded persistent workflow | Persist analysis, evidence IDs, proposal ID, version, current node, and typed failures; pause for clarification or approval; resume after restart without duplicate writes; enforce call and time budgets. |
| FR08 | Review an exact proposal | Display action, arguments, evidence, expiry, and proposer; allow approve, reject, or request revision; modifying action parameters creates a new proposal and invalidates any previous approval. |
| FR09 | Execute and reconcile one safe write | Execute only a current approved proposal; same idempotency key and same payload return the same result; key reuse with changed payload fails; concurrent requests cannot overdraw inventory or create a second replacement; unknown external outcome enters reconciliation. |
| FR10 | Provide an inspectable employee UI | Show case messages, source links, current facts, draft, proposal controls, action outcome, and error/recovery status; hide approval controls from non-managers, while backend enforcement remains authoritative. |
| FR11 | Evaluate and trace behavior | Preserve redacted run IDs, prompt/model/index versions, component latency, usage, tool results, and evaluation outputs; run deterministic CI fixtures plus opt-in live evaluations; user corrections become reviewed regression candidates. |
| FR12 | Benchmark ticket routing | Train a TF-IDF plus logistic-regression baseline using grouped splits; compare with an LLM on the same held-out routing inputs; report macro-F1, per-class metrics, confusion matrix, and measured cost/latency. |
| FR13 | Optional asynchronous-ingestion extension | If reopened by scale/role needs, return job IDs, expose job status, bound safe retries, quarantine permanent failures, and avoid duplicate active document versions. Not required for the initial J0-J5 learning release. |
| FR14 | Optional operational-delivery extension | When deployment is selected, add the smallest justified container/CI/auth/health/recovery evidence for that target. Not required for the initial local J0-J5 learning release. |

## 5. Nonfunctional requirements

| ID | Requirement and initial target | How to verify |
|---|---|---|
| NFR01 | No unauthorized business writes or cross-tenant data disclosure in the defined mandatory test suite | Negative authorization tests at HTTP, repository, retrieval, workflow-resume, and execution boundaries; all must pass |
| NFR02 | No duplicate replacement and no negative stock in replay/concurrency tests | Parallel requests, same-key replay, different-key duplicate attempt, crash-after-commit, and reconciliation fixtures |
| NFR03 | Initial locked-test targets: workflow success >=85%; supported-claim precision >=95%; retrieval section recall@5 >=85% on eligible retrieval cases; required-escalation recall >=95% | Fixed rubric and dataset version; counts and denominators reported; targets are project choices, not observed results |
| NFR04 | Every evaluated interaction has a run ID and model/prompt/retrieval versions; every write has an audit record | Trace completeness and transaction-level audit tests; never record credentials or raw personal data |
| NFR05 | Initial aspirations: p95 draft latency <=15 seconds at five concurrent sessions, excluding human wait; average metered model cost <=USD 0.10 per successful evaluated case | Record machine, network, provider, versions, cold/warm state, errors, and at least 100 attempts; revise only through a documented decision |
| NFR06 | Clean checkout is reproducible; routine tests require no paid calls | Locked dependencies and image references, documented commands, deterministic fixtures, clean-environment CI |
| NFR07 | Synthetic data only by default; no credentials or unredacted customer payloads in Git or external traces | Secret scans, redaction tests, configured trace allowlist, and explicit opt-in for hosted traces/live models |

Budget and latency numbers are engineering targets, not provider prices or promises. Report model cost separately from embeddings, evaluation judges, storage, and hosting. Counts from a small synthetic suite do not establish universal safety or real-world accuracy.

## 6. Acceptance and release gates

A task is done only when its acceptance behavior is implemented, required tests pass, evidence is saved, and a review is recorded. Learning mastery is recorded separately.

Before the first local simulated write, pass approval, permission, expiry, mutation and replay/duplicate checks for the implemented path. Add concurrency and unknown-outcome reconciliation before claiming those stronger properties or connecting an external write. Public deployment has its own auth/redaction/spending/recovery gate. The initial J0-J5 portfolio release remains valid as a reproducible local engineered project with honest evaluation, failure analysis and demo evidence.

No acceptance measurements exist in this planning pack. The twelve example cases are development seeds, not the promised locked acceptance dataset.

## 7. Assumptions and changes

Assumptions and risks live in `10-risks-and-decisions.md`. The learner is the decision owner until another owner is explicitly assigned. A scope change must update affected requirement IDs, contracts, tasks, tests, and learning checkpoints. Preserve the previous baseline in version control. A new tool must solve a documented problem or test an explicit hypothesis.
