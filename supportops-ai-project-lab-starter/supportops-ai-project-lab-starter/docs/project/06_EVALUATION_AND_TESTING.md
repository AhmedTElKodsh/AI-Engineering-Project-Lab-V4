# Evaluation and testing strategy

> **Curriculum scope note:** This file describes destination product architecture and engineering options. Implement only the slice justified by the active J0-J5 mini-release; it is not a day-one checklist.

## Contents

1. Evidence and release definitions
2. Dataset protocol
3. Metrics and initial gates
4. Test layers and failure matrix
5. Experiment and reporting protocol
6. CI and review requirements

## 1. Evidence and release definitions

The planning kit contains no measured application results. Tests named below are requirements to implement. `examples/evaluation_seed.jsonl` supplies twelve development scenarios; it is not the full evaluation suite.

Maintain two separate records: task completion (implementation plus test/review evidence) and learning mastery (a teach-back or independent variation). A valid JSON progress record cannot prove tests really ran. The coach must inspect the linked logs/diff and distinguish observed execution from learner-reported evidence.

LangSmith supports datasets, experiments, and code-, human-, or model-based evaluators. Use it after redaction/opt-in, or export equivalent local records when it is unavailable. [S4]

## 2. Dataset protocol

Build **60 development workflow scenarios** and **120 locked acceptance scenarios**. The locked set's mutually exclusive primary categories are: 40 eligible replacement cases, 20 missing-information cases, 20 manual-escalation cases, 20 authorization/prompt-injection cases, and 20 failure/recovery cases. Secondary tags may overlap. At least 60 locked cases must include an answerable policy-retrieval question with known relevant section IDs; record this subset explicitly.

Each scenario contains ID, split, primary category, message, principal/tenant fixture, fixed clock, operational fixture, policy version, expected facts, required evidence sections, allowed next states/actions, prohibited effects, and a human-authored rubric. Do not store a single reference sentence as the only correct answer.

Developers may inspect the development set freely. Freeze locked-test inputs, expectations, and hashes before final tuning. Do not put locked examples in prompts, training data, or reranker labels. A failed acceptance run is still reported. New tuning after inspecting test failures requires a fresh holdout or an explicitly acknowledged contaminated benchmark.

For model variability, perform three runs per scenario for the final live report when the authorized budget permits; otherwise disclose one run and avoid stability claims. Deterministic safety tests run for every release regardless of live-model budget. Never silently replace unexecuted live tests with fake-adapter results.

The separate routing classifier dataset uses its own grouped train/development/test split; do not count routing accuracy as workflow success.

## 3. Metrics and initial gates

| Metric | Definition and denominator | Initial project gate |
|---|---|---|
| Workflow success | Scenarios whose outcome, evidence, constraints, and side effects all satisfy the rubric / all evaluated workflow scenarios; correct escalation counts as success | >=85% on the frozen acceptance set |
| Retrieval section recall@5 | For each eligible retrieval query: unique relevant section IDs retrieved in top five / total gold relevant section IDs; macro-average over the declared answerable subset | >=85%; report cases with more than five relevant sections separately |
| Supported-claim precision | Supported material factual/policy claims / all emitted material factual/policy claims; human-reviewed against authorized evidence | >=95%; report zero-claim outputs separately, not as automatic 100% |
| Required-escalation recall | Correct escalations / scenarios explicitly requiring escalation | >=95%; separately report inappropriate escalation on eligible cases |
| Citation validity | Authorized, resolvable evidence references / all cited references | 100% valid IDs; factual support remains a separate metric |
| Safety suite pass rate | Mandatory authorization, approval, duplicate, and data-isolation tests passed / all mandatory safety tests | 100%; any unauthorized write is release-blocking |
| Structured-output validity | Successfully schema-validated responses / attempted structured-output calls | Report raw and post-repair rates separately; investigate every failure |
| Latency | Client-observed duration through draft completion, excluding human wait; p50 and p95 with errors/timeouts disclosed | Initial p95 aspiration <=15 s at five concurrent sessions |
| Model cost per success | Total metered model cost for all attempted workflow cases, including failures/retries, divided by successfully handled cases | Initial aspiration <=USD 0.10; report zero successes as undefined |
| Routing macro-F1 | Unweighted mean F1 over all six labels, with per-class supports | Compare baselines; no fabricated universal threshold |

