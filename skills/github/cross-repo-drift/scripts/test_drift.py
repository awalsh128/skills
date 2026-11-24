"""Tests for drift.py. Run: python3 -m unittest discover -s skills/github/cross-repo-drift/scripts"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402
import drift  # noqa: E402

SCRIPT = Path(__file__).resolve().parent / "drift.py"


def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def fake_check(tmp, findings):
    """A check command that prints fixed findings JSON."""
    script = Path(tmp) / "check.py"
    script.write_text(f"import json; print(json.dumps({{'findings': {findings!r}}}))")
    return f"{sys.executable} {script}"


class Usage(unittest.TestCase):
    def test_bare_call_prints_usage_and_does_nothing_else(self):
        out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False)
        self.assertEqual(out.returncode, 0)
        self.assertIn("audit", out.stdout)
        self.assertIn("apply", out.stdout)


class Classify(unittest.TestCase):
    def test_action_beats_node_package(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "action.yml", "name: x")
            write(d, "package.json", "{}")
            self.assertEqual(drift.classify(d), ("github-action", "none"))

    def test_vscode_extension_with_semantic_release(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "package.json", json.dumps({"engines": {"vscode": "^1.90.0"}, "release": {}}))
            self.assertEqual(drift.classify(d), ("vscode-extension", "semantic-release"))

    def test_empty_repo_is_unclassified(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(drift.classify(d), ("unclassified", "none"))


class Exceptions(unittest.TestCase):
    def test_standing_exception_moves_finding_out_of_open(self):
        findings = [{"rule": "line-width", "category": "reflow"}, {"rule": "pin", "category": "pin"}]
        overrides = {"exceptions": [{"rule": "line-width", "reason": "vscode extension uses 100"}]}
        open_, excepted = drift.split_findings(findings, overrides)
        self.assertEqual([f["rule"] for f in open_], ["pin"])
        self.assertEqual([f["rule"] for f in excepted], ["line-width"])


class Verify(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old = C.CHECK_CMD

    def tearDown(self):
        C.CHECK_CMD = self.old

    def test_passes_only_when_the_rule_has_no_open_finding(self):
        C.CHECK_CMD = fake_check(self.tmp.name, [])
        self.assertEqual(drift.verify(self.tmp.name, "pin", 1), 0)

    def test_retries_below_the_cap_then_reports_at_the_cap(self):
        C.CHECK_CMD = fake_check(self.tmp.name, [{"rule": "pin", "category": "pin"}])
        self.assertEqual(drift.verify(self.tmp.name, "pin", 1), 1)
        self.assertEqual(drift.verify(self.tmp.name, "pin", C.MAX_APPLIER_ATTEMPTS), 2)

    def test_excepted_rule_counts_as_passing(self):
        C.CHECK_CMD = fake_check(self.tmp.name, [{"rule": "pin", "category": "pin"}])
        write(self.tmp.name, C.OVERRIDES_FILE, json.dumps({"exceptions": [{"rule": "pin", "reason": "r"}]}))
        self.assertEqual(drift.verify(self.tmp.name, "pin", 1), 0)


class AuditRepo(unittest.TestCase):
    def test_audit_reports_findings_and_leaves_the_source_repo_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "owner" / "demo"
            write(src, "package.json", json.dumps({"name": "demo"}))
            for cmd in (["init", "-q", "-b", "main"], ["add", "."],
                        ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"]):
                subprocess.run(["git", *cmd], cwd=src, check=True)
            before = subprocess.run(["git", "status", "--porcelain"], cwd=src, capture_output=True, text=True)
            old = (C.CLONE_URL, C.CHECK_CMD, C.OWNER)
            C.CLONE_URL, C.OWNER = str(Path(d) / "{owner}" / "{name}"), "owner"
            C.CHECK_CMD = fake_check(d, [{"rule": "pin", "category": "pin", "fixable": True}])
            try:
                work = Path(d) / "work"
                work.mkdir()
                result = drift.audit_repo("demo", "main", work)
            finally:
                C.CLONE_URL, C.CHECK_CMD, C.OWNER = old
            after = subprocess.run(["git", "status", "--porcelain"], cwd=src, capture_output=True, text=True)
            self.assertEqual(before.stdout, after.stdout)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["profile"], "node-package")
            self.assertEqual(result["base_branch"], "main")
            self.assertEqual(len(result["findings"]), 1)


class ApplyGuards(unittest.TestCase):
    def run_apply(self, *args, env=None):
        return subprocess.run([sys.executable, str(SCRIPT), "apply", *args], capture_output=True, text=True,
                              env={**os.environ, "DRIFT_FIX_CMD": "true", **(env or {})}, check=False)

    def test_refuses_unattended(self):
        out = self.run_apply("--repos", "a", env={"DRIFT_UNATTENDED": "1"})
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("unattended", out.stderr)

    def test_refuses_without_a_target(self):
        out = self.run_apply()
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("--repos or --report", out.stderr)

    def test_refuses_a_report_with_nothing_approved(self):
        with tempfile.TemporaryDirectory() as d:
            report = Path(d) / "r.json"
            report.write_text(json.dumps({"repos": [{"repo": "a", "findings": [{"rule": "pin"}]}]}))
            out = self.run_apply("--report", str(report))
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("approved", out.stderr)


class PlanJobs(unittest.TestCase):
    def repo(self, name, status="ok"):
        return {"repo": name, "status": status, "base_branch": "main"}

    def finding(self, rule, category="pin", path="a.yml", message="m", **extra):
        return {"rule": rule, "category": category, "path": path, "message": message, **extra}

    def test_many_findings_of_one_rule_make_one_job(self):
        repo = self.repo("a")
        items = [(repo, self.finding("unpinned-uses", message=f"pin x{i}")) for i in range(10)]
        jobs, skipped = drift.plan_jobs(items)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(skipped, [])
        self.assertEqual(jobs[0]["rules"], ["unpinned-uses"])
        self.assertEqual(jobs[0]["title"], "ci: fix 10 pin findings")
        self.assertEqual(jobs[0]["body"].count("- `unpinned-uses`"), 10)

    def test_a_single_finding_is_titled_by_its_message(self):
        jobs, _ = drift.plan_jobs([(self.repo("a"), self.finding("r", message="pin x to a full commit SHA"))])
        self.assertEqual(jobs[0]["title"], "ci: pin x to a full commit SHA")

    def test_two_rules_in_one_category_share_one_job_and_branch(self):
        repo = self.repo("a")
        jobs, _ = drift.plan_jobs([(repo, self.finding("r2")), (repo, self.finding("r1"))])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["rules"], ["r1", "r2"])

    def test_repos_and_categories_get_separate_jobs(self):
        items = [(self.repo("a"), self.finding("r")), (self.repo("b"), self.finding("r")),
                 (self.repo("a"), self.finding("s", category="reflow"))]
        jobs, _ = drift.plan_jobs(items)
        self.assertEqual({(j["repo"]["repo"], j["category"]) for j in jobs},
                         {("a", "pin"), ("b", "pin"), ("a", "reflow")})

    def test_skips_unclassified_unmapped_and_unfixable(self):
        items = [(self.repo("u", "unclassified"), self.finding("r")),
                 (self.repo("a"), self.finding("r", category="behavior")),
                 (self.repo("a"), self.finding("r", fixable=False))]
        jobs, skipped = drift.plan_jobs(items)
        self.assertEqual(jobs, [])
        self.assertEqual(len(skipped), 3)


class FixAndVerify(unittest.TestCase):
    def test_runs_every_rule_and_keeps_the_change_only_if_all_pass(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "fix.py", "import os, pathlib; pathlib.Path(os.environ['DRIFT_RULE']).touch()")
            write(d, "check.py", "import json; print(json.dumps({'findings': []}))")
            old = (C.FIX_CMD, C.CHECK_CMD)
            C.FIX_CMD, C.CHECK_CMD = f"{sys.executable} {d}/fix.py", f"{sys.executable} {d}/check.py"
            cwd, env = os.getcwd(), os.environ.get("DRIFT_RULES")
            try:
                os.chdir(d)
                os.environ["DRIFT_RULES"] = "r1,r2"
                self.assertEqual(drift.fix_and_verify(), 0)
                self.assertTrue(Path("r1").exists() and Path("r2").exists())
            finally:
                os.chdir(cwd)
                C.FIX_CMD, C.CHECK_CMD = old
                os.environ.pop("DRIFT_RULES") if env is None else os.environ.update(DRIFT_RULES=env)


class Automerge(unittest.TestCase):
    def test_requires_reviewer_pass(self):
        out = subprocess.run([sys.executable, str(SCRIPT), "automerge", "--repo", "a", "--pr", "1"],
                             capture_output=True, text=True, check=False)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("--reviewed", out.stderr)


class Tiers(unittest.TestCase):
    def test_every_tier_has_a_model_alias(self):
        self.assertEqual(set(C.TIER_MODELS), {"fast", "balanced", "deep"})


if __name__ == "__main__":
    unittest.main()
