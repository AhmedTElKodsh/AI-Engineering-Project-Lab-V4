# Commerce Support Copilot
## Project planning kit + learner workspace

**Planning baseline:** 1.1.0 | **Prepared:** 2026-09-15 | **Application status:** not implemented

Build an evidence-backed support copilot for a fictional e-commerce store. Start with a damaged-item replacement: analyze a ticket, retrieve applicable policy, inspect authorized live data, propose a resolution, obtain manager approval, and create exactly one sandbox replacement request.

This is a learning project, not a production-ready customer-support product. The repository contains the product and engineering plans, a sequenced backlog, learning records, and development examples. It does not contain a running API, model, database, CI workflow, or deployment. Commands in implementation plans are future instructions unless a verification record explicitly says they were executed.

## Start here

1. Read [the project brief](docs/00_PROJECT_BRIEF.md) and [the PRD](docs/01_PRD.md).
2. Read [the roadmap](docs/08_ROADMAP.md). Start with **T001**, not the entire stack.
3. Give your coding assistant [AGENTS.md](AGENTS.md), [the learner profile](learning/LEARNER_PROFILE.md), and [the progress record](learning/progress.json). The `commerce-ai-coach` skill is already installed at [.github/skills/commerce-ai-coach](.github/skills/commerce-ai-coach/SKILL.md), where GitHub Copilot discovers repository skills. For Claude Code or Codex, see [13_COACH_SETUP](docs/13_COACH_SETUP.md).
4. Follow [the first implementation plan](docs/plans/01_FOUNDATION.md). Keep evidence in `learning/evidence/`, session handoffs in `learning/SESSION_LOG.md`, and learning records in `learning/records/`.

Suggested first prompt:

> Use commerce-ai-coach. Read this repository's plans and progress. Start T001 in guide mode. Teach the minimum prerequisite, give me one small implementation step, and tell me what evidence to return. Do not build the whole application for me.

## Planning map

| File | Decision it controls |
|---|---|
| [00_PROJECT_BRIEF](docs/00_PROJECT_BRIEF.md) | Purpose, assumptions, boundaries, and learning outcomes |
| [01_PRD](docs/01_PRD.md) | Users, scope, requirements, acceptance criteria, and release gates |
| [02_ARCHITECTURE](docs/02_ARCHITECTURE.md) | Components, trust boundaries, workflow, and future code layout |
| [03_DATA_MODEL](docs/03_DATA_MODEL.md) | Tables, constraints, versioning, and transactions |
| [04_API_AND_TOOL_CONTRACTS](docs/04_API_AND_TOOL_CONTRACTS.md) | HTTP behavior, typed boundaries, tools, and action lifecycle |
| [05_AI_AND_RAG_DESIGN](docs/05_AI_AND_RAG_DESIGN.md) | Model interface, prompts, ingestion, retrieval, and routing classifier |
| [06_EVALUATION_AND_TESTING](docs/06_EVALUATION_AND_TESTING.md) | Test strategy, datasets, metrics, and evidence requirements |
| [07_SECURITY_AND_OPERATIONS](docs/07_SECURITY_AND_OPERATIONS.md) | Threat model, limits, privacy, failure recovery, and release operations |
| [08_ROADMAP](docs/08_ROADMAP.md) | Milestones, dependency order, and scope gates |
| [09_BACKLOG](docs/09_BACKLOG.md) | Thirty concrete work packages with release level, test criteria, and teach-backs |
| [10_RISKS_AND_DECISIONS](docs/10_RISKS_AND_DECISIONS.md) | Risks, explicit assumptions, decision log, and change control |
| [11_PORTFOLIO_AND_DEMO](docs/11_PORTFOLIO_AND_DEMO.md) | Final demonstration and evidence-driven presentation |
| [12_SOURCES_AND_VERSION_POLICY](docs/12_SOURCES_AND_VERSION_POLICY.md) | Official references and dependency verification policy |
| [13_COACH_SETUP](docs/13_COACH_SETUP.md) | Skill setup, GitHub Copilot instructions, and chat-only fallback |
| [Traceability](docs/TRACEABILITY.md) | Requirement-to-task-to-test mapping |
| [Progress protocol](learning/PROGRESS_PROTOCOL.md) | Task status values, evidence entries, and mastery rules |
| [Learning records](learning/records/README.md) | What the learner has shown, stated, or had corrected; steers step size and retrieval |

## Source of truth

The PRD owns product scope; the contracts own field names; `02_ARCHITECTURE.md` §4 owns status values and transitions; the backlog owns task definitions; `learning/progress.json` owns recorded progress, under the rules in `learning/PROGRESS_PROTOCOL.md`. `learning/backlog.json` is the machine-readable form of the backlog. Change the human and machine-readable forms together. Explicitly approved new project decisions supersede this baseline; record their consequences instead of silently rewriting history.

The standalone skill (outside this repository) includes an identical starter snapshot for initializing an empty workspace. The copy installed in `.github/skills/` omits that snapshot. After initialization, the working repository is authoritative. Never reset working progress from the bundled snapshot.

## Scope ladder

**Read-only demo:** T001-T011. **Sandbox workflow MVP:** add T013-T018 and T020 with their safety tests. **Complete portfolio track:** all thirty tasks, including hybrid retrieval, external-write reconciliation, ML comparison, queues, measured evaluation, and deployment. Each task's **Required for** field in the backlog is authoritative. Image analysis, MCP, fine-tuning, and new business workflows are extensions, not prerequisites.

No paid model call, cloud provisioning, external ticket creation, or production action is authorized by possessing these files. Begin with deterministic fake adapters and synthetic data. Obtain an explicit spending cap before live calls.
