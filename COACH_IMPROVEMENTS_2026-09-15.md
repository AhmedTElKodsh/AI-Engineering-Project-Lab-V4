# Coach improvements from two outside toolkits

**Date:** 2026-09-15 · **Scope:** what `commerce-ai-coach` and the project's Copilot setup could take from two outside sources.

**Sources reviewed (read in full):**

- **Manware's AI Learning Toolkit**: `i-am-manware/Manware-s-AI-Learning-Toolkit`. The `copilot` branch is the default (commit `3eb77d0`). I also checked the `claude-code` branch (`713f2a2`).
- **`teach` skill**: `mattpocock/skills`, `skills/productivity/teach/` (commit `959a8e9`, MIT). I also read its sibling `writing-for-agents` skill, because it sets the authoring rules for skills.

**Compared against:** `commerce-ai-coach/` (SKILL.md, 5 references, `agents/openai.yaml`, behavioral cases), plus the project's `AGENTS.md`, `.github/`, `github-updates/`, `learning/*`, and `docs/13_COACH_SETUP.md`.

**Host facts checked against current docs:**

- VS Code agent skills support `argument-hint`, `user-invocable` and `disable-model-invocation`, and a skill can be run as a `/` slash command.
- VS Code prompt files live in `.github/prompts/*.prompt.md`. Their frontmatter supports `description`, `name`, `argument-hint`, `agent`, `model` and `tools`, and they can use relative Markdown links.
- The Agent Skills spec allows only these frontmatter fields: `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`.
- Windows PowerShell 5.1 writes UTF-16LE when you use `>`, `>>` or `Out-File`. PowerShell 7 writes UTF-8 without a BOM.

## Implementation status (2026-09-15)

**Applied in coach 1.2.0** (planning baseline unchanged at 1.1.0; decision D004): items **#1–#8** and behavioral cases **B15–B20**.

| # | Where it landed |
|---|---|
| 1 Predict first | `SKILL.md` Guide row; `coaching-playbook.md` task brief step 5; `CURRICULUM.md`; `AGENTS.md`; Copilot instructions |
| 2 Hypothesis first | `review-and-debug.md` Debug steps 3 and 5; `SKILL.md` Debug row |
| 3 Learning records | new `learning/records/README.md`; `PROGRESS_PROTOCOL.md` (+ skill copy) mastery paths and writing rule 7; `project-map.md`; `SKILL.md` steps 1 and 7 |
| 4 Retrieve mode | `SKILL.md` mode table and step 4; `coaching-playbook.md` Retrieve section; `CURRICULUM.md` |
| 5 Autopsy | `review-and-debug.md` Autopsy section |
| 6 Mission | `LEARNER_PROFILE.md` Mission section; `coaching-playbook.md` mission round; `CURRICULUM.md` diagnostic |
| 7 `learning/**` rules | new project `.github/instructions/learning.instructions.md`; `GITHUB_SOURCES` in `tools/verify_v4.py` |
| 8 PR template | project `.github/pull_request_template.md` (riskiest part, prediction vs. result, records added) |

**Refinement added while applying:** "a correct restatement right after a correction shows repair, not mastery; record `needs_practice` and confirm with a fresh variation" (`PROGRESS_PROTOCOL.md`, `CURRICULUM.md`, playbook, B20). This keeps B20 consistent with the existing protocol, which would otherwise allow `demonstrated` with `assistance: hints`.

**Not applied yet:** P2 items #9–#14 and P3 items #15–#17.

---

## Bottom line

Our coach is already stronger than both sources on **project state**: per-task evidence, mastery kept separate from completion, a validator, safety rules and behavioral cases. Neither source has anything like that.

Where it is weaker is **learning science**. Today the coach checks understanding once, at a teach-back, and never comes back to it:

- It has no retrieval or spaced practice.
- It has no place to record misconceptions or prior knowledge.
- It never asks the learner to predict before running something.
- It never asks the learner for a hypothesis before debugging.
- It has no stated "why" (mission) for the learner.

The two sources fill exactly these gaps:

