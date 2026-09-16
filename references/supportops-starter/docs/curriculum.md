# SupportOps AI curriculum — J0 to J5

This route preserves the existing compact identifiers while changing the learner experience: one product, small runnable mini-releases, meaningful transfer, and named deferral triggers.

## Route principles

1. One evolving SupportOps codebase; no second required medical product.
2. Each stage contains a useful stopping point before the next mechanism is introduced.
3. The product limitation comes before the tool that solves it.
4. Boundary checks are part of the mechanism; large testing/infrastructure programs are not day-one prerequisites.
5. Transfer stays mandatory and changes a reasoning constraint, not only vocabulary.
6. Frameworks are introduced after the native mechanism is visible.
7. Destination architecture in `docs/project/` is reference material, not a checklist to complete before the first result.

## J0 — First useful model boundary

**Product result:** a tiny Reply Drafting Tool. Given a synthetic customer message and an explicitly supplied policy excerpt, it produces a draft for human review without claiming order lookup or action execution.

Teach: local Python -> provider SDK -> authorized request -> hosted inference -> parsed local response; roles/messages; request/response objects; configuration and failure layers; first JSON experiment if useful.

Closed checkpoints: first authorized call; inspect raw/parsed response; produce a small draft; explain deterministic local code versus probabilistic output. Provider-specific examples must match current docs: a list-shaped `choices` response does not imply Groq supports `n=2`.

**Defer:** FastAPI, database, embeddings, LangChain/LangGraph, queues, deployment.

## J1 — Structured support-case intake

**Product result:** Ticket Intake Tool. Convert a support message into validated fields such as issue type, stated order reference, requested resolution, missing information, attributed reports, and evidence spans.

Teach: JSON syntax vs schema validity vs source truth; Pydantic; null/missing; strictness/extra fields; negation, uncertainty, chronology, prompt-injection-like source text; source evidence. Span contract: start-inclusive/end-exclusive **Python string code-point indices into the original unnormalized text**.

Use `fixtures/support/` and keep development/held-out cases distinct. A schema-valid answer can still be factually wrong.

Introduce a few deterministic automated checks once the validator/span behavior exists; do not build a broad testing architecture.

## J2 — Required within-product transfer

**Product result:** adapt intake to a delivery-dispute case where sources can disagree: the customer reports non-delivery while a supplied carrier-status record says delivered. Preserve attribution and uncertainty instead of collapsing both into one fact.

No live carrier API is required here. The new difficulty is the trust/attribution rule, not a new integration stack.

Assess whether the learner can modify/explain/debug the mechanism on a genuinely different case after support is faded. Delayed transfer remains separate from immediate fluency.

## J3 — Retrieval, then grounded answers

**Closed mini-release A: Policy Finder.** Search a small frozen policy corpus and show top passages with document/version/section metadata. Start with an inspectable lexical/exact-term baseline, then one verified embedding route and visible similarity. The generation and embedding provider may differ.

**Closed mini-release B: Cited Policy Assistant.** Generate an answer only from eligible retrieved evidence; cite support, distinguish conflicting/superseded/no-evidence cases, and abstain or ask when evidence is inadequate.

Evaluate retrieval separately from answer support. Do not treat RAG as permission to obey instructions embedded in documents.

**Defer until measured need:** persistent vector DB, hybrid/reranking, protected-doc access filtering beyond the current fixture, large-scale ingestion workers.

## J4 — Read tools, then bounded action

**Closed mini-release A: Scoped Order Lookup.** Hand-write parameterized SQL/read functions against synthetic orders. Trusted application context supplies actor/tenant scope; model arguments cannot broaden it. Missing, unauthorized, and service-error outcomes stay distinguishable.

**Closed mini-release B: Investigation Copilot.** Expose narrow read tools and let the model request them through a bounded loop. Validate arguments, preserve tool-call identity, bound steps/time, and report failures accurately.

**Closed mini-release C: Approved Replacement Simulation.** Prepare an immutable proposal, require exact authorized approval, revalidate at execution, and prevent duplicate local effects under the defined sequential/replay cases. Local success is not distributed exactly-once behavior.

A workflow library such as LangGraph becomes a focused comparison/adoption only when pause/resume or explicit state complexity justifies it.

## J5 — Deliver one engineered learning project

Package **one** SupportOps product, not two portfolio applications. Make it runnable by another person, keep evaluation honest, and require independent ownership evidence.

Required evidence: reproducible local run; small usable interface/API only where it improves the demo; held-out evaluation with counts/denominators and failure categories; one unfamiliar learner change; one unfamiliar learner diagnosis; architecture explanation and rejected alternative; demo recording or equivalent reproducible evidence; clear limitations and assistance disclosure.

Basic CI/container/deployment may be added only when required by the chosen portfolio target or a repeated friction point. Operational maturity remains a separate claim.

## Named deferral triggers

| Deferred capability | Reopen when |
|---|---|
| Pytest architecture/coverage/CI | checks span multiple files, regressions repeat, or a target role explicitly requires it |
| LangSmith/hosted tracing | native logs no longer explain a multi-step failure or evaluation needs structured traces; data/spending authorized |
| Postgres/pgvector/hybrid search | local corpus/search lifecycle or measured retrieval limits justify persistence/scale |
| LangGraph durable workflow | local explicit state becomes hard to resume/reason about or restart/approval recovery is a selected learning target |
| Docker/deployment/auth/OIDC | the project must run outside the development machine or a target role requires evidence |
| queues/workers/concurrency hardening | ingestion or writes require background/durable/concurrent behavior |
| MCP/multi-agent/fine-tuning | a specific measured problem cannot be solved more simply |
