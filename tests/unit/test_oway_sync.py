"""Single-source 5-harness installer (`oway sync` / `engine/oway/install_home.py`)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.helpers import REPO

OM = REPO / "om"
SYNC_SH = OM / "sync-om.sh"
OWAY_BIN = REPO / "engine/oway"
ROLES_DIR = REPO / "agents"
ALL_TOOLS = "pi,opencode,claude,codex,antigravity,oway"
ANTIGRAVITY_TOOLS = ("run_command", "read_file", "search_web", "send_message")


def run_oway_sync(home: Path, *args: str, use_flag: bool = True) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.pop("OM_TOOLS", None)
    env.pop("OM_OWAY_SKILLS", None)
    env.pop("OM_OWAY_AGENTS", None)
    cmd = [sys.executable, str(OWAY_BIN), "sync"]
    if use_flag:
        env.pop("OM_HOME", None)
        cmd.extend(["--home", str(home)])
    else:
        env["OM_HOME"] = str(home)
    cmd.extend(args)
    return subprocess.run(cmd, env=env, capture_output=True, text=True)


def split_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n.*?\n---\n?(.*)", text, re.S)
    return m.group(1) if m else text


class SyncCliTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_help_lists_all_six_flags(self):
        r = subprocess.run([sys.executable, str(OWAY_BIN), "sync", "--help"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for flag in ("--tools", "--oway-skills", "--oway-agents", "--dry-run", "--check", "--home"):
            self.assertIn(flag, r.stdout)

    def test_sync_om_sh_delegates_without_duplicated_target_table(self):
        text = SYNC_SH.read_text(encoding="utf-8")
        self.assertRegex(text, r"engine/oway.*sync|install_home\.py")
        for forbidden in ("tool_rows", "opencode_agent", "APPEND_SYSTEM.md", ".config/opencode/agents"):
            self.assertNotIn(forbidden, text)

    def test_exit_codes_for_missing_tools_unknown_tool_and_om_home(self):
        r_missing = run_oway_sync(self.home, "--check")
        self.assertEqual(r_missing.returncode, 2)
        self.assertIn("--tools", r_missing.stderr)

        r_unknown = run_oway_sync(self.home, "--check", "--tools", "nonexistent")
        self.assertEqual(r_unknown.returncode, 1)

        r_env = run_oway_sync(self.home, "--tools", "oway", use_flag=False)
        self.assertEqual(r_env.returncode, 0, r_env.stdout + r_env.stderr)
        self.assertEqual((self.home / ".local/bin/oway").resolve(), (OM / "bin/oway").resolve())


class HarnessInstallTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_dry_run_leaves_home_untouched(self):
        r = run_oway_sync(self.home, "--dry-run", "--tools", ALL_TOOLS)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_five_harnesses_and_oway_binary_symlink_first_then_check_ok(self):
        r = run_oway_sync(self.home, "--tools", ALL_TOOLS)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        expected_links = {
            ".pi/agent/skills/om-plan": OM / "skills/om-plan",
            ".pi/agent/skills/oway-uix": REPO / "skills/oway-uix",
            ".pi/agent/prompts/om-caps.md": OM / "agents/om-caps.md",
            ".pi/agent/APPEND_SYSTEM.md": OM / "rules/AGENTS.md",
            ".config/opencode/skills/om-plan": OM / "skills/om-plan",
            ".config/opencode/AGENTS.md": OM / "rules/AGENTS.md",
            ".claude/skills/om-plan": OM / "skills/om-plan",
            ".agents/skills/om-plan": OM / "skills/om-plan",
            ".codex/agents/om-caps.md": OM / "agents/om-caps.md",
            ".gemini/config/plugins/om": OM,
            ".gemini/config/skills/oway-uix": REPO / "skills/oway-uix",
            ".local/bin/oway": OM / "bin/oway",
        }
        for rel, target in expected_links.items():
            path = self.home / rel
            self.assertTrue(path.is_symlink(), f"{rel} should be a symlink")
            self.assertEqual(path.resolve(), target.resolve(), rel)

        chk = run_oway_sync(self.home, "--check", "--tools", ALL_TOOLS)
        self.assertEqual(chk.returncode, 0, chk.stdout + chk.stderr)


class ThinAdapterTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_opencode_agents_are_thin_generated_files_without_tools(self):
        r = run_oway_sync(self.home, "--tools", "opencode")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for name in ("om-caps.md", "om-review.md", "om-assist.md"):
            dest = self.home / ".config/opencode/agents" / name
            src = OM / "agents" / name
            self.assertTrue(dest.is_file() and not dest.is_symlink(), name)
            text = dest.read_text(encoding="utf-8")
            self.assertIn("description:", text)
            self.assertIn("mode: subagent", text)
            self.assertNotIn("tools:", text)
            self.assertEqual(split_body(dest), split_body(src))

    def test_claude_om_agents_strip_or_translate_antigravity_tools(self):
        r = run_oway_sync(self.home, "--tools", "claude")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for name in ("om-caps.md", "om-review.md", "om-assist.md"):
            dest = self.home / ".claude/agents" / name
            self.assertTrue(dest.is_file() and not dest.is_symlink(), name)
            text = dest.read_text(encoding="utf-8")
            for raw in ANTIGRAVITY_TOOLS:
                self.assertNotIn(raw, text, f"{raw} leaked into {name}")
            self.assertIn("Read", text)
            self.assertIn("Bash", text)
            self.assertIn("WebSearch", text)

    def test_symlinkable_targets_remain_symlinks(self):
        r = run_oway_sync(self.home, "--tools", "pi,codex,claude", "--oway-agents")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.home / ".pi/agent/prompts/om-caps.md").is_symlink())
        self.assertTrue((self.home / ".codex/agents/om-caps.md").is_symlink())
        role_files = [p for p in ROLES_DIR.glob("*/*.md") if p.name not in ("README.md", "TEAM.md")]
        self.assertEqual(len(role_files), 49)
        sample = role_files[0].name
        self.assertTrue((self.home / ".claude/agents" / sample).is_symlink())
        self.assertTrue((self.home / ".codex/agents" / sample).is_symlink())
        self.assertFalse((self.home / ".claude/agents/TEAM.md").exists())


class OwayAgentsSyncTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_without_flag_zero_oway_agents_installed(self):
        r = run_oway_sync(self.home, "--tools", ALL_TOOLS)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(
            {p.name for p in (self.home / ".claude/agents").iterdir()},
            {"om-caps.md", "om-review.md", "om-assist.md"},
        )
        self.assertFalse((self.home / ".gemini/config/agents").exists())

    def test_with_flag_installs_all_49_role_cards_and_all_36_skills(self):
        r = run_oway_sync(self.home, "--tools", ALL_TOOLS, "--oway-skills", "--oway-agents")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        om_names = {"om-caps.md", "om-review.md", "om-assist.md"}
        for rel, includes_om in (
            (".pi/agent/prompts", True),
            (".config/opencode/agents", True),
            (".claude/agents", True),
            (".codex/agents", True),
            (".gemini/config/agents", False),
        ):
            present = {p.name for p in (self.home / rel).iterdir()}
            oway_only = present - om_names if includes_om else present
            self.assertEqual(len(oway_only), 49, f"{rel} has {len(oway_only)} oway agents")
            self.assertNotIn("TEAM.md", present)

        for skill_dir in (".pi/agent/skills", ".config/opencode/skills", ".claude/skills",
                          ".agents/skills", ".gemini/config/skills"):
            installed = {p.name for p in (self.home / skill_dir).iterdir()}
            for expected_skill in ("free-ui-ux-scout", "interview-me", "constraint-driven-development",
                                   "frontend-ui-engineering", "oway-uix", "om-plan"):
                self.assertIn(expected_skill, installed, f"{skill_dir} missing {expected_skill}")

        chk = run_oway_sync(self.home, "--check", "--tools", ALL_TOOLS, "--oway-skills", "--oway-agents")
        self.assertEqual(chk.returncode, 0, chk.stdout + chk.stderr)


class ProtectedUserFilesTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_user_owned_global_rules_are_never_touched_or_backed_up(self):
        protected = [
            ".claude/CLAUDE.md",
            ".codex/AGENTS.md",
            ".gemini/config/AGENTS.md",
            ".gemini/GEMINI.md",
            ".pi/agent/AGENTS.md",
        ]
        sentinels = {}
        for rel in protected:
            p = self.home / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            content = f"USER-OWNED-SENTINEL::{rel}\n"
            p.write_text(content, encoding="utf-8")
            sentinels[rel] = content

        r = run_oway_sync(self.home, "--tools", ALL_TOOLS, "--oway-skills", "--oway-agents")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        for rel, expected in sentinels.items():
            p = self.home / rel
            self.assertTrue(p.is_file() and not p.is_symlink(), rel)
            self.assertEqual(p.read_text(encoding="utf-8"), expected, rel)

        backups = list(self.home.glob(".om-deploy-backups/**/*"))
        for rel in protected:
            flat = rel.replace("/", "__")
            self.assertFalse(any(b.name == flat for b in backups), f"{rel} was backed up")


class DriftDetectionTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        r = run_oway_sync(self.home, "--tools", ALL_TOOLS)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def _assert_drift_then_repair(self):
        chk = run_oway_sync(self.home, "--check", "--tools", ALL_TOOLS)
        self.assertEqual(chk.returncode, 1, chk.stdout + chk.stderr)
        self.assertIn("DRIFT", chk.stdout)
        rep = run_oway_sync(self.home, "--tools", ALL_TOOLS)
        self.assertEqual(rep.returncode, 0, rep.stdout + rep.stderr)
        ok = run_oway_sync(self.home, "--check", "--tools", ALL_TOOLS)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)

    def test_missing_target_drift_and_repair(self):
        (self.home / ".local/bin/oway").unlink()
        self._assert_drift_then_repair()

    def test_wrong_symlink_target_drift_and_repair(self):
        link = self.home / ".pi/agent/APPEND_SYSTEM.md"
        link.unlink()
        wrong = self.home / "wrong.md"
        wrong.write_text("wrong\n", encoding="utf-8")
        link.symlink_to(wrong)
        self._assert_drift_then_repair()

    def test_stale_thin_adapter_drift_and_repair(self):
        for rel in (".config/opencode/agents/om-caps.md", ".claude/agents/om-caps.md"):
            with self.subTest(adapter=rel):
                (self.home / rel).write_text("stale content\n", encoding="utf-8")
                self._assert_drift_then_repair()

    def test_retired_stale_paths_drift_and_repair(self):
        builtin = self.home / ".pi/agent/skills/om-uix"
        builtin.mkdir(parents=True)
        self._assert_drift_then_repair()
        self.assertFalse(builtin.exists())

        conf = self.home / ".config/om"
        conf.mkdir(parents=True, exist_ok=True)
        custom = self.home / ".legacy/stale-item"
        custom.mkdir(parents=True)
        (conf / "retire").write_text("~/.legacy/stale-item\n", encoding="utf-8")
        self._assert_drift_then_repair()
        self.assertFalse(custom.exists())


if __name__ == "__main__":
    unittest.main()
