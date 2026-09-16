# SupportOps AI Project Lab

> **V4 status: reference only.** In the AI Engineering Project Lab V4 bundle, the active track is `projects/commerce-support-copilot/` (M0-M7, T001-T030) with the `commerce-ai-coach` skill. Keep this J0-J5 starter for comparison or as an alternative route, but do not mix its progress files, stage IDs, or `ai-engineering-tutor` skill with the active track. Open only one of the two projects as a workspace at a time.

A project-based AI-engineering curriculum built around one evolving e-commerce support copilot.

The learner does **not** build an enterprise platform on day one. The route is a sequence of small, runnable releases that progressively become SupportOps AI. Every stage should let the learner build, run, inspect, test, explain, and stop at a useful result.

## Product mission

SupportOps AI helps an authenticated support employee understand a customer case, retrieve the applicable policy, inspect current operational facts through narrow tools, prepare a resolution, and—only after deterministic authorization and exact approval—simulate one safe replacement request.

Design rule: **documents explain policy; tools provide current operational facts; deterministic code owns identity, permissions, business rules, approvals, and effects.**

All bundled data is synthetic. No real refund, shipment, replacement fulfillment, outbound message, or customer-data upload is part of the base project.

## Learning route

| Stage | Closed runnable result |
|---|---|
| J0 | First provider-backed reply draft from a customer message and supplied policy text |
| J1 | Structured support-case intake with missingness, negation, uncertainty, and source evidence |
| J2 | Required transfer to a different support constraint without adding a new external API |
| J3 | Policy finder first, then a cited policy assistant with abstention |
| J4 | Scoped order lookup first, then bounded tool use and one simulated approved action |
| J5 | One reproducible SupportOps release with honest evaluation and independent change/debug/transfer |

J0-J5 are progress identifiers. Mini-release names are learner-facing stopping points, not a second progress schema.

## Start here

1. Read `AGENTS.md` if an AI coding/tutoring agent is involved.
2. Read `docs/curriculum.md` and only the active stage's assessment material.
3. Read `progress/current.json` before suggesting setup; newer actual learner evidence wins over an older snapshot.
4. Run `python tools/validate_workspace.py` to check repository structure/state.
5. Run `python tools/test_supportops.py` to validate the synthetic fixture contracts.

The recorded starter state is J0/Q0/0.3 with onboarding inherited and the first real execution/explanation still pending. That is a saved learning-state claim, not proof that the learner has never made an API call elsewhere.

## Repository map

- `docs/project/` — destination product architecture and planning. It describes where the project can grow; it is **not** a day-one checklist.
- `docs/curriculum.md` — active J0-J5 route and deferral triggers.
- `docs/teaching-guide.md` / `docs/lesson-template.md` — tutoring behavior.
- `docs/assessment-cards.md` — held-back assessment contracts by stage.
- `progress/` — learner evidence/state; do not reset from templates.
- `fixtures/support/` — frozen synthetic cases and failure payloads.
- `.agents/skills/ai-engineering-tutor/` — project-specific Tutor/Agent skill.
- `.claude/skills/ai-engineering-tutor/` — mirror for hosts that look there.
- `tools/` — read-only workspace/fixture validation.

## What this repository does not claim

Static validation does not establish model quality, production safety, learning effectiveness, job readiness, or that a learner understands generated code. Live provider behavior, hosted tracing, deployment, real-data use, and business integrations require separate evidence and explicit authorization.
