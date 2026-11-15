"""om (Oway medium): file shape and sync-om.sh behaviour."""
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

OM = Path(__file__).resolve().parents[2] / "om"
SYNC = OM / "sync-om.sh"


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


def rows():
    text = (OM / "DEPLOYMENTS.md").read_text(encoding="utf-8")
    block = re.search(r"```om-targets\n(.*?)```", text, re.S).group(1)
    return [l.split() for l in block.splitlines() if l.strip() and not l.startswith("#")]


def sync(home, *args, host="vmi3298109"):
    env = dict(os.environ, OM_HOST=host, OM_HOME=str(home))
    return subprocess.run(["bash", str(SYNC), *args], env=env,
                          capture_output=True, text=True)


class ShapeTests(unittest.TestCase):
    def test_rules_stay_short(self):
        lines = (OM / "rules/AGENTS.md").read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 45)

    def test_rules_name_the_three_sizes_and_the_ask_first_list(self):
        text = (OM / "rules/AGENTS.md").read_text(encoding="utf-8")
        for word in ("**Quick**", "**Task**", "**Mission**", "Always ask first"):
            self.assertIn(word, text)

    def test_skills_and_agents_have_name_and_description(self):
        files = list(OM.glob("skills/*/SKILL.md")) + list(OM.glob("agents/*.md"))
        self.assertGreaterEqual(len(files), 6)
        for f in files:
            fm = frontmatter(f)
            name = re.search(r"^name: (\S+)", fm, re.M)
            self.assertIsNotNone(name, f)
            self.assertTrue(name.group(1).startswith("om-"), f)
            self.assertRegex(fm, r"(?m)^description:", f)

    def test_every_target_source_exists(self):
        for host, tool, method, target, source in rows():
            if method == "retire":
                self.assertIn("cgm", target)
                continue
            self.assertTrue((OM / source).exists(), source)

    def test_no_cgm_names_left_outside_the_migration_notes(self):
        allowed = {"README.md", "DEPLOYMENTS.md", "sync-om.sh"}
        for f in OM.rglob("*"):
            if f.is_file() and f.name not in allowed and "catalog" not in f.parts:
                self.assertNotIn("cgm", f.read_text(encoding="utf-8", errors="ignore").lower(), f)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def test_check_reports_drift_on_an_empty_home(self):
        r = sync(self.home, "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("DRIFT", r.stdout)

    def test_dry_run_changes_nothing(self):
        sync(self.home, "--dry-run")
        self.assertEqual(list(self.home.iterdir()), [])

    def test_apply_then_check_is_ok_and_old_links_are_backed_up(self):
        old = self.home / ".pi/agent/skills/cgm-plan"
        old.mkdir(parents=True)
        r = sync(self.home)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(old.exists())
        self.assertTrue(list(self.home.glob(".om-deploy-backups/*/.pi__agent__skills__cgm-plan")))
        link = self.home / ".pi/agent/APPEND_SYSTEM.md"
        self.assertEqual(link.resolve(), (OM / "rules/AGENTS.md").resolve())
        self.assertEqual(sync(self.home, "--check").returncode, 0)

    def test_opencode_agent_copy_drops_the_tools_list(self):
        sync(self.home)
        text = (self.home / ".config/opencode/agents/om-caps.md").read_text(encoding="utf-8")
        self.assertIn("mode: subagent", text)
        self.assertNotIn("tools:", text)

    def test_unknown_host_fails(self):
        self.assertEqual(sync(self.home, "--check", host="nowhere").returncode, 1)


if __name__ == "__main__":
    unittest.main()
