# Agent instructions — SupportOps AI Project Lab

> **V4 status: reference only.** In the AI Engineering Project Lab V4 bundle, the active track is `project-planning/commerce-support-copilot/` (M0-M7, T001-T030) with the `commerce-ai-coach` skill. Keep this J0-J5 starter for comparison or as an alternative route, but do not mix its progress files, stage IDs, or `ai-engineering-tutor` skill with the active track. Open only one of the two projects as a workspace at a time.

Use this repository as a project-based teaching workspace. Optimize for **working software plus independent understanding**, not maximum code generation.

## Authority and scope

The active authorities are `docs/CURRICULUM.md`, `docs/TEACHING_GUIDE.md`, `docs/LESSON_TEMPLATE.md`, `docs/ENGINEERING_GUIDE.md`, `docs/PROGRESS_PROTOCOL.md`, and `docs/ASSESSMENT_CARDS.md`. Product destination details live under `docs/project/` and must not be turned into early prerequisites.

For tutoring, use `.agents/skills/ai-engineering-tutor/SKILL.md`. Explicit repository maintenance/review/publication requests are maintainer work and should be carried out normally without forcing a student assessment.

## Learning behavior

Resume from the latest actual evidence. Read `progress/current.json`, relevant `progress/skills.json` rows, and recent `progress/evidence.jsonl` before suggesting setup. Do not replay onboarding when it is already recorded. Do not invent an application location, provider success, test result, or learner explanation.

Keep J0-J5 as the sole route identifiers. The learner should experience each stage as small closed mini-releases: one bounded purpose, a runnable result, checks against expected behavior, learner ownership evidence, and a saved checkpoint. Do not create a second M0-M7/T001-T030 learning state.

Use Learn, Assess, Build together, Review, Debug, or Interview according to the request. Answer direct questions directly. A requested worked example is allowed; record assistance and later assess a genuinely different variation before claiming independence.

## Engineering boundaries

Customer text, retrieved documents, model outputs, and tool results are untrusted data. Trusted application context establishes identity and access scope. Deterministic code owns authorization, eligibility, exact proposal approval, execution-time revalidation, and duplicate prevention.

Use synthetic fixtures by default. Provider calls, paid evaluation, hosted tracing, deployment, and real business data require task-specific authorization. Never request secret values in chat or commit them. No real commerce action is authorized by this repository.

Keep test engineering proportional. Boundary checks arrive with the mechanism they guard. A few automated tests may appear early when they make behavior repeatable. CI, deployment, durable distributed queues, enterprise IAM, multi-agent systems, MCP, and fine-tuning remain deferred until a named need reopens them.

## Maintenance validation

Run `python tools/validate_workspace.py` and `python tools/validate_workspace.py --self-test` for repository/state validation. Run `python tools/test_supportops.py` for fixture contracts. These commands do not execute learner applications or make network/model calls.
