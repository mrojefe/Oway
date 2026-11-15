"""oway style: fetch into a cache, then list, search and show."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from engine.oway import style
from engine.oway.project import OwayError


def git(cwd, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                   check=True, capture_output=True)


def make_repo(root, files):
    root.mkdir(parents=True)
    git(root, "init", "-q")
    for rel, text in files.items():
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "x")
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()
    return str(root), sha


class StyleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.packs = make_repo(self.tmp / "packs", {
            "LICENSE": "MIT License\n",
            "skills/bento/SKILL.md": "---\ndescription: Modular grid cards\n---\n",
            "skills/bento/DESIGN.md": "tokens",
            "skills/neon/SKILL.md": "---\ndescription: Glow\n---\n",
        })
        self.hall = make_repo(self.tmp / "hall", {
            "skills/hallmark/LICENSE": "MIT License\n",
            "skills/hallmark/references/themes/brutal.md": "material: thick rules\n",
            "skills/hallmark/references/themes/README.md": "readme",
            "skills/hallmark/references/gates.md": "gates",
            "skills/hallmark/scripts/sloplint.mjs": "//",
        })
        self.sources = {"typeui": self.packs, "hallmark": self.hall}
        os.environ["OWAY_STYLES"] = str(self.tmp / "cache")
        self.addCleanup(os.environ.pop, "OWAY_STYLES", None)

    def test_missing_catalog_says_how_to_fetch(self):
        with self.assertRaises(OwayError) as ctx:
            style.listing()
        self.assertIn("oway style fetch", str(ctx.exception))

    def test_fetch_builds_the_catalog_and_keeps_both_licences(self):
        msg = style.fetch(self.sources)
        self.assertIn("2 style packs, 1 themes", msg)
        cache = self.tmp / "cache"
        self.assertTrue((cache / "licenses/LICENSE-awesome-design-skills-MIT.txt").exists())
        self.assertTrue((cache / "licenses/LICENSE-hallmark-MIT.txt").exists())
        self.assertTrue((cache / "hallmark-themes/references/gates.md").exists())
        self.assertIn(self.packs[1], (cache / "SOURCE.txt").read_text(encoding="utf-8"))

    def test_search_show_and_list(self):
        style.fetch(self.sources)
        self.assertTrue(any("bento" in l for l in style.search("bento")))
        self.assertTrue(any("brutal" in l for l in style.search("neobrutalism")))
        self.assertIn("tokens", "\n".join(style.show("bento")))
        self.assertIn("style packs (2)", style.listing()[0])

    def test_a_second_fetch_replaces_the_first(self):
        style.fetch(self.sources)
        (self.tmp / "cache/stale.txt").write_text("x", encoding="utf-8")
        style.fetch(self.sources)
        self.assertFalse((self.tmp / "cache/stale.txt").exists())


if __name__ == "__main__":
    unittest.main()