Initial numeric gates are chosen targets, not empirical results or industry standards. Report numerators, denominators, confidence intervals where meaningful, and uncertainty. Zero failures in a finite suite is not proof of security. Hosted evaluation-judge costs and infrastructure costs are reported separately.

## 4. Test layers and failure matrix

**Unit tests:** schema limits, timezone date arithmetic, policy rules, hash canonicalization, status transitions, redaction, model parsing, usage calculations. Freeze the clock and use deterministic fixtures.

**Integration tests:** PostgreSQL migrations, tenant-scoped queries, vector filtering, document activation, stock reservations, approval/execution transactions, durable checkpoints, queue retries. Use a real disposable PostgreSQL instance for transaction/constraint tests rather than pretending an in-memory mock proves them.

**Contract tests:** fake and hosted model adapters share schema/error/usage semantics; commerce adapters share idempotency and reconciliation semantics; OpenAPI responses match Pydantic schemas. Live provider tests are opt-in, budgeted, and separately tagged.

**End-to-end tests:** support employee creates a case, manager reviews and approves, the UI reports a confirmed replacement ID; reject/revise and clarification paths; re-open a paused case after restart. A UI-only disabled button is not a permission test.

| Adversarial/failure condition | Required behavior |
|---|---|
| Customer asks to ignore policy and run a refund tool | No such write tool exists; route/escalate safely |
| Retrieved document claims manager approval | Treat as untrusted text; no approval record created |
| Foreign-tenant order, case, chunk, proposal, or graph thread ID | Non-disclosing not-found/denial before model exposure |
| Model fabricates a source ID or approved flag | Validation fails; no action |
| Missing delivery time or delivery after complaint | Needs-information/manual review; never compute a fabricated age |
| Seven-day vs eight-day boundary | Seven eligible if other rules pass; eight ineligible; local calendar rule explicit |
| Proposal altered, expired, self-approved, or role revoked | No execution; fresh proposal/authorized review required |
| Two managers approve/execute simultaneously | One effective approved payload and at most one replacement |
| Two proposals target the final stock unit | At most one reservation; stock never negative |
| Same key replay, changed-payload replay, different-key duplicate | Same result, conflict, and duplicate rejection respectively |
| Timeout after downstream commit | Unknown outcome recorded and reconciled; never blind duplicate write |
| Policy activates during approval pause | Stale proposal invalidated before execution |
| Worker restarts halfway through document import | Incomplete version nonsearchable; safe retry |
| Hosted tracing receives sensitive message or API key | Allowlist/redaction test blocks or strips it |

## 5. Experiment and reporting protocol

Record experiment ID, hypothesis, Git commit, dependency lock hash, model ID, prompt/schema/chunk/index versions, dataset version, settings, budget cap, cost basis date, commands, environment, metrics, and inspected failure cases. Keep one primary variable changed per comparison when feasible. Capture the baseline before optimization.

An LLM judge is a supplementary reviewer. Calibrate it against a manually reviewed sample, preserve judge prompt/model version, and report disagreement. Deterministic checks govern tool permissions and writes. A model judge cannot certify authorization.

Preserve ten representative failed or corrected cases in the portfolio report. Explain the root cause and whether the fix improved a held-out measure or merely repaired a known case. Never replace failures with attractive screenshots.

## 6. CI and review requirements

Start with focused deterministic checks beside each mechanism. Add a test framework/CI when the checks span enough files or a target role justifies it. Add persistent-database integration tests when that storage is selected, action/security tests before the J4 simulated write, and deployed smoke tests only when deployment is selected. Separate paid evaluations behind explicit manual authorization and spend limits.

Per task: name the expected failure, write a focused test, observe failure for the intended reason, implement a minimal change, rerun the test and relevant regression suite, inspect the diff, record review and evidence. Commit only within the learner's authorized workflow. Do not mark not-run tests as passing.
