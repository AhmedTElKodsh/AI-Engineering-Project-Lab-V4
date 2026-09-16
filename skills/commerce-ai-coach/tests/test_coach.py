"""Tests for scripts/coach.py. Run from the skill folder:

    python -m unittest discover -s tests -v

These tests cover the helper only, not the support application or coaching behavior.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT = SKILL_DIR / "scripts" / "coach.py"
_spec = importlib.util.spec_from_file_location("coach", SCRIPT)
coach = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(coach)

HAS_TEMPLATE = coach.TEMPLATE_DIR.is_dir()


def _symlinks_supported() -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        try:
            os.symlink(tmp, os.path.join(tmp, "link"))
            return True
        except (OSError, NotImplementedError):
            return False


SYMLINKS = _symlinks_supported()


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = coach.main(argv)
    return code, out.getvalue(), err.getvalue()


def record(**overrides) -> dict:
    base = {"status": "not_started", "mastery": "unassessed", "evidence": [],
            "mastery_evidence": [], "blocker": None, "updated_at": None}
    base.update(overrides)
    return base


class MiniProject:
    """A three-task project: T001 <- T002 <- T003."""

    def __init__(self, root: Path) -> None:
        self.root = root
        (root / "learning" / "evidence").mkdir(parents=True)
        self.backlog = {
            "schema_version": 2,
            "project_version": "1.1.0",
            "tasks": [
                {"id": "T001", "title": "First", "milestone": "M0", "required_for": "read_only_demo", "depends_on": []},
                {"id": "T002", "title": "Second", "milestone": "M0", "required_for": "read_only_demo", "depends_on": ["T001"]},
                {"id": "T003", "title": "Third", "milestone": "M1", "required_for": "portfolio", "depends_on": ["T002"]},
            ],
        }
        self.progress = {
            "schema_version": 2,
            "project_version": "1.1.0",
            "current_task": None,
            "last_session": None,
            "tasks": {t: record() for t in ("T001", "T002", "T003")},
        }
        self.save()

    def save(self) -> None:
        (self.root / "learning" / "backlog.json").write_text(json.dumps(self.backlog), encoding="utf-8")
        (self.root / "learning" / "progress.json").write_text(json.dumps(self.progress), encoding="utf-8")

    def evidence_file(self, name: str) -> str:
        path = self.root / "learning" / "evidence" / name
        path.write_text("output\n", encoding="utf-8")
        return f"learning/evidence/{name}"

    def done_evidence(self, prefix: str = "T001") -> list[dict]:
        return [
            {"kind": "test", "path": self.evidence_file(f"{prefix}-tests.txt"), "result": "pass",
             "source": "observed", "summary": "tests passed"},
            {"kind": "review", "path": self.evidence_file(f"{prefix}-review.md"), "result": "pass",
             "source": "observed", "summary": "reviewed"},
        ]

    def validate(self):
        return coach.validate_project(self.root)[0]


class ProjectTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.p = MiniProject(self.tmp / "proj")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def assertError(self, report, fragment: str) -> None:
        self.assertTrue(any(fragment in e for e in report.errors),
                        f"expected an error containing {fragment!r}, got {report.errors}")


class ValidateTests(ProjectTestCase):
    def test_minimal_project_is_valid(self):
        report = self.p.validate()
        self.assertEqual(report.errors, [])

    def test_missing_progress_file_exits_2(self):
        (self.p.root / "learning" / "progress.json").unlink()
        code, _, err = run(["validate", "--project", str(self.p.root)])
        self.assertEqual(code, 2)
        self.assertIn("missing file", err)

    def test_malformed_json_exits_2(self):
        (self.p.root / "learning" / "progress.json").write_text("{not json", encoding="utf-8")
        code, _, err = run(["validate", "--project", str(self.p.root)])
        self.assertEqual(code, 2)
        self.assertIn("invalid JSON", err)

    def test_unknown_task_in_progress(self):
        self.p.progress["tasks"]["T999"] = record()
        self.p.save()
        self.assertError(self.p.validate(), "T999 is not a backlog task")

    def test_missing_task_record(self):
        del self.p.progress["tasks"]["T002"]
        self.p.save()
        self.assertError(self.p.validate(), "T002 has no progress record")

    def test_dependency_cycle(self):
        self.p.backlog["tasks"][0]["depends_on"] = ["T003"]
        self.p.save()
        self.assertError(self.p.validate(), "dependency cycle")

    def test_unknown_dependency(self):
        self.p.backlog["tasks"][1]["depends_on"] = ["T404"]
        self.p.save()
        self.assertError(self.p.validate(), "unknown dependency T404")

    def test_release_level_order(self):
        self.p.backlog["tasks"][1]["depends_on"] = ["T003"]
        self.p.backlog["tasks"][2]["depends_on"] = []
        self.p.save()
        self.assertError(self.p.validate(), "higher release level")

    def test_invalid_status(self):
        self.p.progress["tasks"]["T001"]["status"] = "finished"
        self.p.save()
        self.assertError(self.p.validate(), "status must be one of")

    def test_unknown_record_key(self):
        self.p.progress["tasks"]["T001"]["statsu"] = "done"
        self.p.save()
        self.assertError(self.p.validate(), "unknown key 'statsu'")

    def test_done_without_evidence(self):
        self.p.progress["tasks"]["T001"]["status"] = "done"
        self.p.save()
        report = self.p.validate()
        self.assertError(report, "passing test evidence")
        self.assertError(report, "passing review evidence")

    def test_done_with_missing_evidence_file(self):
        ev = self.p.done_evidence()
        (self.p.root / ev[0]["path"]).unlink()
        self.p.progress["tasks"]["T001"].update(status="done", evidence=ev)
        self.p.save()
        report = self.p.validate()
        self.assertError(report, "file does not exist")
        self.assertError(report, "passing test evidence")

    def test_done_with_evidence_is_valid(self):
        self.p.progress["tasks"]["T001"].update(status="done", evidence=self.p.done_evidence(),
                                                updated_at="2026-09-20T18:30:00+03:00")
        self.p.save()
        self.assertEqual(self.p.validate().errors, [])

    def test_learner_reported_evidence_is_accepted(self):
        ev = self.p.done_evidence()
        for item in ev:
            item["source"] = "learner_reported"
        self.p.progress["tasks"]["T001"].update(status="done", evidence=ev)
        self.p.save()
        self.assertEqual(self.p.validate().errors, [])

    def test_done_with_undone_dependency(self):
        self.p.progress["tasks"]["T002"].update(status="done", evidence=self.p.done_evidence("T002"))
        self.p.save()
        self.assertError(self.p.validate(), "dependencies are not done: T001")

    def test_in_progress_with_undone_dependency_warns(self):
        self.p.progress["tasks"]["T002"]["status"] = "in_progress"
        self.p.save()
        report = self.p.validate()
        self.assertEqual(report.errors, [])
        self.assertTrue(any("T001" in w for w in report.warnings))

    def test_path_traversal_rejected(self):
        self.p.progress["tasks"]["T001"]["evidence"] = [
            {"kind": "test", "path": "../outside.txt", "result": "fail", "source": "observed", "summary": "x"}]
        self.p.save()
        self.assertError(self.p.validate(), "must not contain '..'")

    def test_absolute_paths_rejected(self):
        for bad in ("/etc/passwd", "C:/Users/x/file.txt"):
            with self.subTest(path=bad):
                self.p.progress["tasks"]["T001"]["evidence"] = [
                    {"kind": "test", "path": bad, "result": "fail", "source": "observed", "summary": "x"}]
                self.p.save()
                self.assertError(self.p.validate(), "relative to the project root")

    def test_backslash_path_rejected(self):
        self.p.progress["tasks"]["T001"]["evidence"] = [
            {"kind": "test", "path": "learning\\evidence\\a.txt", "result": "fail", "source": "observed", "summary": "x"}]
        self.p.save()
        self.assertError(self.p.validate(), "use '/'")

    @unittest.skipUnless(SYMLINKS, "symlinks not supported here")
    def test_symlink_escape_rejected(self):
        outside = self.tmp / "secret.txt"
        outside.write_text("secret", encoding="utf-8")
        os.symlink(outside, self.p.root / "learning" / "evidence" / "link.txt")
        self.p.progress["tasks"]["T001"]["evidence"] = [
            {"kind": "test", "path": "learning/evidence/link.txt", "result": "pass", "source": "observed", "summary": "x"}]
        self.p.save()
        self.assertError(self.p.validate(), "outside the project")

    def test_evidence_enum_and_summary_checked(self):
        self.p.progress["tasks"]["T001"]["evidence"] = [
            {"kind": "screenshot", "path": self.p.evidence_file("a.txt"), "result": "ok",
             "source": "memory", "summary": ""}]
        self.p.save()
        report = self.p.validate()
        for fragment in ("kind must be", "result must be", "source must be", "summary must be"):
            self.assertError(report, fragment)

    def test_demonstrated_requires_mastery_evidence(self):
        self.p.progress["tasks"]["T001"]["mastery"] = "demonstrated"
        self.p.save()
        self.assertError(self.p.validate(), "needs at least one mastery_evidence")

    def test_demonstrated_with_worked_example_only_rejected(self):
        self.p.progress["tasks"]["T001"].update(mastery="demonstrated", mastery_evidence=[
            {"path": self.p.evidence_file("T001-teachback.md"), "summary": "explained", "assistance": "worked_example"}])
        self.p.save()
        self.assertError(self.p.validate(), "without a worked example")

    def test_demonstrated_with_independent_evidence_is_valid(self):
        self.p.progress["tasks"]["T001"].update(mastery="demonstrated", mastery_evidence=[
            {"path": self.p.evidence_file("T001-teachback.md"), "summary": "explained", "assistance": "hints"}])
        self.p.save()
        self.assertEqual(self.p.validate().errors, [])

    def test_mastery_evidence_needs_assistance_in_v2(self):
        self.p.progress["tasks"]["T001"].update(mastery="needs_practice", mastery_evidence=[
            {"path": self.p.evidence_file("T001-teachback.md"), "summary": "confused UTC and local dates"}])
        self.p.save()
        self.assertError(self.p.validate(), "missing 'assistance'")

    def test_blocked_requires_blocker(self):
        self.p.progress["tasks"]["T001"]["status"] = "blocked"
        self.p.save()
        self.assertError(self.p.validate(), "needs a non-empty blocker")

    def test_blocker_only_when_blocked(self):
        self.p.progress["tasks"]["T001"]["blocker"] = "waiting"
        self.p.save()
        self.assertError(self.p.validate(), "blocker must be null")

    def test_invalid_current_task(self):
        self.p.progress["current_task"] = "T042"
        self.p.save()
        self.assertError(self.p.validate(), "current_task 'T042'")

    def test_timestamp_needs_offset(self):
        self.p.progress["last_session"] = "2026-09-20T18:30:00"
        self.p.progress["tasks"]["T001"]["updated_at"] = "yesterday"
        self.p.save()
        report = self.p.validate()
        self.assertError(report, "last_session must be")
        self.assertError(report, "updated_at must be")

    def test_schema_v1_progress_is_accepted(self):
        self.p.progress["schema_version"] = 1
        for rec in self.p.progress["tasks"].values():
            del rec["updated_at"]
        self.p.save()
        self.assertEqual(self.p.validate().errors, [])

    def test_validate_json_output(self):
        code, out, _ = run(["validate", "--project", str(self.p.root), "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["tasks"], 3)

    def test_validate_exit_code_on_errors(self):
        self.p.progress["tasks"]["T001"]["status"] = "done"
        self.p.save()
        code, out, _ = run(["validate", "--project", str(self.p.root)])
        self.assertEqual(code, 1)
        self.assertIn("FAILED", out)


class StatusTests(ProjectTestCase):
    def snapshot(self) -> dict:
        return {p: (p.stat().st_mtime_ns, p.read_bytes()) for p in self.p.root.rglob("*") if p.is_file()}

    def test_status_is_read_only_and_recommends_first_ready_task(self):
        before = self.snapshot()
        code, out, _ = run(["status", "--project", str(self.p.root), "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(before, self.snapshot())
        data = json.loads(out)
        self.assertEqual(data["recommended_task"], "T001")
        self.assertEqual(data["ready_tasks"], ["T001"])

    def test_status_follows_dependencies_and_levels(self):
        self.p.progress["tasks"]["T001"].update(status="done", evidence=self.p.done_evidence())
        self.p.save()
        data = coach.summarize(*coach.validate_project(self.p.root)[1:])
        self.assertEqual(data["recommended_task"], "T002")
        self.assertEqual(data["release_levels"]["read_only_demo"], {"done": 1, "total": 2, "reached": False})

    def test_status_prefers_ready_current_task(self):
        self.p.backlog["tasks"][2]["depends_on"] = []
        self.p.progress["current_task"] = "T003"
        self.p.save()
        data = coach.summarize(*coach.validate_project(self.p.root)[1:])
        self.assertEqual(data["recommended_task"], "T003")

    def test_status_skips_blocked_tasks(self):
        self.p.progress["tasks"]["T001"].update(status="blocked", blocker="uv not installed")
        self.p.save()
        code, out, _ = run(["status", "--project", str(self.p.root)])
        self.assertEqual(code, 0)
        self.assertIn("Blocked T001: uv not installed", out)
        self.assertIn("no dependency-ready task", out)

    def test_autodetects_project_from_installed_skill(self):
        installed = self.p.root / ".github" / "skills" / "commerce-ai-coach"
        (installed / "scripts").mkdir(parents=True)
        shutil.copy2(SCRIPT, installed / "scripts" / "coach.py")
        result = subprocess.run([sys.executable, str(installed / "scripts" / "coach.py"), "status", "--json"],
                                cwd=self.tmp, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["recommended_task"], "T001")

    def test_missing_project_without_hint(self):
        cwd = os.getcwd()
        try:
            os.chdir(self.tmp)
            code, _, err = run(["status"])
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 2)
        self.assertIn("could not find the project", err)


class InitTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self._template = coach.TEMPLATE_DIR

    def tearDown(self) -> None:
        coach.TEMPLATE_DIR = self._template
        self._tmp.cleanup()

    def fake_template(self) -> Path:
        tpl = self.tmp / "tpl"
        MiniProject(tpl)
        (tpl / "README.md").write_text("# demo\n", encoding="utf-8")
        coach.TEMPLATE_DIR = tpl
        return tpl

    def test_refuses_existing_destination(self):
        self.fake_template()
        dest = self.tmp / "exists"
        dest.mkdir()
        code, _, err = run(["init", "--project", str(dest)])
        self.assertEqual(code, 2)
        self.assertIn("already exists", err)
        self.assertEqual(list(dest.iterdir()), [])

    def test_refuses_missing_template(self):
        coach.TEMPLATE_DIR = self.tmp / "nope"
        code, _, err = run(["init", "--project", str(self.tmp / "new")])
        self.assertEqual(code, 2)
        self.assertIn("repository-installed", err)
        self.assertFalse((self.tmp / "new").exists())

    def test_refuses_missing_parent(self):
        self.fake_template()
        code, _, err = run(["init", "--project", str(self.tmp / "a" / "b")])
        self.assertEqual(code, 2)
        self.assertIn("parent directory does not exist", err)

    def test_refuses_destination_inside_skill(self):
        self.fake_template()
        code, _, err = run(["init", "--project", str(SKILL_DIR / "tmp-should-not-exist")])
        self.assertEqual(code, 2)
        self.assertIn("inside the skill folder", err)
        self.assertFalse((SKILL_DIR / "tmp-should-not-exist").exists())

    @unittest.skipUnless(SYMLINKS, "symlinks not supported here")
    def test_refuses_template_with_symlink(self):
        tpl = self.fake_template()
        os.symlink(self.tmp, tpl / "escape")
        code, _, err = run(["init", "--project", str(self.tmp / "new")])
        self.assertEqual(code, 2)
        self.assertIn("symlinks", err)
        self.assertFalse((self.tmp / "new").exists())

    def test_init_from_fake_template_with_skill(self):
        self.fake_template()
        dest = self.tmp / "new"
        code, out, _ = run(["init", "--project", str(dest), "--install-skill"])
        self.assertEqual(code, 0)
        self.assertIn("Validation: 0 errors", out)
        installed = dest / ".github" / "skills" / "commerce-ai-coach"
        self.assertTrue((installed / "SKILL.md").is_file())
        self.assertTrue((installed / "scripts" / "coach.py").is_file())
        self.assertFalse((installed / "assets").exists())
        self.assertEqual([p.name for p in self.tmp.iterdir() if p.name.startswith(".")], [])

    @unittest.skipUnless(HAS_TEMPLATE, "standalone copy only")
    def test_bundled_template_is_valid_and_initializes(self):
        report = coach.validate_project(self._template)[0]
        self.assertEqual(report.errors, [])
        dest = self.tmp / "real"
        code, out, _ = run(["init", "--project", str(dest)])
        self.assertEqual(code, 0)
        self.assertIn("Validation: 0 errors", out)
        self.assertTrue((dest / "docs" / "09-backlog.md").is_file())
        data = coach.summarize(*coach.validate_project(dest)[1:])
        self.assertEqual(data["recommended_task"], "T001")


if __name__ == "__main__":
    unittest.main()
