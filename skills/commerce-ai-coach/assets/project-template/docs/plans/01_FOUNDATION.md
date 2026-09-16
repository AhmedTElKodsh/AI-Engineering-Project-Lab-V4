# Foundation Implementation Plan

**Goal:** complete T001 with a reproducible, installed Python package and a failing-then-passing HTTP test.

**Architecture:** a FastAPI application factory under `src/commerce_support`, tested through TestClient and runnable with Uvicorn. No database, model, graph, or paid service is introduced.

**Tech stack:** Python 3.13 compatibility target (ADR-008), uv with the `uv_build` backend, FastAPI, Pydantic, Uvicorn, pytest, httpx.

**Spec:** `docs/01_PRD.md` FR14/NFR06; T001 in `docs/09_BACKLOG.md`.

**Execution:** guide or pair mode by default. The coach should reveal one step at a time. The complete worked scaffold below is a reference the learner may request; it has not been implemented in this planning repository. The bundle maintainer executed it once in a scratch directory (see `DELIVERY_VALIDATION.md`); that is not evidence for the learner's T001.

## Global constraints

Use synthetic/offline inputs. Preserve existing planning files. Do not install the full future stack. Record actual commands and failures. Do not claim that a health route means the application can handle a business case. Verify uv installation and the local Python command before running setup commands. Official uv and FastAPI testing references are S11, S12, S15, and S16.

## T001: service and health contract

**Create:** `pyproject.toml`, `.python-version`, `uv.lock`, `src/commerce_support/__init__.py`, `src/commerce_support/main.py`, `tests/unit/test_health.py`.

**Produces:** an installed `commerce_support` package; `create_app() -> FastAPI`; `GET /health/live -> 200 {"status":"ok"}`.

### Step 1 - Confirm the environment

Run `python --version` (or the environment's `python3`) and `uv --version`. Record the output. If uv is missing, use the official installation instructions for the actual operating system; do not guess an OS-specific command. uv can provide the interpreter: `uv python install 3.13`. Inspect whether a `pyproject.toml` already exists before creating one.

### Step 2 - Create the minimum project metadata

The planning files already live in this repository, so do not run `uv init` over it blindly. Create this `pyproject.toml` only if none exists:

```toml
[project]
name = "commerce-support-copilot"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []

[build-system]
# `uv init --package` in a scratch directory prints the current recommended
# range; copy it here. The range below was current on 2026-09-15.
requires = ["uv_build>=0.12.14,<0.13"]
build-backend = "uv_build"

[tool.uv.build-backend]
# The distribution is "commerce-support-copilot", but the import package is
# "commerce_support", so the default module name must be overridden.
module-name = "commerce_support"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Why the `[build-system]` table matters: without it, uv installs only the dependencies, not the project itself, so `import commerce_support` works only through test-path tricks. With it, `uv sync` installs the package into `.venv` in editable mode, and the default `src/` layout is used. [S15, S16]

Set `.python-version` to `3.13`. Resolve dependencies with:

```bash
uv add fastapi pydantic uvicorn
uv add --dev pytest httpx
```

These commands resolve versions when the learner executes them. Review and commit the resulting `uv.lock`; do not paste a fabricated lockfile into the project. The environment may need package downloads but no model API key or model inference.

**Version note (checked 2026-09-15):** the FastAPI testing page still says to install `httpx`, but Starlette 1.6 (resolved with FastAPI 0.141) emits a `StarletteDeprecationWarning` recommending `httpx2` for `TestClient`. Check the current FastAPI and Starlette documentation. If you see that warning, `uv remove --dev httpx` followed by `uv add --dev httpx2` removes it. An `anyio` `DeprecationWarning` raised from inside Starlette is not caused by your code; note it in the review and move on.

### Step 3 - Write the tests before the behavior

Create `src/commerce_support/__init__.py` (empty) and put this deliberately incomplete scaffold in `src/commerce_support/main.py`:

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(title="Commerce Support Copilot")
```

Create `tests/unit/test_health.py`:

```python
from importlib.metadata import version

from fastapi.testclient import TestClient

from commerce_support.main import create_app


def test_package_is_installed_in_the_environment():
    # Fails if pyproject.toml has no [build-system]: uv would not install the project.
    assert version("commerce-support-copilot") == "0.1.0"


def test_liveness_is_offline_and_machine_readable():
    client = TestClient(create_app())
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_is_not_a_false_health_success():
    client = TestClient(create_app())
    assert client.get("/not-a-route").status_code == 404
```

Run `uv run pytest tests/unit/test_health.py -q`. Expected initial result: the liveness test fails because the route returns 404, while the package test and unknown-route test pass. If the package test or the import fails, that is a setup defect (check `[build-system]` and `module-name`), not the intended red state. Save the real output.

### Step 4 - Add the minimum behavior

Replace the scaffold with:

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Commerce Support Copilot")

    @app.get("/health/live")
    def liveness() -> dict[str, str]:
        return {"status": "ok"}

    return app
```

Run `uv run pytest tests/unit/test_health.py -q` again. Expected result after implementation: three passing tests. Do not add readiness checks, model calls, UI, or database setup to this task.

### Step 5 - See it run

Start the server with the factory flag (the module exposes `create_app()`, not a module-level `app`):

```bash
uv run uvicorn commerce_support.main:create_app --factory --reload
```

In a second terminal, request `http://127.0.0.1:8000/health/live` with a browser or `curl`, then open `http://127.0.0.1:8000/docs` to see the generated OpenAPI page. Stop the server with Ctrl+C. Record what you observed.

### Step 6 - Review, save evidence, and checkpoint

Run `uv sync --locked`, then `uv run python -c "import commerce_support; print('ok')"`, and rerun the focused tests. Inspect the diff for only the intended changes. Save red/green outputs in `learning/evidence/T001-tests.txt` and a brief review in `learning/evidence/T001-review.md`. Record which output was observed by the assistant and which was supplied by the learner. Commit only when the learner's workflow authorizes it.

A future progress entry may look like this only after the files and evidence exist (rules: `learning/PROGRESS_PROTOCOL.md`):

```json
{
  "status": "done",
  "mastery": "unassessed",
  "evidence": [
    {"kind":"test","path":"learning/evidence/T001-tests.txt","result":"pass","source":"observed","command":"uv run pytest tests/unit/test_health.py -q","summary":"Focused health and package tests passed after the documented failing route test."},
    {"kind":"review","path":"learning/evidence/T001-review.md","result":"pass","source":"observed","summary":"T001 contract, installed package, and offline boundary reviewed."}
  ],
  "mastery_evidence": [],
  "blocker": null,
  "updated_at": "2026-09-20T18:30:00+03:00"
}
```

### Step 7 - Check understanding

Ask the learner to trace an HTTP request through `create_app`, the route, and the JSON response; explain why a dependency lock is useful and what `[build-system]` changes; and predict which test fails if the route path changes. Record mastery only if a relevant demonstration is provided.

## Next work packages

T002 introduces validated configuration, the log-redaction filter, quality tools, and CI. T003 defines fixed-time policy/commerce fixtures. Use their backlog criteria to write the next small plan against the actual files created by T001; do not pretend later file layouts are already implemented.
