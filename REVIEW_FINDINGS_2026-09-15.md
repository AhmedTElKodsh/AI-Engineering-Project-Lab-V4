# Review: Commerce Support Copilot planning pack + `commerce-ai-coach` skill

**Reviewed:** 2026-09-15 · **Scope:** `project-planning/commerce-support-copilot/**` (all 33 files), root `SKILL.md`, root `DELIVERY_VALIDATION.md`. I also read parts of `supportops-ai-project-lab-starter/` because it overlaps with this pack (finding C1).
**Method:** Pass 1 was a manual read of every file. Pass 2 used scripts to check the backlog Markdown against the JSON, dependency cycles, requirement coverage, traceability, links, JSON/JSONL parsing, and the seed schema. I checked key technical claims against primary docs (uv, Python release status, Agent Skills spec, GitHub Copilot skills, LangGraph interrupts).

Severity: **Critical** = broken or unusable as delivered · **High** = a design contradiction that will cause wrong code or wrong tests · **Medium** = a gap or ambiguity a learner will hit · **Low** = polish.

---

## What is already solid (keep it)

- `09_BACKLOG.md` and `learning/backlog.json` agree for all 30 tasks: title, milestone, dependencies, requirements, files, test path, acceptance criteria, teach-back and concepts.
- The dependency graph has no cycles and no forward references. All 21 FR/NFR IDs map to at least one task. `TRACEABILITY.md` matches the backlog exactly, and each listed test belongs to a task in that row.
- No test path is duplicated. `progress.json` has exactly the 30 backlog IDs. All JSON/JSONL parses. No relative Markdown link is broken.
- The locked-set numbers add up: 40+20+20+20+20 = 120.
- The seed clock `+03:00` is correct for Cairo in September, and `examples/README.md` correctly says to use the IANA zone rather than a fixed offset.
- The LangGraph guidance in `02_ARCHITECTURE.md` §4 matches current docs: an interrupt needs a checkpointer and a thread ID, and the node re-runs from its start on resume. The five source URLs I spot-checked (S1, S5, S9, S10, S13) all resolve.
- The trust-boundary design is strong: server-owned principal, hash-bound immutable approval, execution-time revalidation, DB-enforced dedupe, and reconciliation instead of blind retry. The "evidence vs. mastery" separation is well thought out.

---

## Critical

### C1. Two competing curricula and two skills in the same V4 folder
- `project-planning/commerce-support-copilot` uses **M0–M7 / T001–T030** with the `commerce-ai-coach` skill (root `SKILL.md`).
- `supportops-ai-project-lab-starter` is the *same product* with a **J0–J5** route and the `ai-engineering-tutor` skill. It explicitly forbids the other system: its `AGENTS.md` L15 says "Do not create a second M0-M7/T001-T030 learning state", and its `SKILL.md` L8 says "do not initialize a competing M0-M7/T-task curriculum".
- If a learner opens `V4/` in Copilot or Claude, the agent sees contradictory authorities: two progress schemas (`learning/progress.json` vs `progress/current.json`) and two product names (Commerce Support Copilot vs SupportOps AI).
- **Fix:** decide which one V4 ships. Then either (a) move the other into `archive/`, or (b) keep both and add a root `README.md` explaining which is canonical and when to use the other. Don't leave both as peers.

