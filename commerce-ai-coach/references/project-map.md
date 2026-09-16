# Project map

Paths are relative to the project root. Read only what the current question needs.

| Question | Read |
|---|---|
| What is the product, and what is out of scope? | `docs/00_PROJECT_BRIEF.md`, `docs/01_PRD.md` §2 |
| Which business rule applies? | `docs/01_PRD.md` §3 (BR01-BR08) |
| What must a requirement satisfy? | `docs/01_PRD.md` §4-§5 (FR01-FR14, NFR01-NFR08) |
| Which status values and transitions are allowed? | `docs/02_ARCHITECTURE.md` §4 (the only source) |
| Where does code go? | `docs/02_ARCHITECTURE.md` §5 |
| Tables, constraints, indexes, hashing | `docs/03_DATA_MODEL.md` |
| HTTP endpoints, schemas, tools, error codes | `docs/04_API_AND_TOOL_CONTRACTS.md` |
| Prompts, retrieval, run limits, routing classifier | `docs/05_AI_AND_RAG_DESIGN.md` |
| Datasets, metrics, failure matrix, CI stages | `docs/06_EVALUATION_AND_TESTING.md` |
| Roles, secrets, redaction, rate limits, incidents | `docs/07_SECURITY_AND_OPERATIONS.md` |
| Milestones and release levels | `docs/08_ROADMAP.md` |
| A task's definition | `docs/09_BACKLOG.md` or `learning/backlog.json` (same content) |
| Why a decision was made | `docs/10_RISKS_AND_DECISIONS.md`, `learning/DECISIONS.md` |
| Final demo and portfolio artifacts | `docs/11_PORTFOLIO_AND_DEMO.md` |
| Official references and version policy | `docs/12_SOURCES_AND_VERSION_POLICY.md` |
| Skill locations and helper commands | `docs/13_COACH_SETUP.md` |
| Requirement-to-task-to-test mapping | `docs/TRACEABILITY.md` |
| Worked plan for T001 | `docs/plans/01_FOUNDATION.md` |
| Development scenario seeds and their schema | `examples/evaluation_seed.jsonl`, `examples/README.md` |
| Learner facts, preferences, and mission (target release level) | `learning/LEARNER_PROFILE.md` |
| What the learner has shown, stated, or had corrected | `learning/records/` (format in its `README.md`) |
| Retrieval warm-up material | `teach_back` and `concepts` of `done` tasks in `learning/backlog.json`, plus `learning/records/` |
| Recorded progress and its rules | `learning/progress.json`, `learning/PROGRESS_PROTOCOL.md` |
| Previous session handoffs | `learning/SESSION_LOG.md` |
| Modes, hint ladder, mastery labels | `learning/CURRICULUM.md` |
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
