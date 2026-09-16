# Project map

Paths are relative to the project root. Read only what the current question needs.

| Question | Read |
|---|---|
| What is the product, and what is out of scope? | `docs/00-project-brief.md`, `docs/01-prd.md` §2 |
| Which business rule applies? | `docs/01-prd.md` §3 (BR01-BR08) |
| What must a requirement satisfy? | `docs/01-prd.md` §4-§5 (FR01-FR14, NFR01-NFR08) |
| Which status values and transitions are allowed? | `docs/02-architecture.md` §4 (the only source) |
| Where does code go? | `docs/02-architecture.md` §5 |
| Tables, constraints, indexes, hashing | `docs/03-data-model.md` |
| HTTP endpoints, schemas, tools, error codes | `docs/04-api-and-tool-contracts.md` |
| Prompts, retrieval, run limits, routing classifier | `docs/05-ai-and-rag-design.md` |
| Datasets, metrics, failure matrix, CI stages | `docs/06-evaluation-and-testing.md` |
| Roles, secrets, redaction, rate limits, incidents | `docs/07-security-and-operations.md` |
| Milestones and release levels | `docs/08-roadmap.md` |
| A task's definition | `docs/09-backlog.md` or `learning/backlog.json` (same content) |
| Why a decision was made | `docs/10-risks-and-decisions.md`, `learning/decisions.md` |
| Final demo and portfolio artifacts | `docs/11-portfolio-and-demo.md` |
| Official references and version policy | `docs/12-sources-and-version-policy.md` |
| Skill locations and helper commands | `docs/13-coach-setup.md` |
| Requirement-to-task-to-test mapping | `docs/traceability.md` |
| Worked plan for T001 | `docs/plans/01-foundation.md` |
| Development scenario seeds and their schema | `examples/evaluation_seed.jsonl`, `examples/README.md` |
| Learner facts, preferences, and mission (target release level) | `learning/learner-profile.md` |
| What the learner has shown, stated, or had corrected | `learning/records/` (format in its `README.md`) |
| Retrieval warm-up material | `teach_back` and `concepts` of `done` tasks in `learning/backlog.json`, plus `learning/records/` |
| Recorded progress and its rules | `learning/progress.json`, `learning/progress-protocol.md` |
| Previous session handoffs | `learning/session-log.md` |
| Modes, hint ladder, mastery labels | `learning/curriculum.md` |
| Record templates | `learning/templates/` |
| Path-specific assistant rules (tests, migrations, learning files) | `.github/instructions/` |

## Task fields in `learning/backlog.json`

`id`, `title`, `milestone`, `required_for` (`read_only_demo`, `sandbox_mvp`, `portfolio`), `depends_on` (direct prerequisites only), `requirements`, `files` (planned, excluding tests), `test_path`, `additional_tests`, `acceptance`, `teach_back`, `concepts`.

## Minimum reading per task

1. The task entry.
2. Each requirement row it names in the PRD.
3. The contract section for any schema, endpoint, table, or status it touches.
4. The planned files that already exist in the repository, and their tests.

Do not load the whole documentation set for a small step.
