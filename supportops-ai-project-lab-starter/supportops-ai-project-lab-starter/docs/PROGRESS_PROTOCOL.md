# Progress protocol

Progress is evidence, not optimism. Preserve the learner's existing work and record support separately from outcomes.

## Canonical files

- `progress/evidence.jsonl`: append-only learner/maintainer observations.
- `progress/current.json`: derived resume state.
- `progress/skills.json`: capability status and evidence references.

Do not create a competing `learning/progress.json` or reset state from a starter template over newer evidence.

## Evidence kinds

`execution`, `explanation`, `modification`, `debug`, `transfer`, `engagement`, `operational`, and `location`. Assistance levels: `none`, `docs`, `hint`, `scaffold`, `worked_example`, `ai_implemented`.

Every learner evidence event records: unique id, timestamp, milestone, capability IDs, expected behavior, observed behavior, outcome, assistance, source pointer, and any redactions. Learner-pasted output may be recorded as learner-reported evidence; do not convert it into a tool-observed result.

## Advancement versus retention

A milestone may be `ready` when its non-transfer gates pass and only delayed transfer remains, provided the readiness decision references current proof and records the future review trigger. `complete` still requires transfer where defined.

Delayed transfer uses a conservative floor of 24 elapsed hours with timestamps, or two calendar days when either observation is date-only. This is a scheduling safeguard, not scientific proof of retention.

## Independence

Assistant-generated code/tests cannot by themselves establish explanation, modification, debugging, or transfer independence. At final J5, explanation/modification/debug/transfer evidence used for ownership must have assistance `none` or `docs`; execution may have been supported.

## Corrections and regressions

Later contradictory evidence reopens only the affected claim/capabilities. Preserve downstream artifacts, but do not continue using invalidated prerequisite evidence as proof. A correction event references the superseded event and reason; never rewrite history silently.
