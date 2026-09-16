#!/usr/bin/env python3
"""Helper for the commerce-ai-coach skill.

Commands:
  init      copy the bundled project snapshot into a NEW directory
  status    summarize recorded progress and recommend the next dependency-ready task
  validate  check learning/progress.json and learning/backlog.json structure

Standard library only; Python 3.10 or newer. No network access. `status` and
`validate` never write files. The checks cover structure and links only: they
cannot prove that recorded tests really passed or that the learner understands
the material.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath

VERSION = "1.1.0"
SKILL_NAME = "commerce-ai-coach"
SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "project-template"
SKILL_PARENT_DIRS = {".github", ".claude", ".agents"}

STATUSES = ("not_started", "in_progress", "blocked", "done")
MASTERY = ("unassessed", "needs_practice", "demonstrated")
EVIDENCE_KINDS = ("test", "review", "experiment", "demo")
RESULTS = ("pass", "fail", "not_run")
SOURCES = ("observed", "learner_reported")
ASSISTANCE = ("none", "hints", "worked_example")
LEVELS = ("read_only_demo", "sandbox_mvp", "portfolio")
LEVEL_LABELS = {
    "read_only_demo": "Read-only demo",
    "sandbox_mvp": "Sandbox workflow MVP",
    "portfolio": "Complete portfolio",
}
TASK_ID = re.compile(r"^T\d{3}$")

TOP_KEYS_V1 = {"schema_version", "project_version", "current_task", "last_session", "tasks"}
TASK_KEYS_V1 = {"status", "mastery", "evidence", "mastery_evidence", "blocker"}
TASK_KEYS_V2 = TASK_KEYS_V1 | {"updated_at"}
EVIDENCE_REQUIRED = {"kind", "path", "result", "source", "summary"}
EVIDENCE_OPTIONAL = {"command"}
MASTERY_REQUIRED = {"path", "summary"}
MASTERY_OPTIONAL = {"assistance"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


class LoadError(Exception):
    """The project cannot be read well enough to validate."""


# --------------------------------------------------------------------------- helpers

def _read_json(path: Path) -> object:
    if not path.is_file():
        raise LoadError(f"missing file: {path.as_posix()}")
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise LoadError(f"invalid JSON in {path.name}: line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise LoadError(f"cannot read {path.name}: {exc}") from exc


def _is_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def check_relative_path(project: Path, value: object, where: str, report: Report) -> None:
    """Evidence paths must be project-relative, use '/', and resolve inside the project."""
    if not isinstance(value, str) or not value.strip():
        report.error(f"{where}: path must be a non-empty string")
        return
    if "\\" in value:
        report.error(f"{where}: use '/' in paths, not '\\' ({value!r})")
        return
    if PurePosixPath(value).is_absolute() or PureWindowsPath(value).drive:
        report.error(f"{where}: path must be relative to the project root ({value!r})")
        return
    if ".." in PurePosixPath(value).parts:
        report.error(f"{where}: path must not contain '..' ({value!r})")
        return
    root = project.resolve()
    target = (project / value).resolve()
    if not _is_inside(target, root):
        report.error(f"{where}: path resolves outside the project, possibly through a symlink ({value!r})")
        return
    if not target.is_file():
        report.error(f"{where}: file does not exist ({value!r})")


def _dependency_cycles(tasks: dict[str, dict]) -> list[list[str]]:
    cycles: list[list[str]] = []
    state: dict[str, int] = {}

    def visit(tid: str, stack: list[str]) -> None:
        state[tid] = 1
        stack.append(tid)
        for dep in tasks[tid].get("depends_on", []):
            if dep not in tasks:
                continue
            if state.get(dep) == 1:
                cycles.append(stack[stack.index(dep):] + [dep])
            elif state.get(dep) is None:
                visit(dep, stack)
        stack.pop()
        state[tid] = 2

    for tid in sorted(tasks):
        if tid not in state:
            visit(tid, [])
    return cycles


# --------------------------------------------------------------------------- loading

def load_project(project: Path) -> tuple[dict, dict]:
    if not project.is_dir():
        raise LoadError(f"project directory not found: {project.as_posix()}")
    backlog = _read_json(project / "learning" / "backlog.json")
    progress = _read_json(project / "learning" / "progress.json")
    if not isinstance(backlog, dict) or not isinstance(backlog.get("tasks"), list):
        raise LoadError("learning/backlog.json must be an object with a 'tasks' list")
    if not isinstance(progress, dict) or not isinstance(progress.get("tasks"), dict):
        raise LoadError("learning/progress.json must be an object with a 'tasks' object")
    return backlog, progress


def backlog_index(backlog: dict, report: Report) -> dict[str, dict]:
    tasks: dict[str, dict] = {}
    schema = backlog.get("schema_version")
    for i, task in enumerate(backlog["tasks"]):
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            report.error(f"backlog task #{i + 1}: missing string 'id'")
            continue
        tid = task["id"]
        if not TASK_ID.match(tid):
            report.error(f"backlog {tid}: id must look like T001")
        if tid in tasks:
            report.error(f"backlog {tid}: duplicate id")
            continue
        deps = task.get("depends_on", [])
        if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
            report.error(f"backlog {tid}: depends_on must be a list of task IDs")
            deps = []
        task = {**task, "depends_on": deps}
        if isinstance(schema, int) and schema >= 2 and task.get("required_for") not in LEVELS:
            report.error(f"backlog {tid}: required_for must be one of {', '.join(LEVELS)}")
        tasks[tid] = task
    for tid, task in tasks.items():
        for dep in task["depends_on"]:
            if dep not in tasks:
                report.error(f"backlog {tid}: unknown dependency {dep}")
            elif dep == tid:
                report.error(f"backlog {tid}: depends on itself")
            else:
                a, b = task.get("required_for"), tasks[dep].get("required_for")
                if a in LEVELS and b in LEVELS and LEVELS.index(b) > LEVELS.index(a):
                    report.error(f"backlog {tid} ({a}) depends on {dep} ({b}), which belongs to a higher release level")
    for cycle in _dependency_cycles(tasks):
        report.error("backlog dependency cycle: " + " -> ".join(cycle))
    return tasks


# --------------------------------------------------------------------------- validation

def validate_project(project: Path) -> tuple[Report, dict[str, dict], dict]:
    """Return (report, backlog tasks, progress). Raises LoadError if unreadable."""
    report = Report()
    backlog, progress = load_project(project)
    tasks = backlog_index(backlog, report)

    schema = progress.get("schema_version")
    if schema not in (1, 2):
        report.error("progress: schema_version must be 1 or 2")
    top_keys = TOP_KEYS_V1
    task_keys = TASK_KEYS_V2 if schema == 2 else TASK_KEYS_V1
    for key in sorted(set(progress) - top_keys):
        report.error(f"progress: unknown top-level key '{key}'")
    for key in sorted(top_keys - set(progress)):
        report.error(f"progress: missing top-level key '{key}'")

    if progress.get("project_version") != backlog.get("project_version"):
        report.warn(
            f"progress project_version {progress.get('project_version')!r} differs from backlog "
            f"{backlog.get('project_version')!r}; record the planning change in learning/decisions.md"
        )

    records: dict = progress["tasks"]
    for tid in sorted(set(tasks) - set(records)):
        report.error(f"progress: backlog task {tid} has no progress record")
    for tid in sorted(set(records) - set(tasks)):
        report.error(f"progress: {tid} is not a backlog task")

    current = progress.get("current_task")
    if current is not None and current not in tasks:
        report.error(f"progress: current_task {current!r} is not a backlog task")
    for key in ("last_session",):
        value = progress.get(key)
        if value is not None and not _is_timestamp(value):
            report.error(f"progress: {key} must be null or an ISO-8601 timestamp with an offset")

    for tid in sorted(records):
        rec = records[tid]
        where = f"progress {tid}"
        if not isinstance(rec, dict):
            report.error(f"{where}: record must be an object")
            continue
        for key in sorted(set(rec) - task_keys):
            report.error(f"{where}: unknown key '{key}'")
        required = task_keys if schema == 2 else TASK_KEYS_V1
        for key in sorted(required - set(rec)):
            report.error(f"{where}: missing key '{key}'")

        status = rec.get("status")
        mastery = rec.get("mastery")
        if status not in STATUSES:
            report.error(f"{where}: status must be one of {', '.join(STATUSES)}")
        if mastery not in MASTERY:
            report.error(f"{where}: mastery must be one of {', '.join(MASTERY)}")
        if rec.get("updated_at") is not None and not _is_timestamp(rec.get("updated_at")):
            report.error(f"{where}: updated_at must be null or an ISO-8601 timestamp with an offset")

        blocker = rec.get("blocker")
        if status == "blocked":
            if not isinstance(blocker, str) or not blocker.strip():
                report.error(f"{where}: a blocked task needs a non-empty blocker description")
        elif blocker is not None:
            report.error(f"{where}: blocker must be null unless status is 'blocked'")

        evidence = rec.get("evidence", [])
        passing = {"test": False, "review": False}
        if not isinstance(evidence, list):
            report.error(f"{where}: evidence must be a list")
            evidence = []
        for i, item in enumerate(evidence):
            ew = f"{where} evidence[{i}]"
            if not isinstance(item, dict):
                report.error(f"{ew}: entry must be an object")
                continue
            for key in sorted(EVIDENCE_REQUIRED - set(item)):
                report.error(f"{ew}: missing '{key}'")
            for key in sorted(set(item) - EVIDENCE_REQUIRED - EVIDENCE_OPTIONAL):
                report.error(f"{ew}: unknown key '{key}'")
            if item.get("kind") not in EVIDENCE_KINDS:
                report.error(f"{ew}: kind must be one of {', '.join(EVIDENCE_KINDS)}")
            if item.get("result") not in RESULTS:
                report.error(f"{ew}: result must be one of {', '.join(RESULTS)}")
            if item.get("source") not in SOURCES:
                report.error(f"{ew}: source must be one of {', '.join(SOURCES)}")
            if not isinstance(item.get("summary"), str) or not item.get("summary", "").strip():
                report.error(f"{ew}: summary must be a non-empty string")
            if "command" in item and not isinstance(item["command"], str):
                report.error(f"{ew}: command must be a string")
            errors_before = len(report.errors)
            check_relative_path(project, item.get("path"), ew, report)
            path_ok = len(report.errors) == errors_before
            if path_ok and item.get("result") == "pass" and item.get("kind") in passing:
                passing[item["kind"]] = True

        mastery_items = rec.get("mastery_evidence", [])
        independent = False
        if not isinstance(mastery_items, list):
            report.error(f"{where}: mastery_evidence must be a list")
            mastery_items = []
        for i, item in enumerate(mastery_items):
            mw = f"{where} mastery_evidence[{i}]"
            if not isinstance(item, dict):
                report.error(f"{mw}: entry must be an object")
                continue
            for key in sorted(MASTERY_REQUIRED - set(item)):
                report.error(f"{mw}: missing '{key}'")
            for key in sorted(set(item) - MASTERY_REQUIRED - MASTERY_OPTIONAL):
                report.error(f"{mw}: unknown key '{key}'")
            if schema == 2 and "assistance" not in item:
                report.error(f"{mw}: missing 'assistance' (none, hints, or worked_example)")
            if "assistance" in item and item["assistance"] not in ASSISTANCE:
                report.error(f"{mw}: assistance must be one of {', '.join(ASSISTANCE)}")
            if not isinstance(item.get("summary"), str) or not item.get("summary", "").strip():
                report.error(f"{mw}: summary must be a non-empty string")
            check_relative_path(project, item.get("path"), mw, report)
            if item.get("assistance", "none") in ("none", "hints"):
                independent = True

        if mastery == "demonstrated":
            if not mastery_items:
                report.error(f"{where}: 'demonstrated' mastery needs at least one mastery_evidence entry")
            elif not independent:
                report.error(f"{where}: 'demonstrated' mastery needs evidence produced without a worked example")
        if mastery == "needs_practice" and not mastery_items:
            report.error(f"{where}: 'needs_practice' mastery needs at least one mastery_evidence entry")

        if tid in tasks:
            undone = [d for d in tasks[tid]["depends_on"]
                      if isinstance(records.get(d), dict) and records[d].get("status") != "done"]
            if status == "done":
                if not passing["test"]:
                    report.error(f"{where}: 'done' needs a passing test evidence entry with an existing file")
                if not passing["review"]:
                    report.error(f"{where}: 'done' needs a passing review evidence entry with an existing file")
                if undone:
                    report.error(f"{where}: 'done' but dependencies are not done: {', '.join(undone)}")
            elif status in ("in_progress", "blocked") and undone:
                report.warn(f"{where}: {status} while dependencies are not done: {', '.join(undone)}")
    return report, tasks, progress


# --------------------------------------------------------------------------- status

def summarize(tasks: dict[str, dict], progress: dict) -> dict:
    records = progress["tasks"]

    def status_of(tid: str) -> str:
        rec = records.get(tid)
        return rec.get("status", "not_started") if isinstance(rec, dict) else "not_started"

    done = {tid for tid in tasks if status_of(tid) == "done"}
    ready = [tid for tid in sorted(tasks)
             if status_of(tid) in ("not_started", "in_progress")
             and all(d in done for d in tasks[tid]["depends_on"])]
    current = progress.get("current_task")
    if current in tasks and status_of(current) in ("not_started", "in_progress") and current in ready:
        recommended = current
    elif ready:
        in_progress = [t for t in ready if status_of(t) == "in_progress"]
        recommended = in_progress[0] if in_progress else ready[0]
    else:
        recommended = None

    milestones: dict[str, list[int]] = {}
    for tid in sorted(tasks):
        ms = str(tasks[tid].get("milestone", "?"))
        milestones.setdefault(ms, [0, 0])
        milestones[ms][1] += 1
        if tid in done:
            milestones[ms][0] += 1

    levels = {}
    for i, level in enumerate(LEVELS):
        needed = [t for t in tasks if tasks[t].get("required_for") in LEVELS[: i + 1]]
        if needed:
            levels[level] = {"done": sum(t in done for t in needed), "total": len(needed),
                             "reached": all(t in done for t in needed)}

    counts = {s: 0 for s in STATUSES}
    mastery = {m: 0 for m in MASTERY}
    for tid in tasks:
        st = status_of(tid)
        if st in counts:
            counts[st] += 1
        rec = records.get(tid)
        if isinstance(rec, dict) and rec.get("mastery") in mastery:
            mastery[rec["mastery"]] += 1

    blocked = {tid: records[tid].get("blocker") for tid in sorted(tasks) if status_of(tid) == "blocked"}
    return {
        "project_version": progress.get("project_version"),
        "current_task": current,
        "last_session": progress.get("last_session"),
        "status_counts": counts,
        "mastery_counts": mastery,
        "milestones": {k: {"done": v[0], "total": v[1]} for k, v in milestones.items()},
        "release_levels": levels,
        "ready_tasks": ready,
        "blocked_tasks": blocked,
        "recommended_task": recommended,
        "recommended_title": tasks[recommended].get("title") if recommended else None,
    }


# --------------------------------------------------------------------------- project discovery

def find_project(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    parent = SKILL_DIR.parent
    if parent.name == "skills" and parent.parent.name in SKILL_PARENT_DIRS:
        root = parent.parent.parent
        if (root / "learning" / "progress.json").is_file():
            return root
    cwd = Path.cwd()
    if (cwd / "learning" / "progress.json").is_file():
        return cwd
    raise LoadError(
        "could not find the project: pass --project PATH, run from the project root, "
        "or install the skill under <project>/.github/skills/"
    )


# --------------------------------------------------------------------------- commands

def _print_report(report: Report) -> None:
    for msg in report.errors:
        print(f"ERROR   {msg}")
    for msg in report.warnings:
        print(f"WARNING {msg}")


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        project = find_project(args.project)
        report, tasks, _ = validate_project(project)
    except LoadError as exc:
        _emit_load_error(args, exc)
        return 2
    if args.json:
        print(json.dumps({"ok": not report.errors, "tasks": len(tasks),
                          "errors": report.errors, "warnings": report.warnings}, indent=2))
    else:
        _print_report(report)
        verdict = "OK" if not report.errors else "FAILED"
        print(f"{verdict}: {len(tasks)} tasks, {len(report.errors)} errors, {len(report.warnings)} warnings "
              f"({project.as_posix()})")
        print("Structure and links only: this does not prove recorded tests passed.")
    return 0 if not report.errors else 1


def cmd_status(args: argparse.Namespace) -> int:
    try:
        project = find_project(args.project)
        report, tasks, progress = validate_project(project)
    except LoadError as exc:
        _emit_load_error(args, exc)
        return 2
    summary = summarize(tasks, progress)
    summary["validation"] = {"errors": len(report.errors), "warnings": len(report.warnings)}
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0
    print(f"Project {project.as_posix()} (planning {summary['project_version']})")
    counts = summary["status_counts"]
    print("Tasks: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    print("Mastery: " + ", ".join(f"{k} {v}" for k, v in summary["mastery_counts"].items()))
    print("Milestones: " + ", ".join(f"{k} {v['done']}/{v['total']}" for k, v in sorted(summary["milestones"].items())))
    for level, info in summary["release_levels"].items():
        mark = "reached" if info["reached"] else "not reached"
        print(f"{LEVEL_LABELS[level]}: {info['done']}/{info['total']} tasks done ({mark})")
    for tid, blocker in summary["blocked_tasks"].items():
        print(f"Blocked {tid}: {blocker}")
    if summary["recommended_task"]:
        print(f"Next: {summary['recommended_task']} - {summary['recommended_title']}")
    else:
        print("Next: no dependency-ready task (all done, or remaining tasks are blocked)")
    if report.errors or report.warnings:
        print(f"Validation: {len(report.errors)} errors, {len(report.warnings)} warnings; run 'validate' for details")
    return 0


def _emit_load_error(args: argparse.Namespace, exc: Exception) -> None:
    if getattr(args, "json", False):
        print(json.dumps({"ok": False, "load_error": str(exc)}, indent=2))
    else:
        print(f"ERROR   {exc}", file=sys.stderr)


def _template_symlinks(root: Path) -> list[Path]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in dirnames + filenames:
            path = Path(dirpath) / name
            if path.is_symlink():
                found.append(path)
    return found


def cmd_init(args: argparse.Namespace) -> int:
    dest = Path(args.project)
    template = TEMPLATE_DIR
    if not template.is_dir():
        print("ERROR   this copy of the skill has no assets/project-template (it is a repository-installed "
              "copy); use 'status' inside the existing project instead", file=sys.stderr)
        return 2
    if os.path.lexists(dest):
        print(f"ERROR   destination already exists: {dest.as_posix()} (init only creates a new directory)",
              file=sys.stderr)
        return 2
    dest_abs = dest.absolute()
    if _is_inside(dest_abs.parent.resolve() / dest_abs.name, SKILL_DIR):
        print("ERROR   destination must not be inside the skill folder", file=sys.stderr)
        return 2
    if not dest_abs.parent.is_dir():
        print(f"ERROR   parent directory does not exist: {dest_abs.parent.as_posix()}", file=sys.stderr)
        return 2
    links = _template_symlinks(template)
    if links:
        print("ERROR   the template contains symlinks, refusing to copy: "
              + ", ".join(p.relative_to(template).as_posix() for p in links), file=sys.stderr)
        return 2

    tmp = dest_abs.parent / f".{dest_abs.name}.coach-init-{os.getpid()}"
    try:
        shutil.copytree(template, tmp, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        installed = None
        if args.install_skill:
            target = tmp / ".github" / "skills" / SKILL_NAME
            if target.exists():
                print(f"NOTE    template already contains {target.relative_to(tmp).as_posix()}; not copying")
            else:
                shutil.copytree(SKILL_DIR, target,
                                ignore=shutil.ignore_patterns("assets", "__pycache__", "*.pyc"))
                installed = target.relative_to(tmp).as_posix()
        os.rename(tmp, dest_abs)
    except OSError as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"ERROR   copy failed, nothing was created: {exc}", file=sys.stderr)
        return 2

    print(f"Created {dest.as_posix()} from the bundled snapshot (no Git, no dependencies, no network).")
    if installed:
        print(f"Installed the skill at {installed}.")
    try:
        report, _, _ = validate_project(dest_abs)
        print(f"Validation: {len(report.errors)} errors, {len(report.warnings)} warnings.")
    except LoadError as exc:
        print(f"WARNING created project could not be validated: {exc}")
    print("Next: read README.md, then run 'status' for the first task.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="coach.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="copy the project snapshot into a new directory")
    p_init.add_argument("--project", required=True, help="new directory to create (must not exist)")
    p_init.add_argument("--install-skill", action="store_true",
                        help=f"also copy this skill (without assets) to .github/skills/{SKILL_NAME}")
    p_init.set_defaults(func=cmd_init)

    for name, func, text in (("status", cmd_status, "summarize progress and recommend the next task"),
                             ("validate", cmd_validate, "check progress and backlog structure")):
        p = sub.add_parser(name, help=text)
        p.add_argument("--project", help="project root (auto-detected when the skill is installed in it)")
        p.add_argument("--json", action="store_true", help="machine-readable output")
        p.set_defaults(func=func)
    return parser


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 10):
        print("ERROR   Python 3.10 or newer is required", file=sys.stderr)
        return 2
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
