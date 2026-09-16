#!/usr/bin/env python3
"""Maintainer checks for the AI Engineering Project Lab V4 bundle.

Usage (from the V4 folder):
    python tools/verify_v4.py            # run every check, exit 1 on any error
    python tools/verify_v4.py --sync     # first refresh the two derived copies, then check

Derived copies (never edit them by hand):
  * project-planning/commerce-support-copilot/.github/skills/commerce-ai-coach/
      = commerce-ai-coach/ without assets/
  * commerce-ai-coach/assets/project-template/
      = project-planning/commerce-support-copilot/ without .github/skills/

Standard library only; Python 3.10+. No network access.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "project-planning" / "commerce-support-copilot"
SKILL = ROOT / "commerce-ai-coach"
INSTALLED = PROJECT / ".github" / "skills" / "commerce-ai-coach"
TEMPLATE = SKILL / "assets" / "project-template"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
PENDING = PROJECT / "github-updates"
GITHUB_SOURCES = ["copilot-instructions.md", "pull_request_template.md",
                  "instructions/tests.instructions.md", "instructions/migrations.instructions.md",
                  "instructions/learning.instructions.md"]
CATEGORIES = {"eligible_replacement", "missing_information", "manual_escalation",
              "authorization_or_injection", "failure_recovery"}
LOCKED_COUNTS = {"eligible_replacement": 40, "missing_information": 20, "manual_escalation": 20,
                 "authorization_or_injection": 20, "failure_recovery": 20}
LEVELS = ("read_only_demo", "sandbox_mvp", "portfolio")
LEVEL_LABEL = {"read_only_demo": "Read-only demo (and every higher level)",
               "sandbox_mvp": "Sandbox workflow MVP (and complete portfolio)",
               "portfolio": "Complete portfolio only"}

errors: list[str] = []
passed: list[str] = []


def check(name: str, problems: list[str]) -> None:
    if problems:
        errors.extend(f"{name}: {p}" for p in problems)
        print(f"FAIL  {name} ({len(problems)} problems)")
        for p in problems[:20]:
            print(f"      - {p}")
    else:
        passed.append(name)
        print(f"PASS  {name}")


def sync() -> None:
    if PENDING.exists():
        sys.exit(f"Move the contents of {PENDING.relative_to(ROOT).as_posix()}/ into "
                 f"{(PROJECT / '.github').relative_to(ROOT).as_posix()}/ (replace existing files), "
                 "delete the empty github-updates folder, then run --sync again.")
    if INSTALLED.exists():
        shutil.rmtree(INSTALLED)
    shutil.copytree(SKILL, INSTALLED, ignore=shutil.ignore_patterns("assets", "__pycache__", "*.pyc", ".DS_Store"))
    if TEMPLATE.exists():
        shutil.rmtree(TEMPLATE)

    def ignore(directory: str, names: list[str]) -> set[str]:
        skipped = set(IGNORE(directory, names))
        if Path(directory).resolve() == (PROJECT / ".github").resolve():
            skipped.add("skills")
        return skipped

    shutil.copytree(PROJECT, TEMPLATE, ignore=ignore)
    print("synced installed skill copy and project template")


def tree(root: Path, exclude_top: set[str] | None = None) -> dict[str, Path]:
    files = {}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if "__pycache__" in rel.parts or path.suffix == ".pyc":
            continue
        if exclude_top and rel.parts and "/".join(rel.parts[:2]) in exclude_top:
            continue
        if path.is_file():
            files[rel.as_posix()] = path
    return files


def compare(a: Path, b: Path, exclude_a: set[str] | None = None, exclude_b: set[str] | None = None) -> list[str]:
    ta, tb = tree(a, exclude_a), tree(b, exclude_b)
    problems = [f"only in {a.name}: {k}" for k in sorted(set(ta) - set(tb))]
    problems += [f"only in copy: {k}" for k in sorted(set(tb) - set(ta))]
    problems += [f"differs: {k}" for k in sorted(set(ta) & set(tb)) if not filecmp.cmp(ta[k], tb[k], shallow=False)]
    return problems


def load_backlog() -> dict:
    return json.loads((PROJECT / "learning" / "backlog.json").read_text(encoding="utf-8"))


def parse_backlog_md() -> dict[str, dict]:
    md = (PROJECT / "docs" / "09_BACKLOG.md").read_text(encoding="utf-8")
    parts = re.split(r"^## (T\d{3}) - ", md, flags=re.M)
    tasks = {}
    for i in range(1, len(parts), 2):
        tid, body = parts[i], parts[i + 1]
        head = re.search(r"\*\*Milestone:\*\* (M\d) \| \*\*Dependencies:\*\* (.*?) \| \*\*Requirements:\*\* (.*)", body)
        req_for = re.search(r"\*\*Required for:\*\* (.*)", body).group(1).strip()
        files = re.findall(r"`([^`]+)`", re.search(r"\*\*Planned files:\*\*(.*)", body).group(1))
        extra = re.search(r"\*\*Additional tests:\*\*(.*)", body)
        acceptance = re.findall(r"^- (.*)$", body.split("**Acceptance behaviors:**")[1].split("**Focused test")[0], flags=re.M)
        tasks[tid] = {
            "title": body.split("\n", 1)[0].strip(),
            "milestone": head.group(1),
            "depends_on": [] if head.group(2).strip() == "none" else [d.strip() for d in head.group(2).split(",")],
            "requirements": [r.strip() for r in head.group(3).split(",")],
            "required_for": req_for,
            "files": files,
            "test_path": re.search(r"\*\*Focused test:\*\* `([^`]+)`", body).group(1),
            "additional_tests": re.findall(r"`([^`]+)`", extra.group(1).split("(")[0]) if extra else [],
            "acceptance": acceptance,
            "teach_back": re.search(r"\*\*Teach-back:\*\* (.*)", body).group(1).strip(),
            "concepts": re.search(r"\*\*Learning focus:\*\* (.*)", body).group(1).strip().rstrip(".").split(", "),
        }
    return tasks


def check_backlog_sync() -> list[str]:
    js = {t["id"]: t for t in load_backlog()["tasks"]}
    md = parse_backlog_md()
    problems = []
    if set(js) != set(md):
        problems.append(f"task sets differ: json-only {sorted(set(js) - set(md))}, md-only {sorted(set(md) - set(js))}")
    for tid in sorted(set(js) & set(md)):
        for key, value in md[tid].items():
            expected = LEVEL_LABEL.get(js[tid][key]) if key == "required_for" else js[tid][key]
            if value != expected:
                problems.append(f"{tid}.{key}: md={value!r} json={expected!r}")
    return problems


def check_graph() -> list[str]:
    tasks = {t["id"]: t for t in load_backlog()["tasks"]}
    problems = []
    memo: dict[str, set[str]] = {}

    def anc(tid: str, stack: tuple = ()) -> set[str]:
        if tid in stack:
            problems.append("cycle: " + " -> ".join(stack + (tid,)))
            return set()
        if tid not in memo:
            s: set[str] = set()
            for d in tasks[tid]["depends_on"]:
                if d not in tasks:
                    problems.append(f"{tid}: unknown dependency {d}")
                    continue
                s |= {d} | anc(d, stack + (tid,))
            memo[tid] = s
        return memo[tid]

    for tid, t in tasks.items():
        anc(tid)
        deps = t["depends_on"]
        for d in deps:
            if d in tasks and any(d in anc(o) for o in deps if o != d):
                problems.append(f"{tid}: dependency {d} is indirect (listed deps must be direct)")
            if d in tasks and LEVELS.index(tasks[d]["required_for"]) > LEVELS.index(t["required_for"]):
                problems.append(f"{tid} ({t['required_for']}) depends on {d} ({tasks[d]['required_for']})")
    expected = {"read_only_demo": [f"T{i:03d}" for i in range(1, 12)],
                "sandbox_mvp": ["T013", "T014", "T015", "T016", "T017", "T018", "T020"]}
    for level, ids in expected.items():
        actual = sorted(t for t in tasks if tasks[t]["required_for"] == level)
        if actual != ids:
            problems.append(f"{level} tasks {actual} differ from the roadmap {ids}")
    return problems


def check_requirements() -> list[str]:
    prd = (PROJECT / "docs" / "01_PRD.md").read_text(encoding="utf-8")
    reqs = re.findall(r"^\| ((?:N?FR)\d\d) \|", prd, flags=re.M)
    tasks = load_backlog()["tasks"]
    problems = []
    if len(reqs) != len(set(reqs)):
        problems.append("duplicate requirement IDs in PRD")
    used = {r for t in tasks for r in t["requirements"]}
    problems += [f"{r} has no task" for r in reqs if r not in used]
    problems += [f"{r} used by a task but not defined in the PRD" for r in sorted(used - set(reqs))]
    trace = (PROJECT / "docs" / "TRACEABILITY.md").read_text(encoding="utf-8")
    rows = {m.group(1): m for m in re.finditer(r"^\| (N?FR\d\d) \| (.*?) \| (.*?) \|$", trace, flags=re.M)}
    for r in reqs:
        ts = [t for t in tasks if r in t["requirements"]]
        if r not in rows:
            problems.append(f"TRACEABILITY missing {r}")
            continue
        listed = [x.strip() for x in rows[r].group(2).split(",")]
        if listed != [t["id"] for t in ts]:
            problems.append(f"TRACEABILITY {r} tasks {listed} != backlog {[t['id'] for t in ts]}")
        tests = re.findall(r"`([^`]+)`", rows[r].group(3))
        if tests != [t["test_path"] for t in ts[:3]]:
            problems.append(f"TRACEABILITY {r} tests out of date")
    return problems


def check_progress() -> list[str]:
    progress = json.loads((PROJECT / "learning" / "progress.json").read_text(encoding="utf-8"))
    backlog = load_backlog()
    problems = []
    if set(progress["tasks"]) != {t["id"] for t in backlog["tasks"]}:
        problems.append("progress task set differs from backlog")
    if progress.get("project_version") != backlog.get("project_version"):
        problems.append("progress and backlog project_version differ")
    if any(r["status"] != "not_started" or r["mastery"] != "unassessed" or r["evidence"] for r in progress["tasks"].values()):
        problems.append("starter progress should be all not_started/unassessed with no evidence")
    return problems


def check_json_files() -> list[str]:
    problems = []
    for base in (PROJECT, SKILL):
        for path in list(base.rglob("*.json")) + list(base.rglob("*.jsonl")):
            if "project-template" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
                if path.suffix == ".jsonl":
                    for n, line in enumerate(text.splitlines(), 1):
                        if line.strip():
                            json.loads(line)
                else:
                    json.loads(text)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                problems.append(f"{path.relative_to(ROOT).as_posix()}: {exc}")
    for path in list(PROJECT.rglob("*.md")):
        for block in re.findall(r"```json\n(.*?)```", path.read_text(encoding="utf-8"), flags=re.S):
            try:
                json.loads(block)
            except json.JSONDecodeError:
                # single-line examples in a block are checked line by line
                try:
                    for line in block.strip().splitlines():
                        json.loads(line)
                except json.JSONDecodeError as exc:
                    problems.append(f"{path.relative_to(ROOT).as_posix()}: fenced JSON does not parse ({exc})")
    return problems


def check_seeds() -> list[str]:
    problems = []
    lines = (PROJECT / "examples" / "evaluation_seed.jsonl").read_text(encoding="utf-8").splitlines()
    seeds = [json.loads(l) for l in lines if l.strip()]
    required = {"id", "schema_version", "split", "primary_category", "tags", "message", "actors", "clock",
                "operational_fixture", "policy_fixture", "preconditions", "steps",
                "allowed_final_case_states", "expected_error_codes", "prohibited_effects", "note"}
    arch = (PROJECT / "docs" / "02_ARCHITECTURE.md").read_text(encoding="utf-8")
    case_states = set(re.findall(r"`([a-z_]+)`", arch.split("### Case workflow states")[1].split("|")[0]))
    evaluation = (PROJECT / "docs" / "06_EVALUATION_AND_TESTING.md").read_text(encoding="utf-8")
    documented = dict(re.findall(r"^\| `([a-z_]+)` \| (\d+) \|", evaluation, flags=re.M))
    if {k: int(v) for k, v in documented.items()} != LOCKED_COUNTS:
        problems.append(f"06 locked categories {documented} != {LOCKED_COUNTS}")
    if sum(LOCKED_COUNTS.values()) != 120:
        problems.append("locked counts do not sum to 120")
    if len(seeds) != 12 or len({s.get('id') for s in seeds}) != 12:
        problems.append("expected 12 uniquely identified seeds")
    for s in seeds:
        sid = s.get("id")
        if set(s) != required:
            problems.append(f"{sid}: keys differ: missing {sorted(required - set(s))}, extra {sorted(set(s) - required)}")
        if s.get("primary_category") not in CATEGORIES:
            problems.append(f"{sid}: unknown primary_category {s.get('primary_category')}")
        bad = set(s.get("allowed_final_case_states", [])) - case_states
        if bad:
            problems.append(f"{sid}: unknown case states {sorted(bad)}")
        actors = s.get("actors", {})
        if "approver" in actors and actors["approver"]["user_key"] == actors["proposer"]["user_key"]:
            problems.append(f"{sid}: approver must differ from proposer")
        if "roles" in json.dumps(s.get("operational_fixture", {})):
            problems.append(f"{sid}: roles belong in actors, not the operational fixture")
        uses_approver = any(step.get("actor") == "approver" for step in s.get("steps", []))
        if uses_approver and "approver" not in actors:
            problems.append(f"{sid}: a step uses an approver that is not defined")
    return problems


def check_links() -> list[str]:
    problems = []
    for base in (ROOT,):
        for md in base.rglob("*.md"):
            rel = md.relative_to(ROOT)
            if "project-template" in rel.parts or "supportops-ai-project-lab-starter" in rel.parts:
                continue
            text = md.read_text(encoding="utf-8")
            text = re.sub(r"```.*?```", "", text, flags=re.S)
            for link in re.findall(r"\]\(([^)\s]+)\)", text):
                if link.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = (md.parent / link.split("#")[0]).resolve()
                if not target.exists():
                    problems.append(f"{rel.as_posix()}: broken link {link}")
    return problems


def check_skill(folder: Path, standalone: bool) -> list[str]:
    problems = []
    if not (folder / "SKILL.md").is_file():
        hint = "" if standalone else " (run: python tools/verify_v4.py --sync)"
        return [f"{folder.relative_to(ROOT).as_posix()}/SKILL.md is missing{hint}"]
    text = (folder / "SKILL.md").read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not fm:
        return ["SKILL.md has no frontmatter"]
    name = re.search(r"^name: (.+)$", fm.group(1), flags=re.M).group(1).strip()
    desc = re.search(r"^description: (.+)$", fm.group(1), flags=re.M).group(1).strip()
    if name != folder.name:
        problems.append(f"name {name!r} does not match folder {folder.name!r}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append("name violates the Agent Skills naming rules")
    if not 1 <= len(desc) <= 1024:
        problems.append(f"description length {len(desc)} outside 1-1024")
    if len(text.splitlines()) > 500:
        problems.append("SKILL.md longer than 500 lines")
    body = text[fm.end():]
    for ref in set(re.findall(r"\]\(([^)]+)\)", body)) | set(re.findall(r"`((?:scripts|tests|references)/[^`\s]+)`", body)):
        if not (folder / ref).exists():
            problems.append(f"referenced resource missing: {ref}")
    if standalone and not (folder / "assets" / "project-template" / "README.md").is_file():
        problems.append("standalone skill lacks assets/project-template")
    if not standalone and (folder / "assets").exists():
        problems.append("installed copy must not contain assets/")
    return problems


def check_protocol_copy() -> list[str]:
    a = PROJECT / "learning" / "PROGRESS_PROTOCOL.md"
    b = SKILL / "references" / "progress-protocol.md"
    return [] if filecmp.cmp(a, b, shallow=False) else ["references/progress-protocol.md differs from learning/PROGRESS_PROTOCOL.md"]


def check_github_sources() -> list[str]:
    problems = [f"missing .github/{name}" for name in GITHUB_SOURCES if not (PROJECT / ".github" / name).is_file()]
    if PENDING.exists():
        problems.append("github-updates/ still exists: move its contents into .github/ and delete it")
    return problems


def check_root_leftovers() -> list[str]:
    problems = []
    stub = ROOT / "SKILL.md"
    if stub.exists() and stub.read_text(encoding="utf-8").startswith("---"):
        problems.append("a loose root SKILL.md with frontmatter exists; hosts ignore it and it will drift. Delete it.")
    return problems


def run_helper(cmd: list[str], cwd: Path) -> tuple[int, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run([sys.executable, *cmd], cwd=cwd, capture_output=True, text=True, timeout=300, env=env)
    return result.returncode, result.stdout + result.stderr


def check_helper_tests() -> list[str]:
    code, out = run_helper(["-m", "unittest", "discover", "-s", "tests", "-v"], SKILL)
    summary = [l for l in out.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    print("      " + " | ".join(summary))
    return [] if code == 0 else ["helper unit tests failed:\n" + out[-3000:]]


def check_installed_helper() -> list[str]:
    if not (INSTALLED / "scripts" / "coach.py").is_file():
        return ["installed skill is missing (run: python tools/verify_v4.py --sync)"]
    code, out = run_helper([str(INSTALLED / "scripts" / "coach.py"), "validate"], ROOT)
    problems = [] if code == 0 else [f"installed helper validate failed: {out.strip()}"]
    code, out = run_helper([str(INSTALLED / "scripts" / "coach.py"), "status", "--json"], ROOT)
    if code != 0 or json.loads(out).get("recommended_task") != "T001":
        problems.append(f"installed helper status did not recommend T001: {out.strip()[:300]}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sync", action="store_true", help="refresh derived copies before checking")
    parser.add_argument("--skip-tests", action="store_true", help="skip running the helper unit tests")
    args = parser.parse_args()
    if args.sync:
        sync()
    print(f"V4 bundle: {ROOT}")
    print(f"Python {sys.version.split()[0]} on {sys.platform}")
    check("project .github sources in place", check_github_sources())
    check("backlog Markdown matches backlog.json", check_backlog_sync())
    check("dependency graph (acyclic, direct, level-ordered)", check_graph())
    check("requirements coverage and traceability", check_requirements())
    check("starter progress record", check_progress())
    check("JSON, JSONL, and fenced JSON parse", check_json_files())
    check("evaluation seeds (schema v2) and locked-set counts", check_seeds())
    check("relative Markdown links", check_links())
    check("standalone skill format and resources", check_skill(SKILL, standalone=True))
    check("installed skill format and resources", check_skill(INSTALLED, standalone=False))
    check("installed skill == standalone skill without assets", compare(SKILL, INSTALLED, exclude_a={"assets/project-template"} | {"assets"}))
    check("template snapshot == project without .github/skills", compare(PROJECT, TEMPLATE, exclude_a={".github/skills"}))
    check("progress protocol copy", check_protocol_copy())
    check("no loose root skill file", check_root_leftovers())
    if not args.skip_tests:
        check("helper unit tests", check_helper_tests())
    check("installed helper validate/status on the project", check_installed_helper())
    print(f"\n{len(passed)} checks passed, {len(errors)} problems")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
