"""oway style scout: the free reference scout, with the network replaced."""
import json
import tempfile
import unittest
from pathlib import Path

from engine.oway import scout

GODLY = "".join(f'<img src="https://cdn.recent.design/items/ab{i}/0/poster/960.webp">' for i in range(5))
LANDBOOK = (
    '<a href="/websites/12-titan-wealth"><span></span><img src="https://img.example/titan.png"></a>'
    '<a href="/websites/13-titan-wealth-again"><img src="https://img.example/titan.png"></a>'
    '<a href="/websites/14-acme-ledger"><img src="https://img.example/acme.png"></a>'
)


class ScoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.real_fetch, self.real_download = scout.fetch, scout.download
        scout.fetch = lambda url, timeout=12: (GODLY if "godly" in url else LANDBOOK).encode()
        scout.download = lambda url, dest: (dest.parent.mkdir(parents=True, exist_ok=True),
                                            dest.write_bytes(b"x" * 2000), True)[2]
        self.addCleanup(lambda: (setattr(scout, "fetch", self.real_fetch), setattr(scout, "download", self.real_download)))

    def test_limit_and_dedupe_across_both_sources(self):
        refs = scout.scout("dashboard", 3)
        self.assertEqual(sum(r["source"].startswith("Godly") for r in refs), 3)
        self.assertEqual(sum(r["source"].startswith("Land-book") for r in refs), 2)
        self.assertEqual(len({r["image_url"] for r in refs}), len(refs))

    def test_same_site_with_two_images_is_kept_once(self):
        scout.fetch = lambda url, timeout=12: (GODLY if "godly" in url else (
            '<a href="/websites/12-titan"><img src="https://img.example/t1.png"></a>'
            '<a href="/websites/12-titan"><img src="https://img.example/t2.png"></a>'
            '<a href="/websites/14-acme"><img src="https://img.example/acme.png"></a>')).encode()
        links = [r["ref_url"] for r in scout.landbook("x", 3)]
        self.assertEqual(links, ["https://land-book.com/websites/12-titan", "https://land-book.com/websites/14-acme"])

    def test_run_writes_images_and_the_references_page(self):
        out = scout.run("fintech", self.tmp / "refs", self.tmp / "page.md", limit=2)
        self.assertIn("scouted 4 references", out[0])
        self.assertEqual(len(list((self.tmp / "refs").iterdir())), 4)
        page = (self.tmp / "page.md").read_text(encoding="utf-8")
        for part in ("````carousel", "<!-- slide -->", "## 2. Breakdown", "## 3. Plain list",
                     "## 5. Synthesis and token plan", "#0A0A0C", "44x44px"):
            self.assertIn(part, page)

    def test_json_output_and_failed_download_falls_back_to_the_remote_url(self):
        scout.download = lambda url, dest: False
        data = json.loads(scout.run("x", self.tmp / "refs", None, limit=1, as_json=True)[0])
        self.assertTrue(all("local_path" not in r for r in data))
        self.assertTrue(all(r["image_url"].startswith("https://") for r in data))

    def test_sites_down_gives_an_empty_result_not_a_crash(self):
        scout.fetch = lambda url, timeout=12: None
        self.assertEqual(scout.run("x", self.tmp / "refs", None)[0], "scouted 0 references")


if __name__ == "__main__":
    unittest.main()
