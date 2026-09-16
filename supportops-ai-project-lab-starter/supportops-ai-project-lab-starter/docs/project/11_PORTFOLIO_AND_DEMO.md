# Portfolio, release evidence, and demo

> **Curriculum scope note:** This file describes destination product architecture and engineering options. Implement only the slice justified by the active J0-J5 mini-release; it is not a day-one checklist.

## What the final repository should communicate

Show that you can turn a probabilistic model into a testable application with a clear operational boundary. Present evidence for quality, cost, failure handling, and authorization. A list of libraries is not the central achievement.

## Required final artifacts

| Artifact | Required content |
|---|---|
| Reproducible README | Setup, modes, exact tested versions, offline commands, demo accounts, and limitations |
| Architecture walkthrough | Components, data flow, trust boundary, model-versus-code decisions, and approval lifecycle |
| Evaluation report | Dataset versions, metrics/denominators, baseline comparisons, target outcomes, contamination status, and unmeasured items |
| Data card | Synthetic/real provenance, generation process, labels, grouping, partitions, licenses, and limitations |
| Model card | Hosted model IDs, classical model pipeline, intended uses, failures, costs, and restrictions |
| Failure casebook | Ten representative failures/corrections with root cause, fix, regression test, and evidence |
| Security/reliability report | Cross-tenant denial, approval binding, concurrency, restart, reconciliation, and secret/redaction checks |
| Deployment runbooks | Configuration, migrations, health, rollback, backup, restore, and spending controls |
| Demo script | Fixed synthetic cases, expected effects, reset procedure, and no real commerce actions |

These are future deliverables produced as the learner reaches the relevant J4/J5 or optional depth work; they are not completed results in this planning kit.

## Demonstration sequence

Open the synthetic damaged-item case and show extracted fields. Display policy citations and current order/stock facts. Show the proposed exact replacement and its expiry. Switch to the separate manager account, approve, execute, and show the confirmed request ID and audit record. Replay the request and show that no second replacement is created.

Next, submit a customer message or document containing malicious instructions; show that it cannot grant approval or access another tenant. Finally, demonstrate an interrupted/restarted workflow or an ambiguous downstream outcome and its safe reconciliation. Finish with one measured baseline improvement and one rejected experiment.

## Claims to make only when supported

Use phrasing such as "passed these 32 authorization tests," "retrieval section recall changed from X to Y on dataset version Z," or "p95 was X under this workload." Replace X/Y with measured results only. Do not state real-world time savings, universal accuracy, or production safety from synthetic tests. Report targets that were missed and live tests that were not run.

## Interview prompts

Explain why RAG cannot authorize a business action. Trace one answer to its evidence. Explain a database race and its constraint. Show a schema-valid hallucination. Defend using or rejecting the classical classifier. Explain how a checkpoint differs from an approval. Describe the next change you would make with a real authorized customer dataset.

## Completion standard

A reviewer can reproduce the deterministic suite from a clean checkout, inspect a real failure investigation, and understand exactly what the system does and does not guarantee. The learner can explain the key design choices without reading generated answers verbatim.
