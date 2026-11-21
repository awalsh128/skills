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
