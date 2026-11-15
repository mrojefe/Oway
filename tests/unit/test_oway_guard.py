"""Builder write zones: the pre-tool guard and the Git backstop at submit."""

from __future__ import annotations

import json
import unittest

from tests.helpers import TempDir
from tests.unit.test_oway_behaviour import Scene, oway


def zone(root, role="DevBackend", paths=("src/**",)):
    (root / "_oway/state/checkpoint.json").write_text(
        json.dumps({"slice": "s001", "role": role, "zone": list(paths)}))


def write(root, path):
    return oway(root, "guard", stdin=json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(root / path)}}))


class GuardTests(unittest.TestCase):
    def test_builder_cannot_write_proof_or_outside_its_zone(self):
        with TempDir() as root:
            Scene(root)
            zone(root)
            self.assertEqual(write(root, "src/api.py").stdout, "")
            for path, words in (("qa/verify_hello.sh", "proof or Oway state"),
                                ("_oway/slices/s001.matrix.md", "proof or Oway state"),
                                ("_oway/evidence/s001.jsonl", "proof or Oway state"),
                                ("app.py", "outside your zone")):
                out = json.loads(write(root, path).stdout)["hookSpecificOutput"]
                self.assertEqual(out["permissionDecision"], "deny", path)
                self.assertIn(words, out["permissionDecisionReason"])

    def test_devproof_and_leads_are_free_and_reads_pass(self):
        with TempDir() as root:
            Scene(root)
            zone(root, role="DevProof")
            self.assertEqual(write(root, "qa/verify_hello.sh").stdout, "")
            zone(root, role="LeadDev")
            self.assertEqual(write(root, "app.py").stdout, "")
            zone(root)
            r = oway(root, "guard", stdin=json.dumps({"tool_name": "Read", "tool_input": {"file_path": "app.py"}}))
            self.assertEqual(r.stdout, "")

    def test_shell_write_outside_zone_fails_the_submit(self):
        with TempDir() as root:
            s = Scene(root)
            zone(root, paths=("src/**",))
            s.app(f"print('hello {s.canary}')\n")  # app.py is outside src/
            r = oway(root, "submit", "s001", "P1")
            self.assertEqual(r.returncode, 1)
            self.assertIn("app.py is outside your zone", r.stdout)


if __name__ == "__main__":
    unittest.main()