- **Manware** contributes interaction habits: predict first, the learner's hypothesis first, bug autopsy, retrieval warm-ups, and Copilot prompt files.
- **`teach`** contributes the memory model: mission, learning records, glossary, the split between fluency and storage strength, and cited sources.

**One thing not to import:** Manware's hard rule that help is withheld until the learner commits an answer. Our coach answers direct questions and gives worked examples on request, and that is a deliberate choice:

- `coaching-playbook.md` L40
- `learning/CURRICULUM.md` L26
- `SKILL.md` L49
- decision D002
- behavioral case B03

So everything below is added as an **offer** the learner can take or skip. None of it is a gate.

---

## Recommended changes

Priority: **P1** = high value and small, text-only edits. **P2** = worthwhile, needs new files. **P3** = changes the helper or schema, so do it later with tests.

| # | Change | From | Pri | Files |
|---|---|---|---|---|
| 1 | Predict the result (usually the red run) before running a test | Manware `/hint`, `/test` | P1 | `coaching-playbook.md`, `SKILL.md` |
| 2 | Learner's hypothesis first in Debug, plus a prediction for each experiment | Manware `/debug` | P1 | `review-and-debug.md` |
| 3 | Learning records: misconceptions, stated prior knowledge, insights | `teach` learning records; Manware `mistakes.md`/`concepts.md` | P1 | new `learning/records/README.md`, `PROGRESS_PROTOCOL.md` (+ skill copy), `SKILL.md`, `project-map.md` |
| 4 | **Retrieve** mode: an optional warm-up drawn from finished tasks | `teach` (retrieval, spacing, interleaving); Manware `/retrieve` | P1 | `SKILL.md`, `coaching-playbook.md`, `CURRICULUM.md` |
| 5 | Bug autopsy after a non-trivial fix | Manware `/autopsy` | P1 | `review-and-debug.md` |
| 6 | Mission section in the learner profile | `teach` MISSION.md | P1 | `LEARNER_PROFILE.md`, `SKILL.md` step 1 |
| 7 | Path-specific rules for `learning/**` | Manware `learning-files.instructions.md` | P1 | new `.github/instructions/learning.instructions.md`, `verify_v4.py` |
| 8 | PR template: riskiest part; predicted vs. observed | Manware `/code-review` | P1 | `.github/pull_request_template.md` |
| 9 | Project glossary with "avoid" aliases | `teach` GLOSSARY-FORMAT | P2 | new `docs/GLOSSARY.md`, `project-map.md`, optional lint in `verify_v4.py` |
| 10 | A few thin Copilot prompt files that route to coach modes | Manware `.github/prompts/` | P2 | new `.github/prompts/*.prompt.md`, `verify_v4.py`, `13_COACH_SETUP.md` |
| 11 | Checklist for introducing a new library | Manware `/api` | P2 | `coaching-playbook.md` |
| 12 | Better Assess items: one added constraint at a time, a code-reading item, and multiple-choice options of equal length | Manware `/explore`, `/read`; `teach` quizzes | P2 | `coaching-playbook.md` |
| 13 | One primary source per task brief | `teach` "each lesson recommends a primary source" | P2 | `coaching-playbook.md` |
| 14 | Markdown cheat sheets, written after a concept is learned | `teach` reference documents | P2 | new `learning/reference/README.md` |
| 15 | `retained` mastery level (storage strength) | `teach` fluency vs. storage strength | P3 | `coach.py`, tests, protocol (schema v3) |
| 16 | `coach.py retrieve` picks items that are due for review | `teach` spacing | P3 | `coach.py`, tests |
| 17 | UTF-8 check on evidence files, plus a PowerShell note | Found in Manware's `claude-code` branch | P3 | `coach.py validate`, `AGENTS.md` Commands |

### Why each one

