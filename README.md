# AI Engineering Project Lab V4

**Active track: Commerce Support Copilot (milestones M0-M7, tasks T001-T030).** Planning baseline 1.1.0, prepared 2026-09-15. The application itself is not implemented yet; this bundle holds the plans, the learner records, and the coaching skill.

## What is in this folder

| Path | Status | Purpose |
|---|---|---|
| `project-planning/commerce-support-copilot/` | **Active** | The learner's project repository: plans, backlog, progress records, assistant instructions, and the installed `commerce-ai-coach` skill in `.github/skills/`. Push this folder as its own Git repository. |
| `commerce-ai-coach/` | **Active** | Standalone copy of the coaching skill, including `assets/project-template/` for starting a fresh workspace. Zip this folder to share or import the skill. |
| `tools/verify_v4.py` | Maintainer tool | Checks backlog/traceability consistency, seeds, links, skill format, copy drift, and runs the helper tests. `--sync` refreshes the derived copies. |
| `DELIVERY_VALIDATION.md` | Report | What was checked for this bundle, and what was not. |
| `REVIEW_FINDINGS_2026-09-15.md` | Report | The planning review and how each finding was resolved. |
| `COACH_IMPROVEMENTS_2026-09-15.md` | Report | Ideas taken from two outside learning toolkits, and which ones were applied (coach 1.2.0). |
| `supportops-ai-project-lab-starter/` | **Reference only** | An alternative J0-J5 route for the same product idea. Do not use its progress files, stage IDs, or `ai-engineering-tutor` skill alongside the active track. |

## Start here

1. Open `project-planning/commerce-support-copilot/` as your workspace, not this V4 folder. Assistants then see one set of instructions and one progress file.
2. Read its `README.md`, then `docs/08_ROADMAP.md`.
3. Ask your assistant: *"Use commerce-ai-coach. Read the plans and progress, then start T001 in guide mode."*

Skill locations per host (GitHub Copilot, Claude Code, Codex) are described in `project-planning/commerce-support-copilot/docs/13_COACH_SETUP.md`.

## Maintaining the bundle

Edit the plans in `project-planning/commerce-support-copilot/` and the skill in `commerce-ai-coach/`. Then run:

```bash
python tools/verify_v4.py --sync
```

That command recreates the installed skill copy and the template snapshot, then runs every check. Never edit those two derived copies by hand.

## Setup status

The three one-time "Finish setup" steps are already applied in this GitHub repository (2026-09-16):

1. The files from `project-planning/commerce-support-copilot/github-updates/` now live in `project-planning/commerce-support-copilot/.github/`, and `github-updates/` is gone.
2. `python tools/verify_v4.py --sync` created the installed skill at `project-planning/commerce-support-copilot/.github/skills/commerce-ai-coach/` and refreshed the template snapshot. It reports `16 checks passed, 0 problems`.
3. The obsolete root `SKILL.md` was removed.

A fresh clone needs no manual steps. Run `python tools/verify_v4.py` to confirm.
