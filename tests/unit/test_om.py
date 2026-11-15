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


TOOLS = "pi,opencode,antigravity"


def sync(home, *args):
    env = dict(os.environ, OM_HOME=str(home))
    env.pop("OM_TOOLS", None)
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

    def test_no_personal_names_in_om_or_root_docs(self):
        bad = re.compile(r"(?<!mr)ojefe|vmi3298109|_CG-Gov|CortexGate|MEOCE|aiwork|/home/[a-z]+/", re.I)
        files = [f for f in OM.rglob("*") if f.is_file() and "catalog" not in f.parts]
        paths = re.compile(r"/home/[a-z]+/|_CG-Gov|vmi3298109")
        text = (OM.parent / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIsNone(paths.search(text), "AGENTS.md has a workstation path")
        for f in files:
            self.assertIsNone(bad.search(f.read_text(encoding="utf-8", errors="ignore")), f)

    def test_no_old_cgm_names(self):
        allowed = set()
        for f in OM.rglob("*"):
            if f.is_file() and f.name not in allowed and "catalog" not in f.parts:
                self.assertNotIn("cgm", f.read_text(encoding="utf-8", errors="ignore").lower(), f)


class UixTests(unittest.TestCase):
    def test_catalog_is_pinned_to_full_commits(self):
        text = (OM / "skills/om-uix/scripts/fetch_catalog.sh").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"_SHA=[0-9a-f]{40}\n", text)), 2)

    def test_both_mit_licences_are_kept(self):
        for name in ("awesome-design-skills", "hallmark"):
            text = (OM / f"skills/om-uix/licenses/LICENSE-{name}-MIT.txt").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("MIT License"))

    def test_style_hub_says_how_to_get_the_catalog(self):
        import shutil
        tmp = Path(tempfile.mkdtemp())
        shutil.copytree(OM / "skills/om-uix/scripts", tmp / "scripts")
        r = subprocess.run(["python3", str(tmp / "scripts/style_hub.py"), "list"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fetch_catalog.sh", r.stderr)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def test_no_tools_chosen_is_a_usage_error(self):
        r = sync(self.home, "--check")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--tools", r.stderr)

    def test_unknown_tool_fails(self):
        self.assertEqual(sync(self.home, "--check", "--tools", "nope").returncode, 1)

    def test_check_reports_drift_on_an_empty_home(self):
        r = sync(self.home, "--check", "--tools", TOOLS)
        self.assertEqual(r.returncode, 1)
        self.assertIn("DRIFT", r.stdout)

    def test_dry_run_changes_nothing(self):
        sync(self.home, "--dry-run", "--tools", TOOLS)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_apply_then_check_is_ok(self):
        r = sync(self.home, "--tools", TOOLS)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        link = self.home / ".pi/agent/APPEND_SYSTEM.md"
        self.assertEqual(link.resolve(), (OM / "rules/AGENTS.md").resolve())
        plugin = self.home / ".gemini/config/plugins/om"
        self.assertEqual(plugin.resolve(), OM.resolve())
        self.assertEqual(sync(self.home, "--check", "--tools", TOOLS).returncode, 0)

    def test_only_the_chosen_tools_are_touched(self):
        sync(self.home, "--tools", "pi")
        self.assertTrue((self.home / ".pi").exists())
        self.assertFalse((self.home / ".config/opencode").exists())

    def test_tools_file_replaces_the_flag(self):
        conf = self.home / ".config/om"
        conf.mkdir(parents=True)
        (conf / "tools").write_text("pi\n", encoding="utf-8")
        self.assertEqual(sync(self.home).returncode, 0)
        self.assertTrue((self.home / ".pi/agent/skills/om-plan").is_symlink())

    def test_retire_file_backs_up_old_paths_and_extra_adds_targets(self):
        conf = self.home / ".config/om"
        conf.mkdir(parents=True)
        old = self.home / ".mytool/old-skill"
        old.mkdir(parents=True)
        (conf / "retire").write_text("# old\n~/.mytool/old-skill\n", encoding="utf-8")
        (conf / "extra").write_text("symlink $HOME/.mytool/om-plan skills/om-plan\n", encoding="utf-8")
        r = sync(self.home, "--tools", "pi")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(old.exists())
        self.assertTrue(list(self.home.glob(".om-deploy-backups/*/.mytool__old-skill")))
        self.assertEqual((self.home / ".mytool/om-plan").resolve(), (OM / "skills/om-plan").resolve())
        self.assertEqual(sync(self.home, "--check", "--tools", "pi").returncode, 0)

    def test_opencode_agent_copy_drops_the_tools_list(self):
        sync(self.home, "--tools", "opencode")
        text = (self.home / ".config/opencode/agents/om-caps.md").read_text(encoding="utf-8")
        self.assertIn("mode: subagent", text)
        self.assertNotIn("tools:", text)


if __name__ == "__main__":
    unittest.main()