1. **Predict the result.** Task brief step 5 currently *tells* the learner what the failing run should look like (`coaching-playbook.md` L11). If the learner predicts it first, they have to think about it, and TDD already requires that a test "fail for the intended reason". So the prediction lines up with a gate we already have. If the learner doesn't want to predict, show the expected result anyway.
2. **Learner's hypothesis first.** Debug step 4 says "one hypothesis at a time" (`review-and-debug.md` L32) but doesn't say whose. Asking for the learner's hypothesis first costs one question and turns every bug into practice. If the learner asks for the answer, give it. (B05 expects the coach to identify the fix.)
3. **Learning records.** Today, what the learner knows lives in scattered places: one line in `LEARNER_PROFILE.md` L13, the per-session prose in `SESSION_LOG.md`, and the teach-back files. `teach` treats learning records as ADRs for learning:
   - they are numbered;
   - each is one paragraph;
   - they are written only on four triggers: understanding shown, prior knowledge stated, misconception corrected, mission changed;
   - an old record is marked superseded, never deleted.

   Records are what let the coach choose a next step that is "just hard enough" and stop re-teaching things the learner already knows. `mastery_evidence[].path` can already point at them, so the helper doesn't need to change.
4. **Retrieve mode.** Every task in `backlog.json` already has `teach_back` and `concepts` fields, so the warm-up needs no new content.
   - Pull 2–3 items from different finished milestones (interleaving).
   - Prefer "predict", "find the bug" or "apply it here" over "define".
   - Offer the warm-up once per session. Declining costs nothing.
   - Name the mode **Retrieve**, because "Review" is already the code-review mode.
5. **Bug autopsy.** It fills the missing link between Debug and records. Run it only for non-trivial bugs; a typo gets no autopsy.
6. **Mission.** `LEARNER_PROFILE.md` records *what* the learner chose, but not *why*: a job target, a portfolio deadline, or a skill to demonstrate. The mission decides:
   - which release level to aim for (`read_only_demo`, `sandbox_mvp` or `portfolio`);
   - how much Interview mode to use;
   - what to leave out.

   Put it inside the existing profile rather than a new file, and ask for it once in a short round. That respects "no long questionnaire" (`CURRICULUM.md` L18).
7. **Rules for `learning/**`.** We have path rules for tests and migrations, but not for the learner's records, which is where Copilot is most likely to "tidy" history. Manware's rules are:
   - keep old entries;
   - keep the learner's own words separate from the corrected version;
   - date entries.
8. **PR template.** Asking "what's the riskiest part of this change?" is a self-review prompt that costs nothing and gives Review mode a place to start.
9. **Glossary.** The planning review already found terms drifting (completed/succeeded, pending/staging). A canonical glossary with an *Avoid* line per term stops that at the source, and `verify_v4.py` can check for the avoided words. It also enforces a distinction `AGENTS.md` L5 already asks for: the learner's **coach** is not the product **copilot**.
10. **Prompt files.** Skills can already be run as slash commands in VS Code. Manware's README says prompt files also work where skills aren't supported (its claim; not independently verified). Keep **five** prompt files, each 3–6 lines, each naming a mode and linking the skill reference, so no rule is written twice:
    - `/next`
    - `/check` (code review)
    - `/debug`
    - `/quiz`
    - `/warmup`
11. **New libraries.** This curriculum introduces uv, FastAPI, Pydantic, pgvector, LangChain and LangGraph. Before a learner uses one of them, give five quick answers: what problem it solves, what it assumes, when not to use it, its main failure mode, and a link to its official docs (S-ID).
12. **Assess items.**
    - When an answer is right, add exactly **one** new constraint (scale, concurrency, failure or security) rather than moving on.
    - When a task hands the learner existing code, use a code-reading item: "given this input, what does the function return?"
    - Keep multiple-choice options the same length so the formatting doesn't give the answer away.
13. **Primary source.** `teach` says never to trust parametric knowledge. Our task brief doesn't point to a source, but `docs/12_SOURCES_AND_VERSION_POLICY.md` already lists S1–S17.
14. **Cheat sheets.** `teach` notes that lessons are rarely revisited but reference documents are. Write short Markdown cheat sheets (uv commands, pytest fixtures, constraint patterns, LangGraph interrupt rules) *after* the learner has shown the skill. Markdown is diffable and renders in GitHub and VS Code.
15. **`retained` mastery.** A teach-back in the same session where the task was finished mostly shows short-term recall (what `teach` calls fluency). Proposed rule: `retained` requires a later-session Retrieve or variation, done without a worked example, recorded in a record. This needs:
    - a new value in `coach.py` `MASTERY` (L32);
    - a validator rule and tests;
    - a `schema_version: 3` migration;
    - updates to `PROGRESS_PROTOCOL.md`, `CURRICULUM.md` and `quality-gates.md`.

    Worth doing once #3 and #4 have been used for a few weeks.
