"""Oway upgrade (change lists applied in order) and feedback (scrubbed, never sent)."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from tests.helpers import TempDir, run_script

from oway import doctor, feedback, setup, upgrade  # noqa: E402
from oway.project import OwayError


def project(root: Path, version: str) -> Path:
    setup.project_setup(root, "en", [], True, platform=root / "no-platform")
    cfg_path = root / "_oway" / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["oway_version"] = version
    cfg_path.write_text(json.dumps(cfg))
    return root / "_oway"


class UpgradeTests(unittest.TestCase):
    def test_change_lists_apply_in_order_with_git_mv(self):
        with TempDir() as root:
            oway = project(root / "p", "0.1.0")
            (oway / "prototypes").mkdir()
            (oway / "prototypes" / "README.md").write_text(
                "---\nname: d\ndescription: d\ntype: design\nstate: draft\n---\n")
            subprocess.run(["git", "init", "-q"], cwd=root / "p", check=True)
            subprocess.run(["git", "add", "-A"], cwd=root / "p", check=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false",
                            "commit", "-qm", "start"], cwd=root / "p", check=True)
            steps = root / "steps"
            steps.mkdir()
            (steps / "a.json").write_text(json.dumps(
                {"from": "0.1.0", "to": "0.2.0", "moves": [["_oway/prototypes", "_oway/design"]], "notes": "rename"}))
            (steps / "b.json").write_text(json.dumps({"from": "0.2.0", "to": "0.3.0", "moves": []}))
            with mock.patch.dict(os.environ, {"OWAY_UPGRADES": str(steps)}):
                dry = upgrade.run(root / "p", "0.3.0", dry_run=True)
                self.assertTrue((oway / "prototypes").exists())
                self.assertIn("  move _oway/prototypes -> _oway/design", dry)
                upgrade.run(root / "p", "0.3.0")
            self.assertTrue((oway / "design" / "README.md").exists())
            self.assertEqual(json.loads((oway / "config.json").read_text())["oway_version"], "0.3.0")
            self.assertIn("Oway upgrade 0.1.0 -> 0.3.0", (oway / "LEDGER.md").read_text())
            status = subprocess.run(["git", "status", "--short"], cwd=root / "p", capture_output=True, text=True).stdout
            self.assertIn("R  _oway/prototypes/README.md -> _oway/design/README.md", status)
            self.assertEqual(doctor.run(root / "p"), [])

    def test_project_newer_than_tool_is_refused(self):
        with TempDir() as root:
            project(root, "9.0.0")
            with self.assertRaises(OwayError):
                upgrade.run(root, "0.3.5")

    def test_cli_upgrade_without_change_list_only_bumps_version(self):
        with TempDir() as root:
            oway = project(root, "0.0.1")
            r = run_script("oway", "--root", str(root), "upgrade")
            self.assertEqual(r.returncode, 0, r.stderr)
            tool = (Path(__file__).resolve().parents[2] / "engine/VERSION").read_text().strip()
            self.assertEqual(json.loads((oway / "config.json").read_text())["oway_version"], tool)


class FeedbackTests(unittest.TestCase):
    def test_scrub_removes_secrets_emails_and_paths(self):
        out = feedback.scrub("key ghp_abcdefghijklmnop mail a.b@example.com at /home/user/Desktop/x.md")
        self.assertNotIn("ghp_", out)
        self.assertNotIn("example.com", out)
        self.assertNotIn("/home/", out)

    def test_feedback_is_saved_not_sent(self):
        with TempDir() as root:
            oway = project(root, "0.3.5")
            with mock.patch.dict(os.environ, {"OWAY_PLATFORM": str(root / "none")}):
                path, url, cmd = feedback.create(oway, "Takeover has no recipe",
                                                 "Seen in /home/user/example-project")
            self.assertTrue(path.exists())
            self.assertNotIn("/home/", path.read_text())
            self.assertTrue(url.startswith("https://github.com/mrojefe/Oway/issues/new?"))
            self.assertIn("gh issue create", cmd)
            self.assertEqual(doctor.run(root), ["_oway/INDEX.md: out of date, run `oway index`",
                                                "_oway/feedback/INDEX.md: out of date, run `oway index`"])


if __name__ == "__main__":
    unittest.main()
