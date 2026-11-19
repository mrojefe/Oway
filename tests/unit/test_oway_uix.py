"""Tests for unified oway-uix skill (Full + Light mode), naming cleanup, and real style/scout CLIs."""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from engine.oway import style

ROOT = Path(__file__).resolve().parents[2]
OWAY_BIN = ROOT / "engine/oway"
SKILL_MD = ROOT / "skills/oway-uix/SKILL.md"
INSPIRATION_MD = ROOT / "skills/oway-uix/references/inspiration-library.md"
VISUAL_CHOICES_MD = ROOT / "skills/oway-uix/references/visual-choices.md"
DESIGN_DOC = ROOT / "docs/oway/design.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not match:
        raise AssertionError(f"missing section: {heading}")
    return match.group(1)


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


def _make_git_repo(root: Path, files: dict[str, str]) -> tuple[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q")
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()
    return str(root), sha


def _run_oway(*args: str, env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(OWAY_BIN), *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


class OwayUixFullModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = _read(SKILL_MD)
        self.lower = self.text.lower()

    def test_problem_ownership_and_keeper_drift_guard(self) -> None:
        self.assertIn("01-intent", self.lower)
        self.assertIn("leadproduct", self.lower)
        self.assertIn("keeperuix", self.lower)
        self.assertIn("never redoes it", self.lower)

    def test_versions_and_visual_baselines_contract(self) -> None:
        self.assertIn("_oway/design/versions/vN/", self.text)
        self.assertIn("_oway/evidence/visual-baselines/", self.text)
        self.assertIn("baseline", self.lower)

    def test_reference_count_and_screenshot_sketching(self) -> None:
        self.assertIn("up to 6", self.lower)
        self.assertNotIn("two to four", self.lower)
        self.assertIn("sketching on a screenshot beats ranking options", self.lower)

    def test_name_what_you_feel_and_screen_recording(self) -> None:
        self.assertIn("name what you feel", self.lower)
        self.assertIn("screen recording", self.lower)

    def test_explicit_external_qa_rubric_gate(self) -> None:
        full_mode = self.text.split("## Light mode (om)")[0].lower()
        self.assertIn("different reviewer", full_mode)
        self.assertIn("below 3", full_mode)
        self.assertIn("3.5", full_mode)

    def test_layer_4_to_layer_6_parity_invariant(self) -> None:
        self.assertIn("journeys written at layer 4 run unchanged on the real frontend", self.lower)
        self.assertIn("build fails", self.lower)

    def test_layers_table_has_not_yet_guardrails(self) -> None:
        layers = _section(self.text, "What to do at each layer, and what to load")
        table_lines = [ln.strip() for ln in layers.splitlines() if ln.strip().startswith("|")]
        self.assertGreaterEqual(len(table_lines), 10)
        header_cells = [c.strip().lower() for c in table_lines[0].strip("|").split("|")]
        self.assertIn("not yet", header_cells)
        not_yet_idx = header_cells.index("not yet")
        for row in table_lines[2:]:
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertGreater(len(cells), not_yet_idx)
            self.assertTrue(cells[not_yet_idx] and cells[not_yet_idx] not in ("-", "—"), row)

    def test_design_system_guard_and_getdesign(self) -> None:
        self.assertIn("getdesign", self.lower)
        self.assertIn("typed components", self.lower)
        self.assertIn("machine-readable tokens", self.lower)
        self.assertIn("permissive license", self.lower)


class OwayUixLightModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.light = _section(_read(SKILL_MD), "Light mode (om)")
        self.lower = self.light.lower()

    def test_light_mode_includes_name_what_you_feel_and_sketching(self) -> None:
        self.assertIn("name what you feel", self.lower)
        self.assertIn("screen recording", self.lower)
        self.assertIn("sketching on a screenshot", self.lower)

    def test_light_mode_includes_design_system_guard_and_getdesign(self) -> None:
        self.assertIn("permissive", self.lower)
        self.assertIn("getdesign", self.lower)
        self.assertTrue(
            "machine-readable" in self.lower or "machine-checkable" in self.lower,
            "Light mode must guard design systems with machine-readable/checkable tokens",
        )

    def test_light_mode_includes_image_word_and_asset_rights_note(self) -> None:
        self.assertIn("IMAGE-WORD", self.light)
        self.assertIn("provenance", self.lower)
        self.assertIn("rights", self.lower)


class OwayUixNamingAndCompatTests(unittest.TestCase):
    def test_no_cgm_references_in_skill_or_design_doc(self) -> None:
        for path in (SKILL_MD, DESIGN_DOC):
            text = _read(path)
            self.assertIsNone(re.search(r"\bcgm(?:-uix)?\b", text, re.I), f"stale cgm token in {path}")

    def test_inspiration_library_uses_oway_paths(self) -> None:
        text = _read(INSPIRATION_MD)
        self.assertIn("$OWAY_INSPIRATION", text)
        self.assertIn("~/.oway/inspiration/", text)
        self.assertNotIn("$CGSPEC_INSPIRATION", text)
        self.assertNotIn("~/.cgspec/inspiration/", text)

    def test_visual_choices_uses_up_to_6_references(self) -> None:
        text = _read(VISUAL_CHOICES_MD).lower()
        self.assertIn("up to 6", text)
        self.assertNotIn("two to four", text)

    def test_design_doc_uses_oway_style_not_style_hub(self) -> None:
        text = _read(DESIGN_DOC)
        self.assertIn("oway style", text)
        self.assertNotIn("style_hub.py", text)

    def test_v03_compat_tokens_preserved_in_skill(self) -> None:
        text = _read(SKILL_MD)
        for token in ("02-OOUX.md", "checkpoint --update-file", "../../engine/CONTRACT.md"):
            self.assertIn(token, text)
        for kind in ("behavior", "layout", "appearance", "content", "motion"):
            self.assertIn(kind, text.lower())
        self.assertNotRegex(text, r"3[-–]5 (quick|deliberately)")

    def test_relative_links_in_oway_uix_and_design_doc_resolve(self) -> None:
        files = list((ROOT / "skills/oway-uix").rglob("*.md")) + [DESIGN_DOC]
        for md in files:
            text = _read(md)
            for ref in re.findall(r"\]\(([^)\s#]+)", text):
                if not re.match(r"^[a-z][a-z0-9+.-]*:", ref, re.I):
                    self.assertTrue((md.parent / ref).resolve().exists(), f"{md}: broken link {ref}")


class OwayStyleCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        packs = _make_git_repo(
            self.tmp / "packs",
            {
                "LICENSE": "MIT License\n",
                "skills/bento/SKILL.md": "---\ndescription: Modular grid cards\n---\n# Bento\n",
                "skills/bento/DESIGN.md": "bento-design-tokens",
                "skills/swiss/SKILL.md": "---\ndescription: Exposed 12-column grid\n---\n# Swiss\n",
            },
        )
        hall = _make_git_repo(
            self.tmp / "hall",
            {
                "skills/hallmark/LICENSE": "MIT License\n",
                "skills/hallmark/references/themes/brutal.md": "material: thick black rules\n",
                "skills/hallmark/references/themes/README.md": "readme\n",
                "skills/hallmark/references/gates.md": "gates\n",
                "skills/hallmark/scripts/sloplint.mjs": "// lint\n",
            },
        )
        self.cache = self.tmp / "styles-cache"
        old = os.environ.get("OWAY_STYLES")
        os.environ["OWAY_STYLES"] = str(self.cache)
        try:
            style.fetch({"typeui": packs, "hallmark": hall})
        finally:
            if old is None:
                os.environ.pop("OWAY_STYLES", None)
            else:
                os.environ["OWAY_STYLES"] = old

    def test_cli_list_search_show_against_fixture_catalog(self) -> None:
        env = {"OWAY_STYLES": str(self.cache)}

        listed = _run_oway("style", "list", env_overrides=env)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("style packs (2)", listed.stdout)
        self.assertIn("bento", listed.stdout)
        self.assertIn("brutal", listed.stdout)

        searched = _run_oway("style", "search", "bento", env_overrides=env)
        self.assertEqual(searched.returncode, 0, searched.stderr)
        self.assertIn("bento", searched.stdout)

        shown = _run_oway("style", "show", "bento", env_overrides=env)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("bento-design-tokens", shown.stdout)

    def test_cli_missing_catalog_exits_2(self) -> None:
        missing = self.tmp / "empty-cache"
        res = _run_oway("style", "list", env_overrides={"OWAY_STYLES": str(missing)})
        self.assertEqual(res.returncode, 2)
        self.assertIn("oway style fetch", res.stderr)


class _ScoutFixtureServer:
    def __init__(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._make_handler())
        self.port = self.server.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _make_handler(self):
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args) -> None:  # noqa: A002
                return

            def do_GET(self) -> None:
                if self.path.startswith("/godly"):
                    body = (
                        f'<img src="{fixture.base}/cdn/items/ab1/0/poster/960.webp">'
                        f'<img src="{fixture.base}/cdn/items/ab1/0/poster/960.webp">'
                        f'<img src="{fixture.base}/cdn/items/ab2/0/poster/960.webp">'
                        f'<img src="{fixture.base}/cdn/items/ab3/0/poster/960.webp">'
                    ).encode("utf-8")
                    self._send(200, "text/html", body)
                elif self.path.startswith("/landbook"):
                    body = (
                        f'<a href="/websites/12-titan-wealth"><img src="{fixture.base}/img/titan.png"></a>'
                        f'<a href="/websites/13-titan-dup"><img src="{fixture.base}/img/titan.png"></a>'
                        f'<a href="/websites/14-avatar-skip"><img src="{fixture.base}/img/avatar-1.png"></a>'
                        f'<a href="/websites/15-acme-ledger"><img src="{fixture.base}/img/acme.png"></a>'
                    ).encode("utf-8")
                    self._send(200, "text/html", body)
                elif self.path.startswith("/cdn/items/") and self.path.endswith("/0/poster/960.webp"):
                    self._send(200, "image/webp", b"RIFF" + b"W" * 2048)
                elif self.path.startswith("/img/") and self.path.endswith(".png"):
                    self._send(200, "image/png", b"\x89PNG" + b"P" * 2048)
                else:
                    self._send(404, "text/plain", b"not found")

            def _send(self, code: int, ctype: str, data: bytes) -> None:
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        return Handler

    def __enter__(self) -> _ScoutFixtureServer:
        self.thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class OwayScoutCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())

    def test_scout_cli_downloads_dedupes_and_writes_carousel_markdown(self) -> None:
        with _ScoutFixtureServer() as srv:
            dest = self.tmp / "refs"
            out_md = self.tmp / "design_references.md"
            env = {
                "OWAY_SCOUT_GODLY_URL": f"{srv.base}/godly",
                "OWAY_SCOUT_GODLY_CDN_URL": f"{srv.base}/cdn",
                "OWAY_SCOUT_LANDBOOK_URL": f"{srv.base}/landbook",
            }
            res = _run_oway(
                "style", "scout", "fintech",
                "--limit", "2",
                "--dest-dir", str(dest),
                "--output-md", str(out_md),
                env_overrides=env,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("scouted 4 references", res.stdout)
            files = sorted(dest.iterdir())
            self.assertEqual(len(files), 4)
            for f in files:
                self.assertGreater(f.stat().st_size, 1000)

            page = _read(out_md)
            for part in (
                "````carousel",
                "<!-- slide -->",
                "## 2. Breakdown",
                "## 3. Plain list",
                "## 4. Anti-slop directives",
                "## 5. Synthesis and token plan",
                "Titan Wealth",
                "Acme Ledger",
                srv.base,
            ):
                self.assertIn(part, page)

    def test_scout_cli_json_output(self) -> None:
        with _ScoutFixtureServer() as srv:
            dest = self.tmp / "refs-json"
            env = {
                "OWAY_SCOUT_GODLY_URL": f"{srv.base}/godly",
                "OWAY_SCOUT_GODLY_CDN_URL": f"{srv.base}/cdn",
                "OWAY_SCOUT_LANDBOOK_URL": f"{srv.base}/landbook",
            }
            res = _run_oway(
                "style", "scout", "analytics",
                "--limit", "1",
                "--dest-dir", str(dest),
                "--json",
                env_overrides=env,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            data = json.loads(res.stdout)
            self.assertEqual(len(data), 2)
            self.assertEqual(len({r["image_url"] for r in data}), 2)
            for item in data:
                self.assertTrue(item["image_url"].startswith(srv.base), item)
                self.assertIn("local_path", item)
                self.assertTrue(Path(item["local_path"]).is_file())

    def test_scout_cli_unreachable_server_returns_zero_references(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            unused_port = sock.getsockname()[1]
        dead = f"http://127.0.0.1:{unused_port}"
        env = {
            "OWAY_SCOUT_GODLY_URL": f"{dead}/godly",
            "OWAY_SCOUT_GODLY_CDN_URL": f"{dead}/cdn",
            "OWAY_SCOUT_LANDBOOK_URL": f"{dead}/landbook",
        }
        res = _run_oway("style", "scout", "offline", "--dest-dir", str(self.tmp / "dead"), env_overrides=env)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("scouted 0 references", res.stdout)


if __name__ == "__main__":
    unittest.main()