16. **`coach.py retrieve`.** Date arithmetic across many records is easy for a chat model to get wrong. Instead, a small read-only subcommand could list finished tasks due for review on a fixed ladder (1, 3, 7 and 21 days after the last retrieval), read from the records. It stays standard-library only and read-only.
17. **UTF-8 check.**
    - Every file on Manware's `claude-code` branch is **UTF-16LE with CRLF** except its README (plain UTF-8) and the four `learning/*.md` files (ASCII). A tool that reads them as UTF-8 sees NUL-padded text.
    - Our learner is on Windows. In Windows PowerShell 5.1, `uv run pytest ... > learning/evidence/T001-tests.txt` produces exactly that encoding.
    - Fixes: have `coach.py validate` warn when an evidence file isn't UTF-8, and in `AGENTS.md` Commands say "use PowerShell 7, or `| Out-File -Encoding utf8 <path>`".

---

## Deliberately not adopted

| Idea | Source | Why not |
|---|---|---|
| Withhold all help until the learner commits; ask permission before each hint level; "never name the file or line first" | Manware | Conflicts with D002 and B03. For a project-first learner, the friction costs more than it teaches. We keep the *order* (predict or hypothesize first) and drop the *gate*. |
| HTML lessons + shared `assets/` component library, opened via CLI | `teach` | The repository *is* the lesson. HTML lessons would bloat the learner's repo, can't be reviewed in PRs, and Copilot has no "open this file" step. The reference-document idea is kept, in Markdown (#14). |
| Make the coach user-invoked only (`disable-model-invocation: true`) | `teach` | In its own repository the coach should activate automatically. `teach` is user-invoked because it runs in any folder. |
| Four separate small skills (`debugging`, `examination`, `code-review`, `retrieval`) | Manware | Generic descriptions would compete with the coach's triggers (Copilot also has its own code-review features). Folding them into coach modes keeps one entry point. |
| Adding `argument-hint` to the skill frontmatter | VS Code docs | Useful in VS Code, but it is not in the Agent Skills spec, so a strict validator (skills-ref) could flag it. Optional; the prompt files in #10 cover the same need. |
| A "communities" (wisdom) section | `teach` | Low value before M7. At most, one optional line in `11_PORTFOLIO_AND_DEMO.md`: share the demo somewhere for outside feedback. No specific communities were researched. |
| Copying Manware text word for word | Manware | The repository has **no license file**, so the default is all rights reserved. Take the ideas and write our own wording. `teach` is MIT, so adapted text should carry a short attribution line. |

---

## Setup (done 2026-09-16)

When this review was written, the project's `.github/` held only the old `copilot-instructions.md` and `pull_request_template.md`, and the updated files waited in `github-updates/`. That one-time setup is now done: the files live in the project's `.github/`, `github-updates/` is gone, the installed skill exists at `.github/skills/commerce-ai-coach/`, and the root `SKILL.md` was removed (see "Setup status" in the V4 `README.md`).

New Copilot files, such as the prompt files in #10, now go straight into the project's `.github/`. Add each one to `GITHUB_SOURCES` in `tools/verify_v4.py`.

---

## New behavioral cases (add to `tests/behavioral_cases.json`)

| ID | Mode | Setup / prompt | Expected | Prohibited |
|---|---|---|---|---|
| B15 | guide | T001 test written, not yet run. "Run it." | Asks for a one-line prediction of the failure; if skipped, states expected vs. observed separately | Refuses to proceed without a prediction |
| B16 | debug | Retrieval test fails. "Why does it return nothing?" | Asks for the learner's suspected layer, then one discriminating experiment with a prediction | Withholds the answer after "just tell me" |
| B17 | retrieve | T001–T004 done; new session. "Let's continue T005." | Offers one short warm-up from done tasks; on decline, goes straight to T005 | Forces the warm-up; asks definition-only questions |
| B18 | debug | Bug was a typo in a fixture name; fixed. | Skips the autopsy; notes nothing durable | Writes a learning record for a typo |
| B19 | guide | Profile mission empty; first session. "Start the project." | One short round (why, target release level, time budget), then T001 | A long questionnaire before any task |
| B20 | assess | Learner explains the lockfile incorrectly, then corrects it after a hint. | Writes a misconception record (original vs. corrected model, assistance `hints`) | Marks mastery `demonstrated` from that same exchange |

---

## Draft text (ready to paste)

The drafts are written in our own words. The two items adapted from MIT-licensed `teach` (#3 and #9) carry an attribution line.

### D1. `SKILL.md`: mode table (replace the Guide and Assess rows; add Retrieve)

```markdown
| Guide (default) | "next step", "start T0xx", "help me with" | Task goal, minimum concept, one primary source, one step. Before a run, ask for a one-line prediction; show expected vs. observed. Use the hint ladder. |
| Retrieve | "warm up", "retrieval", session start after a done task | Offer once. 2-3 items from different done milestones (predict, find the bug, apply); one at a time; answer revealed after the learner commits or passes. Log in the learning records only when something changed. |
| Assess | "quiz me", "check my understanding" | One teach-back or variation. On success, add exactly one constraint. Record mastery separately from task completion. |
```

Add to Session protocol step 1:

> If `learning/LEARNER_PROFILE.md` has no mission, ask one short round (why this project, target release level, weekly time) before the first task, then continue. Read the newest `learning/records/` entries to set the step size.

Add to step 7:

> Write a learning record only on the four triggers in `learning/records/README.md`.

### D2. `coaching-playbook.md`: additions

```markdown
## Task brief (guide mode)
...
5. **Predict, then run:** ask the learner what the run will show and why (for a new test: which assertion fails, with which message). Then give the command and what to paste back. If they pass, state the expected result yourself.
6. **Primary source:** one S-ID from `docs/12_SOURCES_AND_VERSION_POLICY.md`.

## New library checklist
When a task introduces a library, the minimum concept is five short answers: the problem it solves, what it assumes, when not to use it, its most likely failure mode here, and its official page. Ask the learner to restate one of them after reading.

## Retrieve mode
Sources: `teach_back` and `concepts` of `done` tasks in `learning/backlog.json`, and active `learning/records/`. Mix milestones. Item forms: predict an output, spot the bug in a short snippet, choose between two designs, apply a rule to a new case. Avoid definition-only items. Finish with one weak area and one practice action.

## Assess mode (append)
- After a correct answer, add one constraint (scale, concurrency, a failed dependency, a hostile input) and ask what breaks first.
- Code-reading item: pick a concrete input and ask what the function returns, step by step.
- Multiple-choice options have the same length and form; formatting never hints at the answer.
```

### D3. `review-and-debug.md`: Debug additions

```markdown
4. **Hypothesis first.** Ask which layer the learner suspects and why. Then pick the smallest experiment that separates their hypothesis from the strongest alternative, and ask them to predict its result before running it. If they ask for the answer, give it.
...
7. **Autopsy (non-trivial bugs only).** Ask the learner to fill in: what happened; what they believed; what was actually true; the signal that could have shown it earlier; the concept underneath; the prevention (a test, check, or habit). Classify as: slip, repeated pattern, concept gap, missing domain knowledge, or debugging process. Save a learning record for anything but a slip.
```

### D4. New `learning/records/README.md`

```markdown
# Learning records

Short, numbered notes that change what the coach teaches next. Adapted from the `teach` skill by Matt Pocock (MIT).

File name: `NNNN-short-slug.md`, numbered from the highest existing record. Body: a title and 1-3 sentences on what is now known and why it matters for later tasks. Optional lines: `Status: active | superseded by NNNN`, `Evidence:` (path or task), `Assistance: none | hints | worked_example`, `Original model:` / `Corrected model:` (for misconceptions, in the learner's words first).

Write one only when:
1. the learner showed they can use a non-trivial concept (not just saw it);
2. the learner stated prior knowledge, with its depth;
3. a misconception was corrected;
4. the mission changed (also update the profile).

Coverage is not learning, and a session summary is not a record: those go in `SESSION_LOG.md`. Never delete or rewrite a record; supersede it.
```

### D5. `LEARNER_PROFILE.md`: mission section (insert after "Known context")

```markdown
## Mission

Why: not recorded yet (ask once, briefly).
Target release level: not chosen (read_only_demo / sandbox_mvp / portfolio).
Success looks like: not recorded (observable outcomes, e.g. "explain the approval design in an interview").
Constraints: weekly time, budget for paid calls, deadline.
Out of scope for now: not recorded.

Keep this under one screen. Change it only when the learner confirms, and add a learning record when it changes.
```

### D6. New `.github/instructions/learning.instructions.md`

```markdown
---
applyTo: "learning/**"
---

# Learning record rules

- `learning/progress.json` changes only under `learning/PROGRESS_PROTOCOL.md`.
- Append to `SESSION_LOG.md` and `learning/records/`; never rewrite or delete past entries. Supersede instead.
- Keep the learner's original wording separate from the corrected understanding.
- Date every entry with a timezone offset.
- Evidence files are UTF-8 text with redacted content.
```

### D7. PR template (`.github/pull_request_template.md`): add under "Learning"

```markdown
Riskiest part of this change, and why:
What I predicted before running the tests, and what happened:
```

### D8. Prompt file example (`.github/prompts/warmup.prompt.md`)

```markdown
---
name: warmup
description: Short retrieval warm-up from finished Commerce Support Copilot tasks.
agent: agent
---

Use the commerce-ai-coach skill in Retrieve mode, following [the playbook](../skills/commerce-ai-coach/references/coaching-playbook.md). Read `learning/progress.json` and `learning/records/` first.
```

The other four prompts (`next`, `check`, `debug`, `quiz`) use the same shape and name their mode. The link resolves because the prompt sits in `.github/prompts/`, next to the installed skill in `.github/skills/`. The standalone template copy resolves the same way, since `--sync` copies `.github/prompts/` along with the rest of the project.

### D9. `docs/GLOSSARY.md` seed

```markdown
# Glossary

Canonical terms for this project; docs, code names, and coaching use these. Format adapted from the `teach` skill by Matt Pocock (MIT).

**Coach**: the assistant skill that guides the learner. _Avoid_: copilot (for the coach)
**Copilot**: the support product being built. _Avoid_: coach (for the product)
**Principal**: the server-supplied `Principal(user_id, tenant_id, roles)` behind a request, never taken from the body. _Avoid_: user, caller
**Tenant**: one store's isolated data scope. _Avoid_: account, org
**Proposal**: an immutable suggested action awaiting a manager decision. _Avoid_: request, ticket action
**Approval envelope**: the canonical JSON whose SHA-256 hash an approval binds to. _Avoid_: signature, signed payload
**Succeeded**: the success status of a proposal, action result, replacement request, or ingestion job. _Avoid_: completed, done (for workflow state)
**Staging**: a policy version not yet active. _Avoid_: pending (reserved for proposals)
**Reconciliation**: resolving an unknown write outcome by lookup, never by blind retry. _Avoid_: retry
**Checkpoint**: saved graph state for resume; grants no authority. _Avoid_: approval, save point
**Done**: a task status backed by test and review evidence. **Mastery** is recorded separately.
```

---

## Suggested order

1. **Done (2026-09-16):** the one-time `.github` setup (see "Setup status" in the V4 `README.md`).
2. **Done (coach 1.2.0):** P1 text edits (#1–#8) in the standalone skill and project, plus B15–B20, checked with `python tools/verify_v4.py --sync`.
3. P2 (#9–#14). Add the prompt files to `GITHUB_SOURCES`, and list the new files in `docs/13_COACH_SETUP.md` and `project-map.md`.
4. After a few real sessions, decide on P3 (#15–#17). Each needs helper tests and a protocol change.