### C2. The `commerce-ai-coach` skill can't be used as delivered
- Root `SKILL.md` links or runs 8 resources, and `DELIVERY_VALIDATION.md` cites a 9th. None of them exist in V4: `references/project-map.md`, `coaching-playbook.md`, `review-and-debug.md`, `quality-gates.md`, `progress-protocol.md`, `assets/project-template/README.md`, `scripts/coach.py`, `tests/behavioral_cases.json` (SKILL.md L12–18, L41), plus `tests/HELPER_TEST_RESULTS.txt` (DELIVERY_VALIDATION L24).
- The file is loose in `V4/`. The Agent Skills spec requires `name` to **match the parent directory** (`commerce-ai-coach/SKILL.md`). GitHub Copilot only discovers project skills under `.github/skills/`, `.claude/skills/` or `.agents/skills/`. As placed, no host will load it.
- `13_COACH_SETUP.md` L5/L22 and `DELIVERY_VALIDATION.md` L14–16, L24 describe `skill.zip` / `project-planning.zip` and "22 automated tests passed". Neither the zips nor the helper are in this folder, so the validation report can't be reproduced here.
- **Fix:** restore the full skill folder (`commerce-ai-coach/{SKILL.md,references/,assets/,scripts/,tests/}`) from the original `skill.zip`. Then either install it at `project-planning/commerce-support-copilot/.github/skills/commerce-ai-coach/` or keep it as a sibling folder. Delete the root copy of `DELIVERY_VALIDATION.md`, which is byte-identical to the one in `project-planning/`.
- **Also consider (refinement):** until the references exist, the skill should degrade gracefully. Add one line such as "If a linked reference is missing, use `learning/CURRICULUM.md` (hint ladder, modes, mastery) and `learning/evidence/README.md` (evidence schema)." Those two files already hold most of the missing content.

### C3. The T001 plan can't meet T001's own acceptance criterion
- The `pyproject.toml` in `docs/plans/01_FOUNDATION.md` (L31–41) has no `[build-system]`. uv docs: *"If a build system is not defined, uv will not attempt to build or install the project itself, just its dependencies."* Tests pass only because of `pythonpath = ["src"]`, but `uv run python -c "import commerce_support"` fails. That breaks T001 acceptance #1 ("imports the src package", `09_BACKLOG.md` L24).
- **Fix:** add the following, or start with `uv init --package`, and add the import check to the test:
  ```toml
  [build-system]
  requires = ["uv_build"]   # `uv init --package` writes the current pinned range
  build-backend = "uv_build"
  ```
  Then drop the `pythonpath` workaround.
- Related: the plan never shows how to *run* the service. Add `uv add uvicorn` and a `uv run uvicorn commerce_support.main:create_app --factory --reload` step, then a manual `curl` against `/health/live`. The `--factory` flag is needed because the plan uses `create_app()` rather than a module-level `app`. Seeing the app respond is the motivating moment for a junior learner.

---

## High — design contradictions

### H1. Two sources of truth for delivery time
- `orders.delivered_at` (`03_DATA_MODEL.md` L20) and `shipments.delivered_at` (L23) both exist. BR03 (`01_PRD.md` L59) depends on "delivered local calendar date" but doesn't say which one counts. Different fixtures can then disagree.
- **Fix:** make `shipments` authoritative and drop `orders.delivered_at`, or define precedence and add a fixture where the two disagree.

### H2. `OperationalFacts` can't represent the multi-line case that BR02 must detect
- The contract is a single flat record with one `order_line_id`/`sku`/`quantity` (`04_API_AND_TOOL_CONTRACTS.md` L63). BR02 (`01_PRD.md` L58) requires detecting multiple lines.
- `lookup_order` also returns `available_quantity` and `existing_replacement_id`, which duplicates the separate `check_inventory` tool.
- **Fix:** `OrderFacts{order_id, order_version, delivered_at, lines: list[OrderLineFacts], observed_at}` plus `StockFacts{sku, available_quantity, observed_at}`. Let the rules layer combine them.

### H3. The model is asked to emit an internal UUID
- `TicketAnalysis.order_line_id: UUID | null` (`04` L61; FR02 L77). A customer message never contains an internal UUID, so the field is always null or hallucinated.
- **Fix:** replace it with `product_mention: str | null` (e.g. "blender") and resolve it to `order_line_id` in deterministic code after `lookup_order`. Keep `order_line_id` only in `ReplacementParameters`.

### H4. Cases are never bound to an order
- `cases` (`03` L24) has `customer_id` but no `order_id`/`order_line_id`. Nothing stops `propose_replacement(order_line_id=…)` (`04` L102) from targeting a *different* same-tenant order than the one the case is about. That is an in-tenant confused-deputy risk.
- **Fix:** persist `cases.order_id` once it is resolved. `propose_replacement` must verify `order_line.order_id == case.order_id`. Add a test for it in T017.

