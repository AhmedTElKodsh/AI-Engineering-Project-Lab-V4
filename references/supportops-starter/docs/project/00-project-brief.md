# Project brief

> **Curriculum scope note:** This file describes destination product architecture and engineering options. Implement only the slice justified by the active J0-J5 mini-release; it is not a day-one checklist.

**Baseline:** 1.0.0 | **Status:** proposed implementation baseline, not validated customer demand

## Product thesis

A support employee should resolve a damaged-item case without manually searching multiple policy documents and operational systems. The copilot assembles evidence, recommends an eligible action, and lets an authorized manager inspect and approve the exact change. The system should be useful even when it chooses clarification or escalation rather than an action.

## Two different copilots

The **product copilot** is the application the learner will build. The **learner coach** is the separate `ai-engineering-tutor` skill that guides that construction. The coach does not operate a real store, and its progress file is not the product's runtime conversation database.

## Working assumptions

| Assumption | Chosen baseline | Revisit when |
|---|---|---|
| Learner | Junior with basic Python functions, lists, dictionaries, and terminal use | Initial diagnostic reveals a gap; add a small prerequisite exercise |
| Experience | No prior LangChain, LangGraph, retrieval, or production AI experience required | Learner demonstrates existing skill and can move faster |
| Format | Solo project, small reviewable increments, text-first English interface | Learner explicitly requests a different learning style |
| Store | Fictional small-appliance retailer; no real customer or payment data | Authorized real-data pilot has a separate privacy review |
| Device | Local development; containers added after first Python slice | Local constraints require a remote development environment |
| Providers | Fake adapter first; configurable hosted LLM later; local embeddings | Provider availability, cost, or data rules change |
| Business action | Create one sandbox replacement request; never charge, refund, or ship | Separate approved feature changes the product boundary |
| Calendar | Store business timezone is Africa/Cairo; timestamps stored in UTC | Store configuration changes |
| Budget | Offline by default; live calls require a user-approved cap | Learner authorizes a specific run or ongoing cap |

## What the learner should demonstrate

Connect Python, types, HTTP, SQL, and tests into a working service. Use model APIs and validated structured outputs without treating outputs as trusted facts. Build and evaluate retrieval. Design bounded tool workflows and human approval. Diagnose failures using traces and tests. Compare a simple supervised model with an LLM. Package, deploy, monitor, and explain the application with evidence.

This track does not claim to cover every AI-engineering specialization. It does not require foundation-model pretraining, GPU cluster administration, research-level computer vision, or advanced distributed training. Optional extensions add selected topics only after the base project works.

## Success for the business hypothesis

Measure correct resolutions, employee edits, clarification quality, and time spent on a defined task. A future real-user pilot can compare assisted and unassisted sessions using equivalent cases and a fixed scoring rubric. Do not claim time savings or revenue impact from a synthetic demo.

## Success for learning

For each work package, preserve software evidence and a separate understanding check. Working code can be marked complete while understanding remains unassessed. The coach should adapt help to the learner, provide full examples when explicitly requested, and never confuse copying working code with independently explaining it.

## Project boundaries

One modular Python application, one database, one workflow, one simple interface. Introduce tools only when the milestone needs them. Establish authorization, tests, evaluation seeds, and redacted logs early. Add operational depth rather than multiplying agents or databases.
