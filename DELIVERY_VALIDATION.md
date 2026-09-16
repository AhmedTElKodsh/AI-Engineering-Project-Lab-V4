# Delivery validation report: V4 bundle

Checked on 2026-09-15 after applying the planning review (see `REVIEW_FINDINGS_2026-09-15.md`).

## How to reproduce

```bash
python tools/verify_v4.py          # checks only
python tools/verify_v4.py --sync   # refresh derived copies, then check
```

## Result

`python tools/verify_v4.py --sync` on Linux with Python 3.11.15, in the prepared copy of this bundle: **16 checks passed, 0 problems.** The helper unit tests (45) also passed on Python 3.10, 3.12, and 3.13.

**Re-check after coach 1.2.0 (2026-09-16):** after the learning-practice changes (`COACH_IMPROVEMENTS_2026-09-15.md`, decision D004), the same command again reported **16 checks passed, 0 problems** on Linux with Python 3.11.15, with the helper's 45 unit tests passing. That run used a copy where the `github-updates` move had been done by hand, as described in "Setup status" in `README.md`. Two deliberate breakages were also caught: a missing `.github/instructions/learning.instructions.md`, and a skill protocol copy that differed from the project's.

The checks cover:

- the project's `.github` source files being in place;
- backlog Markdown/JSON agreement;
- the dependency graph and release levels;
- requirement coverage and traceability;
- the starter progress record;
- JSON/JSONL parsing;
- the evaluation seed schema and locked-set counts;
- relative links;
- skill format and referenced resources;
- drift between the standalone skill, the installed skill, and the template snapshot;
- the progress-protocol copy;
- the absence of a loose root skill file;
- the helper unit tests;
- the installed helper running against the project.

A deliberate-breakage run confirmed the checker catches problems. After changing a dependency, a seed category, a traceability row, and a skill reference, and adding a broken link, the checker reported each one plus the resulting copy drift.

Project-level details, including the scratch execution of the T001 plan, are in `project-planning/commerce-support-copilot/DELIVERY_VALIDATION.md`.

## Not covered

- The `supportops-ai-project-lab-starter/` folder was not re-validated. Only its `README.md` and `AGENTS.md` changed, to mark it reference-only.
- No application code exists or was tested.
- Coaching behavior in a real host was not measured.
- Windows and macOS were not executed.

## Manual steps

Done in the GitHub repository on 2026-09-16: the `github-updates` files were moved into `.github/`, `python tools/verify_v4.py --sync` was run (**16 checks passed, 0 problems**, Linux, Python 3.11.15), and the obsolete root `SKILL.md` was deleted. See "Setup status" in `README.md`.
