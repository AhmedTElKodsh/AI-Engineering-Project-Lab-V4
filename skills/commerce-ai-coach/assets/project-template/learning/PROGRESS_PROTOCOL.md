# Progress protocol

This file is the single authority for how `learning/progress.json` is written. The `commerce-ai-coach` skill carries an identical copy in `references/progress-protocol.md`; if they ever differ, this repository copy wins.

## File shape (schema version 2)

```json
{
  "schema_version": 2,
  "project_version": "1.1.0",
  "current_task": "T001",
  "last_session": "2026-09-20T18:30:00+03:00",
  "tasks": {
    "T001": {
      "status": "in_progress",
      "mastery": "unassessed",
      "evidence": [],
      "mastery_evidence": [],
      "blocker": null,
      "updated_at": "2026-09-20T18:30:00+03:00"
    }
  }
}
```

- `tasks` has exactly one entry per task in `learning/backlog.json`. Add or remove entries only together with a recorded backlog change.
- `current_task` is `null` or a task ID. `last_session` and `updated_at` are `null` or ISO-8601 timestamps with an offset.
- Unknown extra keys are errors, so typos are caught.

## Task status

| Status | Meaning | Required fields |
|---|---|---|
| `not_started` | No work recorded | `blocker` is `null` |
| `in_progress` | The learner is working on it; evidence may be partial | Dependencies should be `done` (the helper warns otherwise) |
| `blocked` | Work cannot continue | `blocker` is a non-empty string naming the cause and what would unblock it |
| `done` | Acceptance behaviors met and reviewed | At least one `test` entry with `result: pass` and one `review` entry with `result: pass`, both pointing to existing files; every dependency is `done` |

Allowed changes: `not_started -> in_progress -> done`, `in_progress <-> blocked`, and `done -> in_progress` when a regression or changed requirement reopens the task. When reopening, keep the old evidence and add a `review` entry with `result: fail` explaining why. Never delete evidence to make a record look clean.

## Evidence entries

```json
{"kind": "test", "path": "learning/evidence/T001-tests.txt", "result": "pass", "source": "observed", "command": "uv run pytest tests/unit/test_health.py -q", "summary": "..."}
```

| Field | Values |
|---|---|
| `kind` | `test`, `review`, `experiment`, `demo` |
| `path` | Relative to the project root, using `/`; no `..`, no absolute paths, and it must stay inside the project after resolving symlinks |
| `result` | `pass`, `fail`, `not_run` |
| `source` | `observed` (the assistant ran or inspected it) or `learner_reported` (pasted or described by the learner) |
| `summary` | Non-empty, one or two sentences |
| `command` | Optional; the exact command that was run |

`learner_reported` evidence is valid, but the coach says so when relying on it. A validator can check structure and links, never the truth of a file's contents.

## Mastery

| Value | Meaning | Required fields |
|---|---|---|
| `unassessed` | No relevant demonstration recorded | none |
| `needs_practice` | A concrete misunderstanding is evidenced | at least one `mastery_evidence` entry |
| `demonstrated` | A teach-back or independent variation shows the learner can explain or apply the concept | at least one `mastery_evidence` entry |

A mastery entry is `{"path": "...", "summary": "...", "assistance": "none" | "hints" | "worked_example"}`, pointing to an existing teach-back, variation, or learning record (`learning/records/`). `demonstrated` requires at least one entry with `assistance` of `none` or `hints`. Mastery is independent of status: a task can be `done` and `unassessed`.

A correct restatement given right after the coach corrected a misconception shows repair, not mastery. Record `needs_practice` with the misconception record as evidence, and move to `demonstrated` only after a fresh teach-back or variation, preferably in a later session.

## Writing rules

1. Inspect the evidence file before recording it.
2. Change only the active task's record, plus `current_task`, `last_session`, and that task's `updated_at`.
3. Never reset progress from a template or starter snapshot.
4. Append one session handoff to `learning/SESSION_LOG.md` with one exact next action.
5. If writes are not possible, return the exact JSON fragment and handoff for the learner to save.
6. Run `python .github/skills/commerce-ai-coach/scripts/coach.py validate` when execution is available.
7. Write a learning record in `learning/records/` only for the triggers in its `README.md`. Records are append-only: supersede an old record instead of editing or deleting it. Records, predictions, and retrieval warm-ups never change a task's status by themselves.
