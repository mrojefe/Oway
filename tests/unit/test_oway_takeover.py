"""oway takeover --from cgspec-0.3: moves with history, fixes links, adds headers, keeps the old engine."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from tests.helpers import TempDir, run_script

from oway import takeover  # noqa: E402
from oway.project import OwayError


def cgspec_project(root: Path) -> None:
    files = {
        "docs/_cgspec/project.json": json.dumps({"schema": 1, "path_classes": {"code": ["src/**"], "api": ["api/**"]}}),
        "docs/_cgspec/01-engine/doctor.py": "print('old engine')\n",
        "docs/_memlog.md": "# Project Memory Log\n\n### [M-1] old decision\n",
        "docs/00-INBOX.md": "# Inbox\n",
        "docs/00-INDEX.md": "# Index\n",
        "docs/spines/01-INTENT.md": "# Intent\nSee [research](../_cgspec/02-research/RES-001-market.md).\n",
        "docs/spines/02-OOUX.md": "# Objects\n",
        "docs/_cgspec/02-research/RES-001-market.md": "# Market\nFor [intent](../../spines/01-INTENT.md#why).\n",
        "docs/adrs/ADR-001-hosting.md": "# ADR-001: hosting\n",
        "docs/adrs/.gitkeep": "",
        "docs/prototypes/_vision/README.md": "# Vision\n[v2](html-prototypes/v2-home.html)\n",
        "docs/prototypes/_vision/html-prototypes/v2-home.html": "<html></html>\n",
        "docs/prototypes/_vision/html-prototypes/var-a.html": "<html></html>\n",
        "docs/prototypes/_vision/screenshots/v2-home.png": "png",
        "README.md": "# App\nRead [intent](docs/spines/01-INTENT.md).\n",
    }
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false",
                    "commit", "-qm", "cgspec"], cwd=root, check=True)


class TakeoverTests(unittest.TestCase):
    def test_dry_run_changes_nothing(self):
        with TempDir() as root:
            cgspec_project(root)
            lines = takeover.run(root, "fr", dry_run=True)
            self.assertIn("move docs/spines/02-OOUX.md -> _oway/spines/02-objects.md", lines)
            self.assertIn("unknown docs/prototypes/_vision/html-prototypes/var-a.html (waits for the owner)", lines)
            self.assertFalse((root / "_oway").exists())

    def test_takeover_end_to_end(self):
        with TempDir() as root:
            cgspec_project(root)
            lines = takeover.run(root, "fr")
            self.assertEqual(lines[-1], "doctor: ok", "\n".join(lines))
            oway = root / "_oway"
            self.assertTrue((oway / "spines/02-objects.md").exists())
            self.assertTrue((oway / "decisions/ADR-001-hosting.md").exists())
            self.assertFalse((oway / "decisions/.gitkeep").exists())
            self.assertTrue((oway / "design/versions/v2/v2-home.html").exists())
            self.assertTrue((oway / "design/versions/v2/screenshots/v2-home.png").exists())
            # the old engine is kept until the owner removes it
            self.assertTrue((root / "docs/_cgspec/01-engine/doctor.py").exists())
            # links follow the files, anchors kept
            self.assertIn("(../research/RES-001-market.md)", (oway / "spines/01-intent.md").read_text())
            self.assertIn("(../spines/01-intent.md#why)", (oway / "research/RES-001-market.md").read_text())
            self.assertIn("(_oway/spines/01-intent.md)", (root / "README.md").read_text())
            # headers added, decisions only proposed
            self.assertIn("type: decision\nstate: proposed", (oway / "decisions/ADR-001-hosting.md").read_text())
            # old ledger kept below "Before Oway", plus a takeover line
            led = (oway / "LEDGER.md").read_text()
            self.assertIn("## Before Oway", led)
            self.assertIn("[M-1] old decision", led)
            self.assertIn("takeover from CGSpec 0.3", led)
            cfg = json.loads((oway / "config.json").read_text())
            self.assertEqual(cfg["language"], "fr")
            self.assertEqual(cfg["path_classes"]["api"], ["api/**"])
            status = subprocess.run(["git", "status", "--short"], cwd=root, capture_output=True, text=True).stdout
            self.assertIn("docs/adrs/ADR-001-hosting.md -> _oway/decisions/ADR-001-hosting.md", status)

    def test_refuses_non_cgspec_and_second_run(self):
        with TempDir() as root:
            with self.assertRaises(OwayError):
                takeover.run(root, "en")
            cgspec_project(root)
            takeover.run(root, "en")
            r = run_script("oway", "--root", str(root), "takeover", "--from", "cgspec-0.3")
            self.assertEqual(r.returncode, 2)
            self.assertIn("already exists", r.stderr)


if __name__ == "__main__":
    unittest.main()