### H5. The proposal and case state machines are incomplete
- Proposal states (`02` L74–76) have no path for:
  - an **approved** proposal that expires or goes stale before execution (BR06/BR07 say "invalidate"; `03` L52 returns `STALE_PROPOSAL`);
  - a **revise** decision (`ProposalDecision.decision = revise`, `04` L67). The decision endpoint returns "approved/rejected/superseded" (L46), but `superseded` only happens once a *new* proposal exists.
- The case state list (`02` L68) omits `executing` and `reconciliation_required`, although L70 uses both.
- **Fix:** publish one explicit transition table per entity (state, event, next state, actor, guard) in `02` or `03`. Add `revision_requested` and `invalidated` (or reuse `expired`/`superseded` with a reason code). Have T004 or T017 test that table directly.

### H6. Who is allowed to execute?
- The execute endpoint says "Approved manager principal" (`04` L47). `07` L20 says the manager may "execute an approved proposal". It's unclear whether this means *the approving* manager, *any* same-tenant manager, or also the proposer.
- **Fix:** state one rule, e.g. "any active same-tenant manager other than the proposer; re-checked at execution". Add it to BR07 and to the T017/T018 tests.

### H7. The external-write task (T019) is inside the MVP in some documents and outside it in others
- `08_ROADMAP.md` L11 puts T019 in M4, and README L49 and `08` L24 say MVP = M0–M4. So T019 is required.
- But `08` L20 leaves T019 off the first-action path, `02` L86 calls the external adapter "portfolio hardening", and the PRD MVP row excludes "real commerce integrations" (`01` L38).
- T012 has the same problem: it is in M2 (read-only demo = M0–M2) but is described as "deepening before portfolio gates".
- **Fix:** add an explicit "Required for" column (Read-only / MVP / Portfolio) to the milestone table, or move T019 → M5 and T012 → M5.

### H8. Redaction arrives too late
- The brief says "establish … redacted logs early" (`00` L43). The redaction module is T022 (M5), yet model calls and case messages are logged from T005/T006 and persisted from T008 onward.
- **Fix:** move a minimal `observability/redaction.py` plus a "no raw message body in logs" test into T002 or T005. Keep T022 for trace export, cost accounting and the allowlist.

---

## Medium — gaps and ambiguities

