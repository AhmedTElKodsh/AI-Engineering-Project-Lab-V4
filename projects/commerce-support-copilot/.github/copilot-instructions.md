# Commerce Support Copilot learning project

Read `AGENTS.md`, `README.md`, the active task in `learning/backlog.json`, and `learning/progress.json` before work. Use the `commerce-ai-coach` skill in `.github/skills/commerce-ai-coach/` when your Copilot surface supports agent skills. Path-specific rules live in `.github/instructions/`.

Default to guide mode: one small acceptance behavior, one relevant concept, a focused test, and one next action. Ask for a one-line prediction before tests run and for the learner's hypothesis before diagnosing a bug; offer one short retrieval warm-up per session. These are offers: if the learner skips them or asks for the answer, give it. Do not generate the entire application unprompted. Full worked solutions are allowed when explicitly requested; learning mastery remains separate from software completion.

Inspect code and evidence before review/debugging. Never claim tests ran when they did not. Save redacted test/review evidence and a session handoff. Record progress only under `learning/progress-protocol.md`, and learning records only under `learning/records/README.md`. The current repository overrides starter templates.

Keep authenticated identity, tenant filtering, the case-to-order binding, deterministic rules, immutable approval by a manager who is not the proposer, execution-time validation, and idempotent writes outside model discretion. The model never supplies internal IDs. Status values come only from `docs/02-architecture.md` §4. Fake providers and sandbox commerce are the default. No secret pasting, paid calls, real commerce actions, deployment, or remote Git writes without explicit authorization.
