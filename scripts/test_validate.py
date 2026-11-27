"""Tests for validate.py. Run: python3 -m unittest discover -s scripts"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

PLUGIN_JSON = ".claude-plugin/plugin.json"
MARKETPLACE_JSON = ".claude-plugin/marketplace.json"
SKILL_DIR = "skills/lang/demo"
SKILL_MD = f"{SKILL_DIR}/SKILL.md"
README_ROW = f"| [demo]({SKILL_MD}) |\n"


def plugin_manifest(**overrides):
    manifest = {"name": "tool", "version": "1.0.0", "description": "Does a thing."}
    return {**manifest, "skills": ["./skills/lang/"], **overrides}


def marketplace_entry(**overrides):
    entry = {"name": "tool", "version": "1.0.0", "description": "Does a thing.", "source": "./"}
    return {**entry, **overrides}


def marketplace_manifest(**overrides):
    manifest = {"name": "market", "owner": {}, "description": "Does a thing."}
    return {**manifest, "plugins": [marketplace_entry()], **overrides}


def skill_text(frontmatter="name: demo\ndescription: Use when testing.", body="Body.\n"):
    return f"---\n{frontmatter}\n---\n{body}"


class RepoTestCase(unittest.TestCase):
    """Each test gets its own repo that passes every check, then breaks the part it is about."""

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.write_json(PLUGIN_JSON, plugin_manifest())
        self.write_json(MARKETPLACE_JSON, marketplace_manifest())
        self.write(SKILL_MD, skill_text())
        self.write("README.md", README_ROW)

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content if isinstance(content, bytes) else content.encode())

    def write_json(self, path, data):
        self.write(path, json.dumps(data))

    def run_validate(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = validate.main(self.root)
        return exit_code, output.getvalue().splitlines()

    def assert_single_error(self, expected_start):
        exit_code, lines = self.run_validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith(expected_start), lines[0])

    def assert_passes(self):
        exit_code, lines = self.run_validate()

        self.assertEqual((exit_code, lines), (0, ["ok: 1 skill(s) checked"]))


class ValidRepo(RepoTestCase):
    def test_main_consistent_repo_passes(self):
        self.assert_passes()


class ManifestInput(RepoTestCase):
    def test_main_unusable_manifest_reports_only_that_problem(self):
        cases = {
            "bad JSON": (PLUGIN_JSON, "{", f"{PLUGIN_JSON}: Expecting"),
            "not an object": (PLUGIN_JSON, "[]", f"{PLUGIN_JSON}: must be a JSON object"),
            "not UTF-8": (MARKETPLACE_JSON, b"\xff", f"{MARKETPLACE_JSON}: 'utf-8'"),
        }
        for case, (path, content, expected_error) in cases.items():
            with self.subTest(case):
                self.setUp()
                self.write(path, content)

                self.assert_single_error(expected_error)

    def test_main_missing_manifest_reports_it(self):
        (self.root / MARKETPLACE_JSON).unlink()

        self.assert_single_error(f"{MARKETPLACE_JSON}: ")

    def test_main_wrong_plugins_shape_reports_it(self):
        cases = {"null": None, "string": "tool", "list of strings": ["tool"]}
        for case, plugins in cases.items():
            with self.subTest(case):
                self.write_json(MARKETPLACE_JSON, marketplace_manifest(plugins=plugins))

                self.assert_single_error("marketplace.json: plugins must be a list of objects")

    def test_main_wrong_skills_shape_reports_it(self):
        cases = {"string": "./skills/lang/", "non-string item": [1], "absolute path": [str(Path.cwd())]}
        for case, skills in cases.items():
            with self.subTest(case):
                self.write_json(PLUGIN_JSON, plugin_manifest(skills=skills))

                self.assert_single_error("plugin.json: skills must be a list of relative paths")


class ManifestConsistency(RepoTestCase):
    def test_main_entry_differs_from_plugin_reports_the_key(self):
        cases = {
            "name": "marketplace.json: entry name 'other'",
            "version": "marketplace.json: entry version 'other'",
            "description": "marketplace.json: entry description 'other'",
            "source": "marketplace.json: source 'other' does not exist",
        }
        for key, expected_error in cases.items():
            with self.subTest(key):
                entry = marketplace_entry(**{key: "other"})
                self.write_json(MARKETPLACE_JSON, marketplace_manifest(plugins=[entry]))

                self.assert_single_error(expected_error)

    def test_main_top_description_differs_reports_it(self):
        self.write_json(MARKETPLACE_JSON, marketplace_manifest(description="other"))

        self.assert_single_error("marketplace.json: description 'other'")

    def test_main_no_plugin_entry_reports_it(self):
        self.write_json(MARKETPLACE_JSON, marketplace_manifest(plugins=[]))

        self.assert_single_error("marketplace.json: plugins has no entry for the plugin")

    def test_main_key_missing_from_both_manifests_reports_it(self):
        for key in ("version", "description"):
            with self.subTest(key):
                self.setUp()
                plugin = plugin_manifest()
                entry = marketplace_entry()
                marketplace = marketplace_manifest(plugins=[entry])
                del plugin[key], entry[key]
                if key == "description":
                    del marketplace[key]
                self.write_json(PLUGIN_JSON, plugin)
                self.write_json(MARKETPLACE_JSON, marketplace)

                self.assert_single_error(f"plugin.json: missing {key}")

    def test_main_marketplace_key_missing_reports_it(self):
        for key in ("name", "owner"):
            with self.subTest(key):
                marketplace = marketplace_manifest()
                del marketplace[key]
                self.write_json(MARKETPLACE_JSON, marketplace)

                self.assert_single_error(f"marketplace.json: missing {key}")


class SkillLocation(RepoTestCase):
    def test_main_listed_group_missing_reports_it(self):
        skills = ["./skills/lang/", "./skills/gone/"]
        self.write_json(PLUGIN_JSON, plugin_manifest(skills=skills))

        self.assert_single_error("plugin.json: skills path './skills/gone/' does not exist")

    def test_main_no_skills_found_reports_it(self):
        (self.root / SKILL_MD).unlink()
        self.write("README.md", "")

        self.assert_single_error("no SKILL.md found")

    def test_main_skill_in_unlisted_group_reports_it(self):
        self.write("skills/extra/hidden/SKILL.md", skill_text())

        self.assert_single_error("skills/extra/hidden/SKILL.md: its group is not listed")

    def test_main_workspace_skill_in_unlisted_group_passes(self):
        self.write("skills/extra/demo-workspace/SKILL.md", skill_text())

        self.assert_passes()


class Frontmatter(RepoTestCase):
    def test_main_valid_yaml_passes(self):
        cases = {
            "quoted name": 'name: "demo"\ndescription: Use when testing.',
            "multi-line description": "name: demo\ndescription:\n  Use when\n  testing.",
            "quoted colon": 'name: demo\ndescription: "Use when: testing."',
        }
        for case, frontmatter in cases.items():
            with self.subTest(case):
                self.write(SKILL_MD, skill_text(frontmatter))

                self.assert_passes()

    def test_main_bad_frontmatter_reports_it(self):
        no_description = "description must be a non-empty string"
        cases = {
            "unquoted colon": ("name: demo\ndescription: Use when: testing.", "invalid YAML frontmatter"),
            "impossible date": ("name: demo\ndescription: x\ndate: 2026-13-45", "invalid YAML frontmatter"),
            "list": ("- demo", "frontmatter is not a mapping"),
            "wrong name": ("name: other\ndescription: x", "name 'other' != folder 'demo'"),
            "no description": ("name: demo", no_description),
            "empty description": ("name: demo\ndescription:\nlicense: MIT", no_description),
            "blank string": ('name: demo\ndescription: " "', no_description),
            "empty block": ("name: demo\ndescription: >", no_description),
        }
        for case, (frontmatter, expected_error) in cases.items():
            with self.subTest(case):
                self.write(SKILL_MD, skill_text(frontmatter))

                self.assert_single_error(f"{SKILL_MD}: {expected_error}")

    def test_main_invalid_yaml_reports_the_line_in_the_file(self):
        self.write(SKILL_MD, skill_text("name: demo\ndescription: Use when: testing."))

        _, lines = self.run_validate()

        self.assertIn("line 3,", lines[0])

    def test_main_missing_frontmatter_reports_it(self):
        self.write(SKILL_MD, "Body only.\n")

        self.assert_single_error(f"{SKILL_MD}: missing frontmatter")

    def test_main_non_utf8_skill_reports_it(self):
        self.write(SKILL_MD, b"\xff")

        self.assert_single_error(f"{SKILL_MD}: 'utf-8'")

    @unittest.skipIf(os.geteuid() == 0, "root can read any file")
    def test_main_unreadable_skill_reports_it_once(self):
        (self.root / SKILL_MD).chmod(0)

        self.assert_single_error(f"{SKILL_MD}: [Errno 13]")


class ReferencedFiles(RepoTestCase):
    def test_main_missing_referenced_file_reports_it(self):
        cases = {
            "reference": ("`references/gone.md`", "references/gone.md"),
            "script": ("`scripts/gone.py`", "scripts/gone.py"),
            "template": ("<skill dir>/templates/gone.txt", "templates/gone.txt"),
        }
        for case, (mention, path) in cases.items():
            with self.subTest(case):
                self.write(SKILL_MD, skill_text(body=f"Read {mention}\n"))

                self.assert_single_error(f"{SKILL_MD}: referenced {path} does not exist")

    def test_main_present_referenced_files_pass(self):
        self.write(f"{SKILL_DIR}/references/notes.md", "Notes.\n")
        self.write(f"{SKILL_DIR}/scripts/run.py", "")
        self.write(SKILL_MD, skill_text(body="`references/notes.md` and `scripts/run.py`\n"))

        self.assert_passes()


class PowerpackNames(RepoTestCase):
    def test_main_powerpack_name_in_skill_file_reports_the_line(self):
        for file_name in ("references/notes.md", "scripts/run.py", "templates/ci.yml"):
            with self.subTest(file_name):
                self.setUp()
                self.write(f"{SKILL_DIR}/{file_name}", "first\nuses gh-dev-powerpack\n")

                self.assert_single_error(f"{SKILL_DIR}/{file_name}:2: names gh-dev-powerpack")

    def test_main_powerpack_name_outside_skill_content_passes(self):
        for folder in ("evals", "__pycache__", "node_modules"):
            with self.subTest(folder):
                self.write(f"{SKILL_DIR}/{folder}/input.txt", "gh-dev-powerpack\n")

                self.assert_passes()

    def test_main_binary_skill_file_passes(self):
        self.write(f"{SKILL_DIR}/templates/icon.png", b"\x89PNG\xff\x00")

        self.assert_passes()


class ReadmeTable(RepoTestCase):
    def test_main_skill_not_in_readme_reports_it(self):
        self.write("README.md", "")

        self.assert_single_error(f"README.md: skills table is missing {SKILL_DIR}")

    def test_main_readme_lists_unknown_skill_reports_it(self):
        self.write("README.md", README_ROW + "[gone](skills/lang/gone/SKILL.md)\n")

        self.assert_single_error("README.md: skills table lists skills/lang/gone")

    def test_main_missing_readme_reports_it(self):
        (self.root / "README.md").unlink()

        self.assert_single_error("README.md: ")


if __name__ == "__main__":
    unittest.main()
