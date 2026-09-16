# Delivery roadmap

**Planning baseline:** 1.1.0. Milestones group related work; they are not calendar promises and do not by themselves define a release level. No duration is implied.

| Milestone | Tasks | Exit deliverable |
|---|---|---|
| M0: Foundation | T001-T003 | A tiny service, log redaction, and reproducible tests; explicit synthetic business fixtures. |
| M1: Typed model feature and evaluation baseline | T004-T007 | Structured extraction through a fake-first adapter, with baseline evaluation. |
| M2: Evidence-backed read-only product | T008-T012 | Tenant-safe knowledge lifecycle, grounded drafts, read-only UI; hybrid retrieval experiment (T012, portfolio). |
| M3: Tools and persistent workflow | T013-T016 | Authorized reads, deterministic rules, bounded graph, and safe pause/resume. |
| M4: Approved sandbox action | T017-T020 | Immutable approval and one deduplicated replacement; external-uncertainty simulation (T019, portfolio). |
| M5: Measured AI and ML engineering | T021-T024 | Expanded safety/evaluation suite, traces, classifier, and comparative experiments. |
| M6: Operational hardening | T025-T028 | Deployment identity, queues, containers, recovery, load and spending controls. |
| M7: Portfolio release | T029-T030 | Frozen evidence, reproducibility, failure analysis, and a defensible demo. |

## Release levels

The backlog's **Required for** field is authoritative. A task required for a lower level is also required for every higher level.

| Level | Required tasks | Not required at this level |
|---|---|---|
| Read-only demo | T001-T011 | T012 and everything from T013 |
| Sandbox workflow MVP | Read-only tasks plus T013-T018 and T020 | T012, T019, T021-T030 |
| Complete portfolio | All thirty tasks | - |

`tools/verify_v4.py` (V4 bundle) checks that no task depends on a task from a higher level.

## Recommended route

Complete dependencies before marking a task done. Several work packages can be studied in parallel, but the solo learner should keep one active implementation task. The coach recommends the earliest dependency-ready task unless the learner chooses another. Task IDs are stable identifiers, not proof that every lower-numbered task must precede every higher-numbered one.

T001 -> T002/T003 -> T004 -> T005 -> T006 -> T007 establishes the first baseline. T008 -> T009 -> T010 -> T011 produces a read-only demo. T014 (pure rules) can start right after T004; T013 -> T015 -> T016 -> T017 -> T018 -> T020 produces the first approved sandbox action. T012 and T019 are portfolio work that deepens retrieval and reliability.

## Scope gates

Read-only demo requires T001-T011 and their safety tests. Sandbox workflow MVP additionally requires T013-T018 and T020; the full locked evaluation set, external-write reconciliation, and public deployment are not implied. The complete portfolio track requires all thirty work packages. M5-M6 expand assurance but do not postpone fundamental authorization or duplicate prevention until after the first write.

## Working cadence

At session start, read progress and choose one concrete deliverable. Break a work package into small testable steps. At session end, save changed files, test evidence, a short review, an understanding check when appropriate, and the next exact action. Record blockers rather than inventing progress.

## Just-in-time detail

The PRD, contracts, backlog, and dependency graph cover the whole project. `docs/plans/01_FOUNDATION.md` supplies the first detailed implementation sequence. For each later task, the coach derives a small file-level/test-level plan from its acceptance criteria and current repository, then asks the learner to implement the next step. This avoids writing an entire solution before the learner has encountered the problem.

## Extensions after M7

Customer-uploaded damage images; MCP wrapping existing read tools; a justified fine-tuning experiment; an additional return/delivery workflow. Each needs a new requirement, evaluation cases, scope/budget decision, and tasks. None can waive the base safety gates.
