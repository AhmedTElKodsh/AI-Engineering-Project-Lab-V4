---
applyTo: "tests/**,evals/**"
---

# Test and evaluation rules

- Write the focused test first and confirm it fails for the intended reason before implementing. An import or environment error is a setup defect, not a valid red state.
- Freeze the clock and use the synthetic fixtures from `tests/fixtures/`. Calendar-day logic uses the store's IANA timezone (Africa/Cairo), never a fixed offset.
- Routine tests make no network or paid model calls. Live-provider tests are opt-in, separately marked, and need an approved budget.
- Transaction, constraint, and tenant-isolation tests use a real disposable PostgreSQL instance, not mocks.
- Security tests exercise the backend. A hidden or disabled UI control is not a permission test.
- Never copy locked acceptance cases (`evals/acceptance_locked.jsonl`) into prompts, few-shot examples, training data, or reranker labels.
- Scorers must report numerators and denominators and must not turn zero claims or zero successes into 100%.
- Save the actual command output, including the failing run, under `learning/evidence/`, and label it `observed` or `learner_reported`.
