"""Oway behaviour, end to end through the CLI: a builder cannot fake or skip proof.

Each test plays one scene from docs/oway/proof-loop.md, "Why the agent cannot cheat".
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from tests.helpers import TempDir, run_script

MATRIX = """---
name: s001-matrix
description: Proof matrix of s001
type: matrix
parent: s001-hello
state: draft
approved: yes
owner: LeadQATester
verifiers: qa/verify_hello.sh
---

# S001 proof matrix

| id | Interaction | Accepted proof | Medium | Verifier commands | Canary | State |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Run the app and read the greeting | Output has the canary word | command record | `sh qa/verify_hello.sh` | {canary} | OPEN |
| P2 | The app has a version | Output has a version | command record | `python3 app.py --version` | none | OPEN |
"""

VERIFIER = "#!/bin/sh\npython3 app.py\n"


def oway(root: Path, *args: str, stdin: str | None = None):
    return run_script("oway", "--root", str(root), *args, stdin=stdin)


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false",
                    *args], cwd=root, check=True, capture_output=True)


class Scene:
    def __init__(self, root: Path, canary: str = "kiwi-7731"):
        self.root = root
        self.canary = canary
        r = oway(root, "setup", "--language", "en", "--builder", "DevBackend",
                 "--platform", str(root / "no-platform"))
        assert r.returncode == 0, r.stderr
        (root / "qa").mkdir()
        (root / "qa" / "verify_hello.sh").write_text(VERIFIER)
        (root / "_oway" / "slices").mkdir()
        (root / "_oway" / "slices" / "s001.matrix.md").write_text(MATRIX.format(canary=canary))
        (root / "_oway" / "state").mkdir()
        (root / "_oway" / "state" / "checkpoint.json").write_text(
            json.dumps({"slice": "s001", "role": "DevBackend"}))
        self.app("print('hello')\n")
        git(root, "init", "-q")
        git(root, "add", "-A")
        git(root, "commit", "-qm", "start")
        assert oway(root, "freeze", "s001").returncode == 0

    def app(self, text: str) -> None:
        (self.root / "app.py").write_text(
            "import sys\nif '--version' in sys.argv:\n    print('1.0.0')\n    raise SystemExit\n" + text)

    def stop(self) -> dict | None:
        r = oway(self.root, "stop-hook", stdin=json.dumps({"stop_hook_active": False}))
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout) if r.stdout.strip() else None


class ProofLoopBehaviour(unittest.TestCase):
    def test_worker_cannot_stop_until_every_item_passes(self):
        with TempDir() as root:
            s = Scene(root)
            block = s.stop()
            self.assertEqual(block["decision"], "block")
            self.assertIn("P1 is OPEN", block["reason"])

            r = oway(root, "submit", "s001", "P1")
            self.assertEqual(r.returncode, 1)
            self.assertIn("canary 'kiwi-7731' not in the output", r.stdout)
            self.assertIn("P1 is FAIL", s.stop()["reason"])

            s.app(f"print('hello {s.canary}')\n")
            self.assertEqual(oway(root, "submit", "s001", "P1").returncode, 0)
            self.assertEqual(oway(root, "submit", "s001", "P2").returncode, 0)
            self.assertIsNone(s.stop())
            r = oway(root, "check", "s001")
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_saying_done_in_the_matrix_changes_nothing(self):
        with TempDir() as root:
            s = Scene(root)
            m = root / "_oway/slices/s001.matrix.md"
            m.write_text(m.read_text().replace("| OPEN |", "| PASS |"))
            r = oway(root, "check", "s001")
            self.assertEqual(r.returncode, 1)
            self.assertIn("P1 OPEN", r.stdout)
            self.assertEqual(s.stop()["decision"], "block")

    def test_editing_the_matrix_or_the_verifier_is_tamper(self):
        with TempDir() as root:
            s = Scene(root)
            m = root / "_oway/slices/s001.matrix.md"
            m.write_text(m.read_text().replace("`sh qa/verify_hello.sh`", "`true`"))
            r = oway(root, "submit", "s001", "P1")
            self.assertEqual(r.returncode, 3)
            self.assertIn("TAMPER", r.stderr)
            self.assertIn("TAMPER", s.stop()["reason"])

        with TempDir() as root:
            Scene(root)
            (root / "qa/verify_hello.sh").write_text("#!/bin/sh\necho kiwi-7731\n")
            self.assertEqual(oway(root, "submit", "s001", "P1").returncode, 3)

    def test_editing_the_evidence_is_tamper(self):
        with TempDir() as root:
            s = Scene(root)
            oway(root, "submit", "s001", "P1")
            ev = root / "_oway/evidence/s001.jsonl"
            ev.write_text(ev.read_text().replace('"verdict": "FAIL"', '"verdict": "PASS"'))
            r = oway(root, "check", "s001")
            self.assertEqual(r.returncode, 3)
            self.assertIn("evidence chain", r.stderr)
            oway(root, "keeper", "wake", "dev")
            r = oway(root, "keeper", "scan")
            self.assertIn("new", r.stdout)
            self.assertIn("TAMPER", (root / "_oway/keeper/INDEX.md").read_text())

    def test_mocked_proof_is_fake(self):
        with TempDir() as root:
            s = Scene(root)
            s.app(f"print('hello {s.canary} from /?mock=1')\n")
            r = oway(root, "submit", "s001", "P1")
            self.assertIn("FAKE", r.stdout)
            self.assertEqual(oway(root, "check", "s001").returncode, 1)

    def test_three_failed_rounds_block_and_the_keeper_sees_a_loop(self):
        with TempDir() as root:
            s = Scene(root)
            oway(root, "keeper", "wake", "dev")
            for _ in range(3):
                oway(root, "submit", "s001", "P1")
            r = oway(root, "submit", "s001", "P1")
            self.assertEqual(r.returncode, 2)
            self.assertIn("BLOCKED", r.stderr)
            self.assertIn("BLOCKED", (root / "_oway/LEDGER.md").read_text())
            first = oway(root, "keeper", "scan").stdout
            second = oway(root, "keeper", "scan").stdout
            self.assertIn("new", first)
            self.assertIn("known", second)  # alert once, not every scan
            # P2 is still OPEN, so the hook still blocks the worker
            self.assertIn("P2 is OPEN", s.stop()["reason"])

    def test_a_lead_is_never_blocked(self):
        with TempDir() as root:
            Scene(root)
            cp = root / "_oway/state/checkpoint.json"
            cp.write_text(json.dumps({"slice": "s001", "role": "LeadDev"}))
            r = oway(root, "stop-hook", stdin="{}")
            self.assertEqual(r.stdout.strip(), "")

    def test_stuck_worker_is_let_go_after_idle_blocks_and_it_is_logged(self):
        with TempDir() as root:
            s = Scene(root)
            for _ in range(5):
                self.assertIsNotNone(s.stop())
            self.assertIsNone(s.stop())
            self.assertIn("stop allowed after 5 blocks", (root / "_oway/LEDGER.md").read_text())

    def test_old_pass_is_stale_at_a_new_commit(self):
        with TempDir() as root:
            s = Scene(root)
            s.app(f"print('hello {s.canary}')\n")
            oway(root, "submit", "s001", "P1")
            oway(root, "submit", "s001", "P2")
            git(root, "commit", "-qam", "change")
            r = oway(root, "check", "s001", "--head")
            self.assertEqual(r.returncode, 1)
            self.assertIn("STALE", r.stdout)

    def test_plain_format_for_other_hosts(self):
        with TempDir() as root:
            Scene(root)
            r = oway(root, "stop-hook", "--format", "plain", stdin="")
            self.assertEqual(r.returncode, 2)
            self.assertIn("P1 is OPEN", r.stderr)

    def test_project_stays_doctor_clean_through_the_loop(self):
        with TempDir() as root:
            s = Scene(root)
            s.app(f"print('hello {s.canary}')\n")
            oway(root, "submit", "s001", "P1")
            self.assertEqual(oway(root, "index").returncode, 0)
            r = oway(root, "doctor")
            self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
