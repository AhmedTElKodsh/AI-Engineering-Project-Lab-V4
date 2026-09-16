# Learner-coach setup and use

## What exists and where

| Location | What it is |
|---|---|
| `.github/skills/commerce-ai-coach/` (this repository) | The installed `commerce-ai-coach` skill: `SKILL.md`, `references/`, `scripts/coach.py`, `tests/`, and `agents/openai.yaml`. It has no starter snapshot, because this repository already is the project. |
| `commerce-ai-coach/` (V4 bundle root, outside this repository) | The standalone copy of the same skill **plus** `assets/project-template/`, a snapshot of this repository used to start a fresh workspace. Zip this folder to share the skill. |
| `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/` | Lightweight guidance for assistants that do not load skills. |

The two skill copies are identical apart from `assets/`. Edit the standalone copy first, then re-copy it here without `assets/`. The V4 bundle's `tools/verify_v4.py` reports any drift.

Nothing here installs a skill into an account, creates a GitHub repository, provisions a database, or starts an autonomous service.

## Choosing the skill location for your host

The skill folder name must equal the skill's `name` (`commerce-ai-coach`), as the Agent Skills specification requires. [S14] Keep **one** repository copy and move it to the location your tools read:

| Host | Repository location it reads | Notes |
|---|---|---|
| GitHub Copilot (cloud agent, code review, CLI, VS Code/JetBrains agent mode) | `.github/skills/`, `.claude/skills/`, or `.agents/skills/` | Installed at `.github/skills/` by default. [S13] |
| Claude Code | `.claude/skills/` | Move the folder there if you use Claude Code; Copilot still finds it. |
| OpenAI Codex | `.agents/skills/` (from the working directory up to the repository root) | Move the folder there if you use Codex; Copilot still finds it. `agents/openai.yaml` supplies Codex UI metadata. |

If you move the folder, update the helper paths in `AGENTS.md` and `learning/PROGRESS_PROTOCOL.md`. Availability and activation behavior still depend on the host and its permissions; this delivery does not certify any host. Repository instruction support also varies by client. [S9]

## Helper commands

The helper uses only the Python standard library and needs Python 3.10 or newer. Use `python3` instead of `python` where that is your command. From this repository's root:

```bash
python .github/skills/commerce-ai-coach/scripts/coach.py status      # progress summary and next dependency-ready task
python .github/skills/commerce-ai-coach/scripts/coach.py validate    # structural check of learning/progress.json
python .github/skills/commerce-ai-coach/scripts/coach.py status --json
```

When the skill sits inside a repository's `.github/skills`, `.claude/skills`, or `.agents/skills` folder, the helper finds the project root automatically. Otherwise pass `--project PATH`. Both commands are read-only and make no network calls. `validate` checks task IDs, dependencies, status and mastery rules, and that evidence paths stay inside the project and exist. It cannot verify that recorded tests really passed or assess understanding.

## New workspace from the standalone skill

From the V4 bundle root (or wherever the standalone `commerce-ai-coach/` folder is):

```bash
python commerce-ai-coach/scripts/coach.py init --project ./my-commerce-support-copilot --install-skill
python commerce-ai-coach/scripts/coach.py status --project ./my-commerce-support-copilot
```

`init` copies the bundled snapshot into a **new, nonexistent directory** and refuses an existing destination. `--install-skill` also copies the skill (without its snapshot) into the new project's `.github/skills/commerce-ai-coach/`. It makes no network calls, initializes no Git history, and installs no dependencies. `init` is never used inside an existing project, and it is unavailable in a repository-installed copy, which has no snapshot.

## Beginning a session

> Use commerce-ai-coach. Read README.md, AGENTS.md, my learner profile, and progress. Start or resume the next dependency-ready task in guide mode. Give me one small step, the concept it teaches, and the evidence you need. Do not build the whole project at once.

Useful mode switches:

> Review T010 against its acceptance criteria. Read my changed files and test output before suggesting fixes.

> Debug this retrieval failure. Separate ingestion, filtering, retrieval, and generation hypotheses. Start with the smallest reproduction.

> Pair with me on T018. Explain the transaction boundary, then help me implement one testable change.

> Interview me on the approval design. Ask one question at a time and tell me what a strong answer would include.

> Warm me up on what I finished earlier: two or three questions, one at a time, then continue with the next task.

> Give me a complete worked solution for this task, including tests. Leave my understanding unassessed until I explain it.

## Chat-only fallback

Attach or paste the current README, AGENTS, active task entry, relevant contracts, progress, `learning/PROGRESS_PROTOCOL.md`, and the code/logs being discussed. The coach can teach and review provided content without repository access. It must say when execution or saving is unavailable, label results as not run or learner-reported, and return a handoff you can save. A file uploaded in one chat is not guaranteed persistent memory in another.

## Progress and continuity

The current repository overrides the skill's starter snapshot. The coach reads evidence before changing status and follows `learning/PROGRESS_PROTOCOL.md`. It records software completion (`not_started`, `in_progress`, `blocked`, `done`) separately from mastery (`unassessed`, `needs_practice`, `demonstrated`). What the learner has shown, stated, or had corrected goes in numbered learning records under `learning/records/`; the learner's goal and target release level go in the Mission section of `learning/LEARNER_PROFILE.md`. `.github/instructions/learning.instructions.md` keeps assistants from rewriting that history.

No connector is required. Optional connected GitHub access should be used only for the repository/task the learner authorizes. Do not create issues, branches, PRs, commits, paid resources, or external messages merely because the skill can suggest them.

## Testing the coach itself

From the skill folder, `python -m unittest discover -s tests -v` tests the helper. `tests/behavioral_cases.json` lists host-level coaching scenarios; run them in your chosen host and judge the transcripts by hand. Helper tests are not proof of conversational behavior, automatic activation, or learning effectiveness.
