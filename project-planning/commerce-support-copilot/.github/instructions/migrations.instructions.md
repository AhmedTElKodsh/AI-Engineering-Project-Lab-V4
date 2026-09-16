---
applyTo: "migrations/**,src/commerce_support/db/**"
---

# Database and migration rules

- Every tenant-owned table has `tenant_id`, and foreign keys (or equivalent constraints) never link rows from two tenants.
- Implement the unique indexes listed in `docs/03_DATA_MODEL.md` §2 in the migration that creates the table, including one execution per proposal, one decision per proposal, one active policy version per key, and the partial unique index on active/succeeded replacements.
- Add CHECK constraints for nonnegative stock, positive quantities, and valid enum values. Enum values must match `docs/02_ARCHITECTURE.md` §4 and `docs/03_DATA_MODEL.md`.
- `audit_events` is append-only: revoke `UPDATE` and `DELETE` from the application role in the migration and test it.
- The pgvector column type fixes the embedding dimension. A new dimension needs a new column or table plus full re-embedding.
- Do not claim row-level security exists unless a migration creates it and a test proves it.
- Never write destructive down-migrations for valuable data without a reviewed recovery plan. Back up before migrating a demo database.