| # | Location | Issue | Suggested fix |
|---|---|---|---|
| M1 | `learning/progress.json`, `evidence/README.md`, `01_FOUNDATION.md` L113 | The task `status` enum is never defined. Only `not_started` and `done` appear, although `blocker` and `current_task` exist. | Document `not_started \| in_progress \| blocked \| done` (and whether `done → in_progress` reopening is allowed) in the progress protocol and in `evidence/README.md`. |
| M2 | `03` L36, `04` L70, FR13, `07` L41 | Jobs are "quarantined", but the `ingestion_jobs` and `JobView` enums only have `queued/running/succeeded/failed`. | Add `quarantined`, or define it as `failed` + `error_code`. Also link jobs to `document_id`/`policy_version_id`. |
| M3 | `03` L32/L44 | `action_executions` is unique only on `(tenant_id, idempotency_key)`. A second key for the same proposal creates a second ledger row; the replacement constraint blocks the *effect*, but the audit trail is misleading. | Add `UNIQUE(tenant_id, proposal_id)` on executions. |
| M4 | `03` L31/L44 | "At most one effective approval decision per proposal" has no matching index. | Add a unique index on `approvals(tenant_id, proposal_id)` (partial if rejections can be re-decided). |
| M5 | `03` L28, T012 | Hybrid retrieval needs full-text search, but `chunks` has no `tsvector` column or GIN index. | Add a generated `tsv` column + GIN index at T012 (or T009). |
| M6 | `03` L28/L64 | `embedding_dimension` is stored per row, but a pgvector column's dimension is fixed by its type (`vector(n)`). | Store model, revision, dimension and preprocessing in an `index_versions` table. Chunks reference `index_version_id`. |
| M7 | `04` L48 | Upload returns `201` before M6 and `202` after, which is a breaking contract change mid-project. | Return `202 + JobView` from the start. The pre-M6 job can simply complete synchronously. |
| M8 | `04` L59–60, `03` L25 | `AddMessageRequest` has no length limit (Create has 1–8000) and no author type. `messages` has neither `role` values nor `author_id`. | Add the same length limit, `kind: customer_text \| employee_note`, `author_id`, and an enum for `messages.role`. |
| M9 | `04` L105 | Rejecting tool arguments that "contain SQL, shell commands, or URLs" is a content blocklist. It is brittle and will false-positive on `search_policies(query="select a replacement…")`. | Rely on strict schemas instead: `extra="forbid"`, a regex for `order_reference`, max lengths. Test that unknown fields are rejected. |
| M10 | `04` L32 vs L47/L53 | `RECONCILIATION_REQUIRED` is listed as an *error code*, but the execute endpoint returns it as a non-error `202` body. | Pick one: keep it as an `ActionResult.status` only and remove it from the error-code list, or document when each form is used. |
| M11 | `02` L26 | Rate limits are drawn in the architecture but have no FR/NFR, task or test. | Add a small NFR (per-principal request limit) and one acceptance line in T025 or T028, or remove it from the diagram. |
| M12 | `01` L63, `03` L30 | BR07 "expires after 15 minutes" doesn't say *from what* (creation or approval). Does execution after approval but past `expires_at` fail? | "15 minutes from proposal creation; execution must also start before `expires_at`." |
| M13 | `05` L58, T023 | ~1,000 LLM-generated routing records, then an LLM-vs-TF-IDF comparison on the same distribution. This favours template artefacts and the generating model. | Hold out a small hand-written test slice (and/or one from a different generator). Report it separately. |
| M14 | T023 (`09` L444) | The LLM comparison needs live calls, but T023 has no budget or "not measured" clause (T024 does). | Copy T024's clause: "No paid run without cap; otherwise report LLM side as unmeasured." |
| M15 | T025, `10` L65 | OIDC validation is required, but there is no plan for testing it locally. | Say so explicitly: tests use a locally generated RSA key + JWKS fixture. Demo uses a containerized IdP (e.g., Keycloak) or the chosen provider's dev tenant. |
| M16 | `examples/evaluation_seed.jsonl` | Seed categories (`boundary`, `inventory`, `duplicate`, `stale_approval`, …) don't map onto the 5 locked primary categories in `06` L22. | Add `primary_category` from the locked taxonomy and move the current value into `tags`. |
| M17 | Seeds DEV011/DEV012 | Execution scenarios are written as a *chat message* ("Execute the approved replacement proposal") with a single principal. The seed schema can't express proposer ≠ approver, a pre-existing proposal or approval, or an API action sequence. DEV011 also allows `failed`, but a stale proposal should return to review. | Add `actors: {proposer, approver}`, `preconditions` (existing proposal/approval) and `steps` (API calls). Change DEV011's allowed states to `awaiting_approval` + new proposal. |
| M18 | Seed DEV009 | "Conflicting **active** policy" is impossible under atomic activation (`03` L60 retires the previous version of the same key). The message also has no order reference, so two outcomes are mixed together. | State that the conflict is between *two policy keys*. Add an order reference so the case tests only the conflict. |
| M19 | Seed DEV003 | Order `1042` is unique only *within* a tenant, so store-b could legitimately have its own 1042. | Add `"order_exists_in_principal_tenant": false` to the fixture. |
| M20 | Seed DEV010 | `roles` sits inside `operational_fixture_overrides`, but roles are principal data. | Remove it (the principal fixture already sets the role). |
| M21 | Python target (`10` ADR-008, `12` L23, `01_FOUNDATION` L35) | Python 3.12 is in **security-only** mode (no more binary releases). 3.13 and 3.14 are in bugfix mode, and `>=3.12,<3.13` blocks both. | Target 3.13 (or 3.14 after checking torch / sentence-transformers wheels at T001). Keep the "verify at T001" rule. |

---

## Low — polish and refinements

