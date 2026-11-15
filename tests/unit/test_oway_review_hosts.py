"""Reviewer step for visual proof, and the pi stop-hook extension."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from tests.helpers import TempDir, run_script
from tests.unit.test_oway_behaviour import Scene, oway

from oway import review, setup  # noqa: E402


def visual(root: Path, reviewer: str | None) -> Scene:
    s = Scene(root)
    m = root / "_oway/slices/s001.matrix.md"
    # a new matrix: P1 is now visual, so it needs the reviewer; frozen again
    text = m.read_text().replace("| command record | `sh qa/verify_hello.sh`", "| screenshot + live output | `sh qa/verify_hello.sh`", 1)
    text = text.replace("state: frozen", "state: draft")
    m.write_text("\n".join(l for l in text.splitlines() if not l.startswith("frozen_hash:")) + "\n")
    assert oway(root, "freeze", "s001").returncode == 0
    if reviewer is not None:
        script = root / "qa" / "reviewer.py"
        script.write_text(reviewer)
        cfg_path = root / "_oway/config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["reviewer_command"] = f"{sys.executable} {script}"
        cfg_path.write_text(json.dumps(cfg))
    s.app(f"print('hello {s.canary}')\n")
    return s


ANSWER = 'import sys; sys.stdin.read(); print({!r})\n'


class ReviewTests(unittest.TestCase):
    def test_verifier_pass_on_visual_proof_waits_for_the_reviewer(self):
        with TempDir() as root:
            visual(root, None)
            oway(root, "submit", "s001", "P1")
            oway(root, "submit", "s001", "P2")
            r = oway(root, "check", "s001")
            self.assertEqual(r.returncode, 1)
            self.assertIn("P1 NEEDS_REVIEW", r.stdout)
            self.assertIn("no reviewer_command", oway(root, "review", "s001", "P1").stderr)

    def test_reviewer_pass_makes_the_item_pass(self):
        with TempDir() as root:
            visual(root, ANSWER.format('{"verdict":"PASS","reason":"shows the greeting","evidence_ids":[1]}'))
            oway(root, "submit", "s001", "P1")
            oway(root, "submit", "s001", "P2")
            self.assertEqual(oway(root, "review", "s001", "P1").returncode, 0)
            self.assertEqual(oway(root, "check", "s001").returncode, 0)

    def test_bad_format_is_unreviewed_and_fake_is_a_failed_round(self):
        with TempDir() as root:
            visual(root, ANSWER.format("Looks good to me, PASS"))
            oway(root, "submit", "s001", "P1")
            r = oway(root, "review", "s001", "P1")
            self.assertIn("UNREVIEWED", r.stdout)
            self.assertIn("P1 NEEDS_REVIEW", oway(root, "check", "s001").stdout)
        with TempDir() as root:
            visual(root, ANSWER.format('{"verdict":"FAKE","reason":"staged page","evidence_ids":[1]}'))
            oway(root, "submit", "s001", "P1")
            oway(root, "review", "s001", "P1")
            out = oway(root, "check", "s001").stdout
            self.assertIn("P1 FAKE rounds=1", out)

    def test_parse_accepts_only_the_fixed_format(self):
        self.assertIsNone(review.parse('{"verdict":"OK","reason":"x","evidence_ids":[]}'))
        self.assertIsNone(review.parse('{"verdict":"PASS"}'))
        self.assertIsNone(review.parse('a {"verdict":"PASS","reason":"x","evidence_ids":[]} b {"x":1}'))
        self.assertEqual(review.parse('{"verdict":"PASS","reason":"x","evidence_ids":[1]}')["verdict"], "PASS")


class PiExtensionTests(unittest.TestCase):
    def test_install_writes_extension_with_tool_path(self):
        with TempDir() as root:
            self.assertEqual(setup.install_pi_extension(root), ".pi/extensions/oway-stop.ts")
            text = (root / ".pi/extensions/oway-stop.ts").read_text()
            self.assertNotIn("__OWAY_ENTRY__", text)
            self.assertIn("engine/oway", text)
            self.assertIn('pi.on("agent_before_settle"', text)
            self.assertIn('"stop-hook", "--format", "plain"', text)

    def test_cli(self):
        with TempDir() as root:
            (root / "_oway").mkdir()
            r = run_script("oway", "--root", str(root), "install-hook", "--host", "pi")
            self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
