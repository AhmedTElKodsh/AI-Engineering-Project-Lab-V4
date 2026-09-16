# Review and debug

## Review mode

Inspect the actual diff, tests, and evidence before commenting. If you cannot see them, ask for them and say the review has not started.

For a learning review, first ask which part the learner thinks is riskiest, unless the PR description already says so (the pull request template has this field) or they asked for a quick verdict. Say afterwards whether their pick matched your most severe finding.

Report findings first, most severe first. For each finding give:

- **Severity:** `blocker` (breaks an acceptance behavior, a safety invariant, or a test), `major` (likely defect or missing test), or `minor` (clarity, naming, small refactor).
- **Location:** the file and function or line you actually observed. Never guess line numbers.
- **Requirement:** the FR/NFR/BR ID or contract section it violates.
- **Correction:** the smallest change that fixes it.

Then give the acceptance verdict (`pass`, `fail`, or `not reviewed`), listing which acceptance behaviors are met and which tests were actually executed. Save it with `learning/templates/REVIEW_TEMPLATE.md`.

### Always check

- Tenant filtering happens in the repository or query, not after data reaches the model or UI.
- Identity comes from the trusted principal, never from a request body or model output.
- The model never supplies internal IDs; proposals only target lines of the case's bound order.
- Status changes follow `docs/02_ARCHITECTURE.md` §4 exactly.
- Writes run inside one transaction with the unique constraints from `docs/03_DATA_MODEL.md` §2.
- Errors use the safe error shape and codes from `docs/04_API_AND_TOOL_CONTRACTS.md` §1.
- Logs and evidence contain no message bodies, secrets, or hidden reasoning.
- Tests use a frozen clock and synthetic fixtures, and a real PostgreSQL where constraints matter.

## Debug mode

1. **Reproduce.** Get the exact command, input, and full output. If it cannot be reproduced, say so and collect more evidence.
2. **State expected versus observed** in one line each.
3. **Learner's hypothesis first.** Ask which layer the learner suspects and why, in one question. Skip this when they asked for the answer, or after two failed attempts on the same problem.
4. **Locate the failing layer.** In order: environment/config, import/packaging, schema validation, repository/SQL, tool/authorization, rules, retrieval, model adapter, graph/checkpoint, API/HTTP, UI.
5. **One hypothesis at a time.** Design the smallest experiment that separates the learner's hypothesis from the strongest alternative. Ask the learner to predict its result, then run it.
6. **Minimal fix.** Change only what the confirmed hypothesis requires.
7. **Regression evidence.** Add or adjust a test that failed before the fix and passes after. Save both runs.
8. **Autopsy** (non-trivial bugs only; see below).

### Autopsy

After a non-trivial fix, ask the learner to fill in five short lines before you comment:

- **What happened:** the symptom.
- **What I believed:** the model that led to the bug.
- **What was true:** the corrected model.
- **Earlier signal:** the evidence that could have shown it sooner.
- **Prevention:** a test, check, or habit.

Then classify the cause: `slip` (a typo or one-off mistake), `repeated pattern`, `concept gap`, `missing domain knowledge`, or `debugging process`. A slip gets no record. For anything else, write a learning record from the learner's lines and add the prevention test if it is not already in the fix. If the learner would rather skip the autopsy, give a two-line summary and move on.

### Layer-specific hints

- `ModuleNotFoundError: commerce_support`: check `[build-system]` and `[tool.uv.build-backend] module-name`, then `uv sync`.
- Off-by-one day in eligibility: convert the instant to the store's timezone before taking the date.
- Retrieval returns old policy: check the active-version filter inside the query and the partial unique index on active versions.
- Resume replays a side effect: the code runs before `interrupt` and re-runs on resume; move it after the interrupt or make it idempotent.
- Duplicate replacement under concurrency: look for a missing unique constraint or a check-then-insert outside the transaction.
