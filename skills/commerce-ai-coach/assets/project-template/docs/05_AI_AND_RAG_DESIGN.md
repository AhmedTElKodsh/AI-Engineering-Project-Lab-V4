# AI, RAG, and ML design

## Contents

1. Baseline and model boundaries
2. Prompt/output contract
3. Ingestion and retrieval experiments
4. Controlled workflow and memory
5. Traditional ML experiment
6. Feedback and optimization

## 1. Baseline and model boundaries

Start with a deterministic `FakeModelClient` that implements the same interface as the hosted adapter. Unit tests must not call paid services. The first live baseline uses a configurable hosted text model through its provider's official SDK; Claude is the initial preference, not a hard-coded model release. Record the selected model ID and verify structured-output/tool support against current official documentation before implementation.

Use Pydantic for typed outputs and explicit nulls. Implement provider timeout, schema errors, usage reporting, and fake responses before introducing LangChain. At the workflow milestone, use LangChain where an integration reduces boilerplate and LangGraph for state/pause/resume. Preserve model-adapter contract tests across the change.

Provider calls are nondeterministic even with conservative generation settings. Do not assert that low temperature guarantees identical results. Log prompt version, model ID, request settings, schema version, and usage for every evaluated call.

## 2. Prompt/output contract

Separate trusted system instructions, validated task data, retrieved evidence, and conversation content. Customer messages and documents may contain instructions but cannot override application rules. Extraction should identify facts stated in the message (order reference, product mention, intent, requested resolution), not infer eligibility, invent order references, or emit internal IDs. Drafting should cite authorized evidence IDs and distinguish a customer's claim from verified operational data.

Version two initial prompts: `ticket_analysis_v1` and `resolution_draft_v1`. Each defines the task, allowed outputs, missing-information behavior, evidence rules, and a few development examples. Do not include locked-test examples in prompts or few-shot demonstrations.

Validate schema before consuming output. If a structured response is invalid, permit at most one controlled repair when the run budget allows, then return `INVALID_MODEL_OUTPUT`. A repair does not make unsupported content true. Validate cited IDs against the retrieved authorized set and run separate factual/policy checks.

Do not use an uncalibrated model self-confidence score to authorize writes or decide that an answer is safe. Prefer observable conditions: required fields present, applicable policy located, facts refreshed, deterministic eligibility satisfied, and human approval valid.

## 3. Ingestion and retrieval experiments

Start with section-aware chunks around 450 tokens with up to 60 tokens of overlap, avoiding duplicated headings and broken tables. These are initial hypotheses, not optimal values. Use the actual selected embedding tokenizer and record the chunking version. Retain original page/section locators and a stable section ID.

Use a compact local Sentence Transformers embedding model selected after verifying its license, dimensions, and revision. Pin the exact identifier/revision in the index manifest. No document leaves the machine for embedding unless explicitly authorized.

### Retrieval sequence

First filter by authenticated tenant, active compatible policy version, and access scope. Retrieve exact vector top-k as the baseline. For hybrid retrieval, combine keyword and vector candidate rankings using a documented reciprocal-rank-fusion configuration; begin with top 20 candidates from each leg. Optionally rerank the fused candidates and send at most five source sections within a 6000-token evidence budget to drafting. Pin all parameters for experiments. PostgreSQL full-text search plus pgvector is the selected hybrid architecture. [S2]

Reranking is a separate experiment, not an assumed improvement. Compare semantic-only, hybrid, and hybrid-plus-reranker on the same development queries, then evaluate the frozen configuration on the locked test set. Sentence Transformers documents the retrieve-then-rerank pattern. [S5]

De-duplicate by stable section ID before scoring retrieval; otherwise overlapping chunks can inflate apparent recall. Include exact SKU/order-like identifiers, paraphrases, near-identical policies, old versions, and unanswerable questions in development cases. Live order facts do not belong in the policy vector index.

### Citations and abstention

A returned source ID proves only that the source exists, not that it entails a claim. Review factual support separately. Do not manufacture quotes or source locations. If evidence is missing, contradictory, unauthorized, or incompatible with the active rules, ask for clarification or escalate. Never substitute obsolete policy solely because it is semantically similar.

## 4. Controlled workflow and memory

Use explicit graph nodes for analysis, authorized reads, retrieval, rules, drafting, proposal, approval pause, execution, and final reporting. The graph may choose among bounded next steps; it does not invent new tools or business rules.

Per run, allow at most four model HTTP attempts including retries/repairs, eight read-tool attempts, and a 45-second wall-time ceiling. A single call timeout is at most 15 seconds. Transient operations may be attempted twice at most, within the total budget. Exceeded limits produce a typed error and preserved case state. The p95 target in the PRD remains an aspirational 15 seconds for drafts under the documented workload; the ceiling is a failure limit, not a latency promise.

Persist known case facts and evidence references, not a promise that volatile data remains valid. Refresh order versions and stock before execution. Summarized conversation memory must preserve provenance and uncertainty; it cannot create approval. Do not persist a model's hidden reasoning. Persist concise decision explanations, source references, tool calls, and outcomes instead.

## 5. Traditional ML experiment

Build a ticket router predicting the six `TicketAnalysis.intent` classes from the initial customer text only. Generate or curate approximately 1000 synthetic/de-identified records with a documented label guide. Record the generator (model ID or "hand-written") for every record. Start with TF-IDF plus logistic regression. Use grouped 70/15/15 train/development/test partitions by source conversation and generation-template family; preserve class coverage and document the realized split sizes.

Fit text preprocessing, vocabulary, and classifier on the training split only. Tune on development data. Exclude agent replies, eventual resolutions, policy labels embedded in filenames, and post-outcome metadata. Strip or normalize identifying numbers only through a documented preprocessing experiment. A group split and duplicate audit are mandatory.

LLM-generated data carries the generating model's phrasing and template artefacts. They can inflate TF-IDF scores and favour the same model family as a router. Therefore also build a separate **hand-written challenge slice** of at least 60 messages (at least 10 per class), written without looking at generated examples and never used for tuning. Report results on the generated test split and the challenge slice separately; if the LLM router is from the same family as the generator, say so.

Compare the classical baseline and LLM router on the same held-out test messages and label taxonomy. The LLM side needs an approved live budget; without one, report it as not measured. Report macro-F1, per-class precision/recall/F1, confusion matrix, sample counts, model call cost, and latency. Scikit-learn defines these metrics and supports their computation. [S6]

Do not route writes directly from either classifier. Classification selects a workflow entry; rules and approval remain authoritative. Deploy the simpler router only if measured quality satisfies the chosen threshold. Otherwise keep it as a documented experiment.

## 6. Feedback and optimization

Store employee corrections as review candidates, not automatically correct training labels. Review, de-identify, and assign them to development or a new versioned holdout. Do not contaminate an existing locked test set by tuning on its individual failures without declaring a new evaluation protocol.

For each experiment, state a hypothesis, one primary change, fixed controls, dataset versions, metrics, failures, cost, and decision. Optimize a measured bottleneck: retrieval relevance, prompt behavior, model selection, caching, or tool latency. Cache only with tenant/permission/version-aware keys; never treat cached inventory as authoritative for a write.
