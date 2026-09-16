# Quality gates

## Definition of done (every task)

- Every acceptance behavior in the task entry is implemented.
- The focused test (and any additional tests) failed for the intended reason first and passes now, with both runs saved.
- The relevant regression suite still passes.
- A review is recorded with a `pass` verdict.
- Documentation and configuration are updated where behavior changed; `09_BACKLOG.md` and `backlog.json` still match.
- No secrets, raw personal data, or hidden reasoning in the diff, logs, or evidence.
- No unreviewed scope expansion.

Mastery is a separate field and is not part of done.

## Gates by milestone

| Milestone | Gate before moving on |
|---|---|
| M0 | Package installs from the lock; health tests pass offline; config validation fails loudly; log redaction test passes; CI fails on a broken test |
| M1 | Fake and hosted adapters share one contract; invalid output becomes a typed failure after at most one repair; baseline evaluation report names its mode and dataset |
| M2 | Cross-tenant and old-version chunks never reach model context; citations resolve to retrieved authorized chunks; abstention works |
| M3 | Read tools inject the principal; rules are pure and boundary-tested; the graph respects run limits; resume is authorized and replay-safe |
| M4 | Before the first sandbox write: approval binding, self-approval, expiry, stale-version, wrong-order-line, duplicate, and concurrency tests pass |
| M5 | Locked set frozen with hashes; every metric shows numerator and denominator; fake and live results are labeled |
| M6 | OIDC tests pass on a local JWKS; development identity rejected outside local; restore and rollback evidenced; rate limits and spend caps enforced |
| M7 | Every target reported as met, missed, or not measured; a clean checkout reproduces the deterministic suite |

## Release levels

The backlog field `required_for` is authoritative.

| Level | Tasks |
|---|---|
| Read-only demo | T001-T011 |
| Sandbox workflow MVP | adds T013-T018 and T020 |
| Complete portfolio | all thirty tasks (adds T012, T019, T021-T030) |

Never describe a level as reached while one of its tasks is not `done`.

## Claims

Only claim what evidence supports: "passed these N tests", "recall changed from X to Y on dataset version Z", "p95 was X under this workload". Never claim production readiness, real-world accuracy, or business savings from synthetic results.
