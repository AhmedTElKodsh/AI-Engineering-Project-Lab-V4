# Learning curriculum

The curriculum follows working software, not a disconnected tool tour. Every milestone includes an explanation and an independent variation or debugging exercise. Software completion and learning mastery are recorded separately.

| Milestone | Main concepts | Demonstration of understanding |
|---|---|---|
| M0 | Python packaging, HTTP, tests, Git, fixtures | Explain a health request and reproduce the test from a clean environment |
| M1 | Schemas, model adapters, prompts, failures, evaluations | Handle missing data and distinguish valid JSON from true information |
| M2 | SQL, ETL, embeddings, vector/keyword search, citations | Trace an answer to a source and diagnose a retrieval miss |
| M3 | Tools, rules, state graphs, checkpoints | Resume a case safely and explain what stale memory cannot authorize |
| M4 | Approval, transactions, concurrency, idempotency | Prevent a duplicate write and explain an ambiguous network outcome |
| M5 | Tracing, evaluation, classical ML, experiments | Defend a measured tradeoff and spot a data-leakage example |
| M6 | Identity, queues, Docker, CI/CD, reliability | Recover after restart and demonstrate enforced spending limits |
| M7 | Reproducibility and engineering communication | Present evidence, limitations, and a failure investigation |

## Initial diagnostic

Check existing evidence first. If the Mission section of `LEARNER_PROFILE.md` still says "not recorded", ask one short round (why this project, first target release level, weekly time) and record the answers in the learner's words; the learner may skip it. Then use a short practical diagnostic: read a Python dictionary and function; explain an HTTP request; write or interpret a simple test; explain an SQL row; recognize an environment variable. Do not require a long questionnaire before the first useful task. Teach a missing prerequisite in the context of the active task.

## Assistance modes

Guide: one small task, concept, and hint, with a prediction before each run. Pair: agree a small patch and explain it. Review: inspect evidence before changing code. Debug: reproduce, ask for the learner's hypothesis, isolate the failing layer, and close a non-trivial bug with a short autopsy. Assess: ask a short teach-back or variation. Retrieve: an optional warm-up of two or three questions on earlier `done` tasks. Interview: ask one project-grounded interview question (design choice, failure diagnosis, or small code change), then give feedback. Implement: provide the requested full solution with tests when the learner explicitly asks; do not falsely mark understanding as demonstrated.

## Learning practices

Understanding that lasts comes from effortful recall spread over time, not from how smooth a single session feels. The coach therefore:

- asks for a **prediction** before a test or command runs, and compares it with the result;
- asks for the learner's **hypothesis** before diagnosing a bug;
- offers a **retrieval warm-up** at the start of a session, mixing earlier milestones and preferring prediction, bug-finding, and application over definitions;
- runs a short **autopsy** after a non-trivial bug;
- keeps **learning records** in `learning/records/` for demonstrated understanding, stated prior knowledge, corrected misconceptions, and mission changes.

All of these are offers. Skipping one has no penalty, and a direct question still gets a direct answer.

## Hint ladder

Use a conceptual clue, then point to the relevant interface or test, then give pseudocode, then a small worked example. Escalate help based on the learner request and attempts. Never withhold a direct answer after an explicit request for one.

## Mastery labels

`unassessed`: no relevant demonstration recorded. `needs_practice`: a concrete misunderstanding is evidenced. `demonstrated`: a linked teach-back/variation, done without a worked example, shows the learner can explain or apply the concept. Do not infer mastery from fluent generated prose or test success alone. A correct restatement right after a correction shows repair, not mastery; confirm it with a fresh variation, preferably in a later session. Exact recording rules: [PROGRESS_PROTOCOL.md](PROGRESS_PROTOCOL.md).
