# Development examples

`evaluation_seed.jsonl` contains twelve deliberately specified scenario seeds (schema version 2). They are not executable application fixtures or a finished gold evaluation set. Resolve their named synthetic fixtures, gold evidence sections, and rubric at T003/T007. Never count these public development examples as an untouched holdout.

## Seed schema (version 2)

| Field | Meaning |
|---|---|
| `id`, `schema_version`, `split` | Stable ID, schema version, and `development_seed` |
| `primary_category` | Exactly one of `eligible_replacement`, `missing_information`, `manual_escalation`, `authorization_or_injection`, `failure_recovery` (the enum in `docs/06_EVALUATION_AND_TESTING.md` §2) |
| `tags` | Secondary labels such as `boundary_7_days` or `prompt_injection`; they may overlap |
| `message` | Initial customer text entered by the proposer |
| `actors` | `proposer` and, for approval scenarios, a separate `approver`, each with `tenant_key`, `user_key`, and `roles`. Roles live only here, never in the operational fixture |
| `clock` | Fixed instant for the whole scenario |
| `operational_fixture` | A named `base` fixture plus overrides (days since delivery, stock, shipment state, existing replacement, downstream adapter behavior) |
| `policy_fixture` | Named policy/rules fixture active at the start |
| `preconditions` | Records that must exist before step 1 (for example an existing proposal) |
| `steps` | Ordered API-level actions with the acting role and optional per-step expectations. Execution and approval are API calls, never chat messages |
| `allowed_final_case_states` | Case states (from `docs/02_ARCHITECTURE.md` §4) that count as correct at the end |
| `expected_error_codes` | Error codes that must appear during the steps |
| `prohibited_effects` | Effects that fail the scenario whatever the final state |

## Fixture notes

- Fixture names, tenant keys, and user keys are human-readable test references, not API UUID values.
- Order external references are unique only within a tenant. DEV003 uses reference `7731`, which exists only in `store-a`. A separate T003 fixture places reference `1042` in both tenants to test that lookups never cross tenants.
- DEV009's conflict comes from two different active policy keys that both claim small-appliance damage. Two active versions of the same key cannot exist.
- The fixed clock uses Africa/Cairo's offset for that date. Implementation must use the IANA timezone for calendar logic, not assume a fixed offset year-round.