**Backlog and dependencies**
- **Tighter dependencies.** T014 (pure rules) depends on T013 (read tools), although it only needs the T004 schemas. Dropping that dependency lets rules be learned earlier. T023's dependency on T008 and T027's on T021 look incidental, so review them.
- **Redundant transitive dependencies.** These are harmless but noisy: T008←T003, T011←T006/T007, T012←T007, T014←T003/T004, T015←T013, T017←T014/T015, T018←T013, T020←T011/T016, T021←T007, T022←T007, T025←T016, T026←T009, T027←T002, T028←T019/T022. Keep them only if they are meant as reading pointers.
- **T001 planned files** omit `tests/unit/test_health.py`, which the foundation plan creates.

**Wording and naming**
- **Host-specific wording.** `LEARNER_PROFILE.md` L15 says "not persistent ChatGPT memory", and `DECISIONS.md` L5 says "the project selected in the conversation". Make both host-neutral, since the pack targets Copilot, Claude and Codex.
- **"completed" vs "succeeded".** BR05 says "completed replacement", while the data model says "succeeded". Use one term.
- **"pending" vs "staging"** policy versions (`02` L60 vs `03` L60). Use one term.

**Contracts and data model**
- **Hash spec.** `03` L50 describes canonical JSON well. Name the algorithm (SHA-256) and cite RFC 8785 (JCS) as the reference. Also, "signed-off envelope" reads like a cryptographic signature, but it's a hash.
- **`audit_events` append-only.** Enforce it with DB grants (`REVOKE UPDATE, DELETE`) and a test, not only by convention.
- **Missing type definitions.** `RunCaseRequest`, `CaseView` and `ProposalView` are named but not in the schema table (`04` §3). The interface signatures use `str` for IDs that are UUIDs elsewhere.

**Coach and repo guidance**
- **Skill modes.** Add an **Interview** mode; `11_PORTFOLIO_AND_DEMO.md` already has interview prompts, and the SupportOps tutor has this mode. Also spell out that `init` applies only to a standalone skill, and that `status` is the only correct command when the skill is installed inside the project repo.
- **AGENTS.md.** Add a short "Commands" section (`uv sync --locked`, `uv run pytest -q`, `uv run ruff check`, `uv run ruff format --check`) marked "valid after T001/T002". Agents use this heavily.
- **copilot-instructions.md.** Point to `.github/skills/commerce-ai-coach/` once installed. Consider path-specific `.github/instructions/tests.instructions.md` (TDD and evidence rules) and `migrations.instructions.md` (constraint and tenant rules).
- **PR template.** Add checkboxes for "`09_BACKLOG.md` and `learning/backlog.json` updated together" and "`progress.json` changed only from inspected evidence".
- **Validation claim.** Root and planning `DELIVERY_VALIDATION.md` L17 say the "standalone starter snapshot matches". That can't be checked from V4 because the snapshot isn't present. Either ship it or reword the line.

---

## Suggested fix order

1. **C1** Choose the canonical curriculum for V4.
2. **C2** Restore and install the skill folder.
3. **C3** Fix the T001 plan before any learner starts.
4. **H1–H6** One pass over the `03` and `04` contracts plus a state-transition table. These change schemas that T004 freezes, so fix them before T004 starts.
5. **H7–H8, M1** Release-gate columns, early redaction, status enum.
6. Seeds (**M16–M20**), then the remaining Medium and Low items.

---

## Resolution (applied 2026-09-15, planning baseline 1.1.0)

All findings were addressed. `python tools/verify_v4.py --sync` passes 16/16 checks now that the `.github` files are in place (moved on 2026-09-16; see "Setup status" in the root `README.md`). Details are in `DELIVERY_VALIDATION.md` and in decision D003 (`learning/DECISIONS.md`).

