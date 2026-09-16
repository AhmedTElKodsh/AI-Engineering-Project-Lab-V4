# Learning records

Short, numbered notes about what the learner has shown, stated, or had corrected. The coach reads the newest ones at the start of a session to set the step size and choose retrieval questions. The format is adapted from the `teach` skill in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT License).

No learning record has been written yet.

## When to write one

Write a record only when one of these happens:

1. **Understanding shown:** the learner used or explained a non-trivial concept correctly, with evidence (a teach-back, a variation, a debugging step). Seeing a concept is not the same as learning it.
2. **Prior knowledge stated:** the learner says they already know something. Record the depth they claimed.
3. **Misconception corrected:** the learner believed something wrong and now sees why. These are the most valuable records, because they predict the next stumble.
4. **Mission changed:** the learner's goal or target release level changed. Update the Mission section of `learning/LEARNER_PROFILE.md` as well.

Do not write a record for a typo or one-off slip, for material that was only covered, or as a session summary. Session summaries go in `learning/SESSION_LOG.md`.

## Format

File name: `NNNN-short-slug.md`, numbered one higher than the highest existing record (`0001-lockfile-pins-resolved-tree.md`).

```markdown
# The lockfile pins the whole resolved dependency tree

Date: 2026-09-20T18:30:00+03:00
Task: T001
Kind: understanding | prior_knowledge | misconception | mission
Status: active
Assistance: none | hints | worked_example
Evidence: learning/evidence/T001-teachback.md

One to three sentences: what is now known, and why it changes what to teach next.

Original model: (misconceptions only, in the learner's words)
Corrected model: (misconceptions only)
```

`Evidence`, `Assistance`, and the two model lines are optional; include them when they apply.

## Rules

- Records are append-only. When understanding changes, write a new record and set the old one to `Status: superseded by NNNN`. Never delete a record.
- Keep the learner's original wording separate from the corrected understanding.
- A record may be the `path` of a `mastery_evidence` entry in `learning/progress.json` (see `learning/PROGRESS_PROTOCOL.md`). A record never changes a task's status by itself.
- No credentials, raw personal data, or hidden model reasoning.
