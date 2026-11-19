"""Oway tool: headers, index, doctor, ledger, keeper, setup."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import TempDir, run_script

from oway import doctor, headers, index, keeper, ledger, setup  # noqa: E402
from oway.project import OwayError

SPINE = "---\nname: 01-intent\ndescription: Why\ntype: spine\nstate: draft\napproved: no\n---\n\n# Intent\n"


def make_project(root: Path, builders=("DevBackend",)) -> Path:
    setup.project_setup(root, "fr", list(builders), uix=True, platform=root / "no-platform")
    return root / "_oway"


class HeaderTests(unittest.TestCase):
    def test_types_match_rules_doc(self):
        rules = (Path(__file__).resolve().parents[2] / "docs/oway/rules.md").read_text(encoding="utf-8")
        for kind, states in headers.TYPES.items():
            self.assertIn(f"| {kind} |", rules)
            self.assertIn(", ".join(states), rules)

    def test_bad_type_and_state(self):
        self.assertIn("no header", headers.problems(None))
        self.assertTrue(any("unknown type" in p for p in headers.problems(
            {"name": "a", "description": "b", "type": "notes", "state": "draft"})))
        self.assertTrue(any("not allowed" in p for p in headers.problems(
            {"name": "a", "description": "b", "type": "spine", "state": "Proposed"})))

    def test_set_fields_keeps_other_lines(self):
        out = headers.set_fields(SPINE, {"state": "approved", "frozen_hash": "abc"})
        self.assertIn("state: approved", out)
        self.assertIn("frozen_hash: abc", out)
        self.assertIn("# Intent", out)


class SetupAndDoctorTests(unittest.TestCase):
    def test_setup_then_doctor_is_clean(self):
        with TempDir() as root:
            oway = make_project(root)
            cfg = json.loads((oway / "config.json").read_text())
            self.assertEqual(cfg["language"], "fr")
            self.assertIn("owner profile (OwayHelpers interview)", cfg["setup_pending"])
            self.assertEqual(doctor.run(root), [])

    def test_setup_refuses_existing_project(self):
        with TempDir() as root:
            make_project(root)
            with self.assertRaises(OwayError):
                make_project(root)

    def test_doctor_finds_real_problems(self):
        with TempDir() as root:
            oway = make_project(root)
            (oway / "spines").mkdir()
            (oway / "spines" / "01-intent.md").write_text(
                SPINE.replace("state: draft", "state: Proposed") + "[x](../missing.md) /home/user/x\n")
            (oway / "milestones").mkdir()
            for n in (1, 2):
                (oway / "milestones" / f"m{n}.md").write_text(
                    f"---\nname: m{n}\ndescription: d\ntype: milestone\nstate: draft\ncurrent: true\n---\n")
            out = "\n".join(doctor.run(root))
            self.assertIn("state 'Proposed'", out)
            self.assertIn("broken link", out)
            self.assertIn("personal machine path", out)
            self.assertIn("more than one milestone has current: true", out)
            self.assertIn("out of date, run `oway index`", out)

    def test_config_checks(self):
        with TempDir() as root:
            oway = make_project(root, builders=("DevTester",))
            out = "\n".join(doctor.run(root))
            self.assertIn("unknown Dev builder 'DevTester'", out)
            cfg = json.loads((oway / "config.json").read_text())
            cfg["language"] = "french"
            cfg["message_max_chars"] = 500
            (oway / "config.json").write_text(json.dumps(cfg))
            out = "\n".join(doctor.run(root))
            self.assertIn("two-letter code", out)
            self.assertIn("0 to 200", out)


class IndexTests(unittest.TestCase):
    def test_index_lists_headers_and_is_stable(self):
        with TempDir() as root:
            oway = make_project(root)
            (oway / "spines").mkdir()
            (oway / "spines" / "01-intent.md").write_text(SPINE)
            index.build(oway)
            text = (oway / "spines" / "INDEX.md").read_text()
            self.assertIn("| [01-intent.md](01-intent.md) | spine | draft | no | Why |", text)
            self.assertIn("[spines/](spines/INDEX.md)", (oway / "INDEX.md").read_text())
            self.assertEqual(index.build(oway, check=True), [])

    def test_index_leaves_keeper_index_alone(self):
        with TempDir() as root:
            oway = make_project(root)
            keeper.wake(oway, "dev")
            keeper.note(oway, "dev", "LOOP", "same review 4 times", "ledger L-1")
            before = (oway / "keeper" / "INDEX.md").read_text()
            index.build(oway)
            self.assertEqual((oway / "keeper" / "INDEX.md").read_text(), before)
            self.assertEqual(doctor.run(root), [])

    def test_cli_check_exit_code(self):
        with TempDir() as root:
            oway = make_project(root)
            (oway / "research").mkdir()
            (oway / "research" / "RES-001.md").write_text(SPINE.replace("type: spine", "type: research"))
            r = run_script("oway", "--root", str(root), "index", "--check")
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertEqual(run_script("oway", "--root", str(root), "index").returncode, 0)
            self.assertEqual(run_script("oway", "--root", str(root), "index", "--check").returncode, 0)


class LedgerTests(unittest.TestCase):
    def test_ids_count_up(self):
        with TempDir() as root:
            oway = root / "_oway"
            a, b = ledger.append(oway, "one"), ledger.append(oway, "two")
            self.assertEqual(int(b[-3:]), int(a[-3:]) + 1)
            self.assertTrue((oway / "LEDGER.md").read_text().startswith("# Ledger"))


class KeeperTests(unittest.TestCase):
    def test_asleep_keeper_cannot_note(self):
        with TempDir() as root:
            oway = make_project(root)
            with self.assertRaises(OwayError):
                keeper.note(oway, "qa", "DRIFT", "fact", "proof")

    def test_dedupe_and_resolve(self):
        with TempDir() as root:
            oway = make_project(root)
            keeper.wake(oway, "dev")
            fid, new = keeper.note(oway, "dev", "loop", "trigger review v5", "ledger L-20261114-004")
            self.assertTrue(new)
            again, new2 = keeper.note(oway, "dev", "LOOP", "trigger  review v5", "other proof")
            self.assertEqual((again, new2), (fid, False))
            keeper.resolve(oway, fid, "lead stopped the review")
            _, new3 = keeper.note(oway, "dev", "LOOP", "trigger review v5", "again")
            self.assertTrue(new3)
            self.assertIn("| resolved |", (oway / "keeper" / "INDEX.md").read_text())

    def test_owner_message_is_short_and_has_no_paths(self):
        f = {"type": "DRIFT", "fact": "main goal paused for 4 days " + "x" * 300,
             "proof": "see _oway/slices/s012.md line 4"}
        msg = keeper.owner_message(f)
        self.assertLessEqual(len(msg), 200)
        self.assertNotIn("_oway/", msg)

    def test_sleep_and_report(self):
        with TempDir() as root:
            oway = make_project(root)
            keeper.wake(oway, "qa")
            keeper.note(oway, "qa", "PACE", "3 slices in review", "oway check")
            keeper.sleep(oway, "qa")
            self.assertEqual(keeper.awake(oway), {})
            report = keeper.report(oway).read_text()
            self.assertIn("Open findings: 1", report)


class PlatformTests(unittest.TestCase):
    def test_platform_init_never_overwrites(self):
        with TempDir() as root:
            made = setup.platform_init(root / "p")
            self.assertEqual(sorted(made), ["platform.json", "profile.md"])
            (root / "p" / "profile.md").write_text("mine")
            self.assertEqual(setup.platform_init(root / "p"), [])
            self.assertEqual((root / "p" / "profile.md").read_text(), "mine")

    def test_approved_profile_removes_pending_item(self):
        with TempDir() as root:
            setup.platform_init(root / "p")
            prof = root / "p" / "profile.md"
            prof.write_text(prof.read_text().replace("state: draft", "state: approved"))
            setup.project_setup(root / "proj", "en", [], True, platform=root / "p")
            cfg = json.loads((root / "proj" / "_oway" / "config.json").read_text())
            self.assertNotIn("owner profile (OwayHelpers interview)", cfg["setup_pending"])

    def test_claude_hook_install_keeps_settings(self):
        with TempDir() as root:
            (root / ".claude").mkdir()
            (root / ".claude" / "settings.json").write_text(json.dumps({"model": "x"}))
            setup.project_setup(root, "en", [], True, platform=root / "p", claude_hook=True)
            setup.install_claude_stop_hook(root)
            data = json.loads((root / ".claude" / "settings.json").read_text())
            self.assertEqual(data["model"], "x")
            self.assertEqual(len(data["hooks"]["Stop"]), 1)
            self.assertIn("stop-hook", data["hooks"]["Stop"][0]["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()


class ContentRuleTests(unittest.TestCase):
    RES = "---\nname: r\ndescription: d\ntype: research\nstate: draft\n---\n\n# Market\n"

    def test_research_needs_real_sources(self):
        with TempDir() as root:
            oway = make_project(root)
            (oway / "research").mkdir()
            f = oway / "research" / "RES-001.md"
            f.write_text(self.RES + "Rents from avito.ma.\n")
            index.build(oway)
            out = "\n".join(doctor.run(root))
            self.assertIn("no Sources section", out)
            self.assertIn("bare source 'avito.ma'", out)
            f.write_text(self.RES + "\n## Sources\n- [Avito rents](https://www.avito.ma/fr/casablanca)\n")
            index.build(oway)
            self.assertEqual(doctor.run(root), [])

    def test_done_slice_needs_walkthrough(self):
        with TempDir() as root:
            oway = make_project(root)
            (oway / "slices").mkdir()
            f = oway / "slices" / "s001.md"
            f.write_text("---\nname: s001\ndescription: d\ntype: slice\nstate: done\n---\n\n# S001\n")
            index.build(oway)
            self.assertIn("needs its walkthrough", "\n".join(doctor.run(root)))
            f.write_text(f.read_text() + "\n## Walkthrough\nWhat happened.\n")
            index.build(oway)
            self.assertEqual(doctor.run(root), [])


class GitHeaderTests(unittest.TestCase):
    def test_dates_come_from_git(self):
        import subprocess
        from oway import githeaders
        with TempDir() as root:
            oway = make_project(root)
            self.assertIn("_oway/project.md", githeaders.run(root, check=True))
            githeaders.run(root)
            self.assertIn("created: not committed", (oway / "project.md").read_text())
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=Tester", "-c", "commit.gpgsign=false",
                            "commit", "-qm", "x"], cwd=root, check=True)
            githeaders.run(root)
            text = (oway / "project.md").read_text()
            self.assertRegex(text, r"created: \d{4}-\d{2}-\d{2}\n")
            self.assertRegex(text, r"updated: \d{4}-\d{2}-\d{2} by Tester\n")
            self.assertEqual(githeaders.run(root, check=True), [])
