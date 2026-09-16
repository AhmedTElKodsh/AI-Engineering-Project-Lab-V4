# Learner decisions

## D001 - Initial project baseline

Date: 2026-09-15. Decision: use Commerce Support Copilot with a damaged-item replacement workflow and a fake-first learning route. Basis: the learner's choice of a single broad, practical AI-engineering project in the planning session that produced this kit. Status: planning baseline, no application results yet.

## D002 - Coaching defaults

Date: 2026-09-15. Decision: guide mode, one reviewable task, evidence-backed progress, separate learning mastery. These are starting defaults and can be changed explicitly by the learner.

## D003 - Planning baseline 1.1.0

Date: 2026-09-15. Decision: apply the planning review. Delivery time comes only from shipments; the model never emits internal IDs; cases are bound to one order; explicit case/proposal transition tables; any non-proposer manager may execute; proposal expiry counts from creation; release levels are declared per task (T012 and T019 are portfolio work); log redaction moves to T002; NFR08 adds rate limits; Python target moves to 3.13; seed schema v2. Affected requirements and rules: FR01, FR02, FR08, FR13, NFR07, NFR08 (new), BR03, BR05, BR06, BR07. Tasks with changed content: T001, T002, T003, T004, T006, T008, T009, T010, T012, T013, T014, T017, T018, T020, T021, T022, T023, T025, T026, T028, T029. Tasks whose dependency lists were reduced to direct prerequisites, changed, or reordered: T008, T010, T011, T012, T013, T014, T017, T018, T020, T021, T022, T023, T025, T026, T027, T028. Every task gained a `required_for` release level. No progress existed, so no evidence was invalidated.

## D004 - Learning practices in the coach

Date: 2026-09-15. Decision: add prediction before runs, the learner's hypothesis before diagnosis, an optional Retrieve warm-up mode, short bug autopsies, learning records in `learning/records/`, a Mission section in the learner profile, path-specific rules for `learning/**`, and two self-review fields in the pull request template. Coaching skill version 1.2.0; planning baseline stays 1.1.0 (no requirement, task, contract, or progress-schema change). Basis: review of two outside learning toolkits (`2026-09-15-coach-improvements.md` in the V4 bundle). Alternatives rejected: withholding help until the learner answers (conflicts with D002), and HTML lessons (the repository is the lesson). Also clarified: a correct restatement right after a correction is recorded as repair (`needs_practice`), not as `demonstrated`. No progress existed, so no evidence was invalidated.

Record future changes with reason, alternatives, affected requirements/tasks, and evaluation consequences. Do not overwrite past decisions to hide changes.