| Finding | Resolution |
|---|---|
| C1 two curricula | Commerce (M0-M7) chosen as the active track. New root `README.md` says so. The SupportOps `README.md` and `AGENTS.md` are marked reference-only. The project's `AGENTS.md` and the skill say to ignore SupportOps progress. Risk R16 added. |
| C2 skill unusable | Skill rebuilt in `commerce-ai-coach/`: `SKILL.md`, 5 references, `scripts/coach.py` (init/status/validate), 45 unit tests, 14 behavioral cases, `agents/openai.yaml`, and the template snapshot. Installed copy (no snapshot) at `project-planning/commerce-support-copilot/.github/skills/commerce-ai-coach/`. The helper auto-detects the project root. The loose root `SKILL.md` is replaced by a "delete me" note (manual delete needed). `13_COACH_SETUP.md` rewritten with per-host locations (Copilot, Claude Code, Codex). |
| C3 T001 plan | `[build-system]` with `uv_build` and `module-name = "commerce_support"`, a package-installed test, an import check, and a Uvicorn `--factory` run step. Executed once in a scratch directory; red/green matched the plan. Also added a note on Starlette's `httpx2` deprecation warning. |
| H1 delivery time | `orders.delivered_at` removed; the shipment record is the only source (BR03, ADR-009). |
| H2 facts shape | `OperationalFacts` replaced by `OrderFacts` (with `lines`), `StockFacts`, and `ReplacementHistory`. New `resolve_order_line`. `evaluate_replacement` is declared pure. |
| H3 model UUID | `TicketAnalysis.order_line_id` replaced by `product_mention`; the model never emits internal IDs (ADR-010). |
| H4 case binding | `cases.order_id` added; proposals for lines outside the bound order are rejected (FR08, T017, failure matrix). |
| H5 state machines | Full case and proposal transition tables in `02` §4, with `revision_requested` and `invalidated` added. The decision endpoint returns `revision_requested`. T004 encodes the enums. |
| H6 executor | Any active same-tenant manager who is not the proposer (BR07, `04`, `07`, T018). |
| H7 release levels | `required_for` on every task (MD and JSON). T012 and T019 are portfolio work. Roadmap, README, and PRD updated. The checker enforces level ordering (ADR-011). |
| H8 redaction | Log-redaction filter and test moved into T002. T022 builds on it. |
| M1 | Status enum and rules in the new `learning/PROGRESS_PROTOCOL.md` (copied to the skill); progress schema v2 adds `updated_at`. |
| M2 | `quarantined` job state; jobs link to document and policy version. |
| M3, M4 | Unique `(tenant_id, proposal_id)` on executions and on approvals. |
| M5, M6 | `tsv` column + GIN index; new `index_versions` table. |
| M7 | Upload returns 202 + `JobView` from the start. |
| M8 | `AddMessageRequest` has a length limit and `kind`; messages have `author_id` and a `kind` enum. |
| M9 | Keyword blocklist replaced by strict per-tool schemas. |
| M10 | `RECONCILIATION_REQUIRED` removed from error codes; it is only an `ActionResult` status (HTTP 202). |
| M11 | NFR08 rate limits (T028, T029), `RATE_LIMITED` error code, and failure-matrix row. |
| M12 | Expiry counts from creation; execution must start before `expires_at`. |
| M13, M14 | Hand-written challenge slice; generator recorded per routing record; T023 budget clause. |
| M15 | OIDC tests use a local RSA key and JWKS fixture (`07`, T025). |
| M16-M20 | Seed schema v2: locked-category enum, `tags`, `actors`, `preconditions`, `steps`, `allowed_final_case_states`, `expected_error_codes`. DEV003/DEV009/DEV010/DEV011/DEV012 fixed. Schema documented in `examples/README.md`. |
| M21 | Python target moved to 3.13 (ADR-008, sources S14-S17 added). |
| Low items | Dependencies reduced to direct prerequisites; T014 no longer waits on T013; T023 and T027 dependencies trimmed; host-neutral wording; succeeded/staging terminology unified; SHA-256 + RFC 8785 hash spec; `audit_events` grants; `RunCaseRequest`/`CaseView`/`ProposalView`/`MessageView`/`FeedbackRequest` defined; interface IDs use UUID; Interview mode added to the skill and curriculum; `AGENTS.md` Commands section; `.github/instructions/` for tests and migrations; PR template checklist; validation claims now reproducible via `tools/verify_v4.py`. The T001 "planned files omit the test" point is now a documented convention (tests are listed separately). |
