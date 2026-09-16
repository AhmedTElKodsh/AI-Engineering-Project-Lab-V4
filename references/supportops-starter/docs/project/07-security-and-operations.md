# Security, reliability, and operations

> **Curriculum scope note:** This file describes destination product architecture and engineering options. Implement only the slice justified by the active J0-J5 mini-release; it is not a day-one checklist.

## Contents

1. Threat model and permissions
2. Data handling and secrets
3. Runtime limits and reliability
4. Deployment and cost control
5. Incident, rollback, and release checklists

## 1. Threat model and permissions

Protect customer/order records, policy integrity, approval records, inventory, execution credentials, evaluation integrity, and learner API keys. Trust the authenticated principal and reviewed configuration, not customer messages, uploaded documents, model responses, or task logs containing instructions.

OWASP identifies both direct/indirect prompt injection and excessive agency as material LLM-application risks. The project responds with narrow tools, backend authorization, explicit approval, and untrusted-content separation; prompts alone are not the enforcement boundary. [S7, S8]

| Actor | Allowed | Not automatically allowed |
|---|---|---|
| Support agent | Read same-tenant cases/orders/policies; draft; propose | Approve own or others' proposals; activate policy; execute unapproved actions |
| Support manager | Support actions; approve another employee's same-tenant proposal; execute an approved proposal | Bypass expiry, rules, tenant scope, or duplicate guards |
| Knowledge administrator | Upload and activate reviewed same-tenant policies | Approve commerce actions merely because of admin status |
| Worker | A specific persisted job/action under scoped service credentials | Invent actor identity, change approvals, unrestricted commerce access |
| LLM | Return bounded structured suggestions and permitted read/proposal tool requests | Set roles, approve, access arbitrary SQL/shell/network, or execute writes |

Local development uses explicit loopback-only synthetic identities. Never trust unsigned tenant/role headers. A selected public-deployment extension replaces development identity with OIDC token validation: signature, issuer, audience, expiry, tenant mapping, and current role checks. Fail startup when development authentication is enabled outside an explicitly local environment. Hosted UI access requires real authentication before any public exposure.

## 2. Data handling and secrets

Use synthetic data by default. Store credentials in environment/secret storage, exclude `.env` from Git, commit only key names in `.env.example`, and scan changes for accidental secrets. Never ask a learner to paste a live API key into chat. A suspected leaked credential requires redaction and rotation guidance, not repeating it in the response.

Keep raw customer bodies out of hosted traces. Use an allowlist of trace fields: run ID, pseudonymous tenant/case identifiers, versions, durations, safe error codes, usage totals, and redacted tool summaries. Explicitly opt in before enabling a third-party trace sink or sending any data to a hosted model.

Default synthetic-demo retention: local raw case/log content for 30 days, de-identified aggregate evaluation results until the learner deletes the project. This is a proposed demo setting, not legal-compliance advice. A real-data deployment needs a jurisdiction- and contract-specific retention/privacy review, deletion propagation, backups policy, and access audit.

Treat uploaded files as data: allow text, Markdown, and text-based PDF; maximum 10 MiB per file and 100 pages for PDFs in the initial configuration. Reject executable/archive input, encrypted PDFs, unsupported scans, and failed parsing. Do not execute embedded PDF or HTML content. No URL-fetch ingestion is included.

## 3. Runtime limits and reliability

Each case run has at most four model attempts, eight read-tool attempts, a 15-second per-call timeout, and a 45-second wall-time ceiling. At most two attempts for a transient call, constrained by those total limits. A schema repair consumes a model attempt. Do not retry non-retryable authentication, validation, or business-rule errors.

Use exponential backoff with jitter for safe transient reads and ingestion jobs. Ingestion jobs have at most three total attempts; exhausted jobs retain a diagnostic record in failed/quarantine state. Never auto-retry an ambiguous external write unless the adapter supplies verified idempotency/reconciliation semantics.

Expose liveness without touching providers and readiness with safe database/broker checks. Do not make readiness depend on a paid model inference. Track error rates, queue depth, oldest queued job age, p95 latency, budget consumption, pending approvals, and reconciliation-required actions.

Approval data and action deduplication live in PostgreSQL. Redis can fail without creating authority to write. Graph state, application state, and execution state must reconcile through persisted IDs. Revalidate approval/facts after restart instead of trusting a checkpoint's old stock value.

## 4. Deployment and cost control

Use one authenticated container host with API and UI, PostgreSQL with pgvector, and optional worker/Redis services. The learner selects a host only when deployment becomes an explicit learning/portfolio target, after comparing current prices and capabilities; no cloud account, provider plan, or paid resource is provisioned by this planning kit.

Record exact Python/package versions and image tags or digests after verifying compatibility. Commit a dependency lock. Use separate development and demo databases. Back up the database before migrations; test restore in an isolated instance. Encrypt traffic with TLS and keep database/broker ports private in a hosted deployment.

Live model calls begin disabled. Before a live experiment, set a user-approved run cap and daily cap, input/output token limits, concurrency, and provider/model IDs. Enforce the run cap in application code, not only a dashboard. Show estimates as estimates and metered totals as metered totals. Store the dated pricing basis and usage categories; if prices are unavailable, report token counts without inventing monetary totals.

## 5. Incident, rollback, and release checklists

### Unexpected or duplicate action

Disable new business writes; preserve request IDs, approval records, and execution ledger; reconcile downstream outcomes; restore service only after a regression test covers the defect. Never automatically delete a possibly successful replacement to make logs look consistent.

### Bad policy/index release

Deactivate the defective version, restore the previously validated version, invalidate pending proposals bound to changed policy versions, and rebuild affected indexes. Preserve past evidence references for audit. Test a safe activation rollback in the demo.

### Provider outage or runaway spending

Fail into preserved case state, disable live calls, use fake adapters for development, and show a controlled service-unavailable result in the product. Do not fabricate answers or automatically switch to an unapproved provider.

### Deployment rollback

Stop new writes, identify the last known-good application image and compatible migration level, back up current data, and roll back application configuration first. Do not run destructive down-migrations against valuable data without a reviewed recovery plan. Demonstrate restore on synthetic data, not on production records.

### Release gate

Before publishing the portfolio demo: all mandatory safety tests pass; OIDC replaces local identities; no secrets in artifacts; fake versus live mode is visible; dataset and model cards identify synthetic limitations; application and database are backed up; health checks and spend caps are configured; restore and approval-resume smoke tests have evidence; demo actions remain sandboxed. A portfolio release is not a certification of production safety.
