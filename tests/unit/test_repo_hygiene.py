"""Repository rename, legacy retirement, and workstation/slug hygiene tests (PR 4)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

from tests.helpers import REPO

HISTORICAL_PREFIXES = (
    "docs/adr/",
    "docs/_cgspec/02-research/",
    "docs/_cgspec/03-councils/",
)
HISTORICAL_EXACT = frozenset({"CHANGELOG.md"})

FORBIDDEN_PATTERNS: tuple[tuple[str, str], ...] = (
    ("linux_home", "/home/" + "ojefe"),
    ("macos_home", "/Users/" + "ojefe"),
    ("private_gov_dir", "_CG-" + "Gov"),
    ("legacy_workspace", "cgspec-" + "workspace"),
    ("workstation_docs_dir", "~/Documents/" + "Project/"),
    ("old_repo_slug", "BeOjefe/" + "cgspec"),
    ("personal_handle", "@" + "ojefe"),
    ("personal_trailer", "Approved-by: " + "Ojefe"),
)


def _is_historical(rel_path: str) -> bool:
    if rel_path in HISTORICAL_EXACT:
        return True
    return any(rel_path.startswith(prefix) for prefix in HISTORICAL_PREFIXES)


def _scan_text(text: str) -> list[str]:
    return [label for label, needle in FORBIDDEN_PATTERNS if needle in text]


def _tracked_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=REPO, text=True)
    return [line for line in out.splitlines() if line]


def _load_install_module():
    spec = importlib.util.spec_from_file_location("oway_install_check", REPO / "engine/install.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ManifestAndSourceTests(unittest.TestCase):
    """P4-01: Plugin/marketplace manifests renamed to oway and PLUGIN_SOURCE points to mrojefe/Oway."""

    def test_plugin_manifests_named_oway(self):
        root_manifest = json.loads((REPO / "plugin.json").read_text(encoding="utf-8"))
        claude_manifest = json.loads((REPO / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(root_manifest["name"], "oway")
        self.assertEqual(claude_manifest["name"], "oway")

    def test_marketplace_manifest_named_oway(self):
        mp = json.loads((REPO / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(mp["name"], "oway-local")
        plugin = mp["plugins"][0]
        self.assertEqual(plugin["name"], "oway")
        self.assertEqual(plugin["interface"]["displayName"], "Oway")

    def test_install_plugin_source_points_to_oway_repo(self):
        mod = _load_install_module()
        self.assertEqual(mod.PLUGIN_SOURCE, "https://github.com/mrojefe/Oway.git")


class LegacyRetirementTests(unittest.TestCase):
    """P4-02: Legacy agents/cgspec-*.md and .claude/rules/cgspec-contributor.md retired."""

    def test_legacy_agent_files_removed(self):
        leftover = sorted(p.relative_to(REPO).as_posix() for p in (REPO / "agents").glob("cgspec-*.md")) if (REPO / "agents").exists() else []
        self.assertEqual(leftover, [], f"legacy agent files still present: {leftover}")

    def test_legacy_claude_rule_removed(self):
        rule_path = REPO / ".claude/rules/cgspec-contributor.md"
        self.assertFalse(rule_path.exists(), "legacy .claude/rules/cgspec-contributor.md still present")

    def test_docs_do_not_advertise_retired_legacy_agents(self):
        stale_phrases = (
            "agents/" + "cgspec-",
            "cgspec-" + "contributor",
            "eight role definitions",
            "eight bounded team role definitions",
            "Eight definitions; runtime rehearsal pending",
        )
        for rel in ("README.md", "docs/00-INDEX.md", "docs/STATUS.md", "docs/METHOD.md"):
            text = (REPO / rel).read_text(encoding="utf-8")
            for phrase in stale_phrases:
                self.assertNotIn(phrase, text, f"{rel} still mentions retired legacy agent prose: {phrase!r}")


class WorkstationAndSlugHygieneTests(unittest.TestCase):
    """P4-03: Zero personal/workstation paths or old repo slugs across non-historical tracked files."""

    def test_scanner_canary_catches_every_forbidden_pattern(self):
        for label, needle in FORBIDDEN_PATTERNS:
            hits = _scan_text(f"sample line containing {needle} in fixture")
            self.assertIn(label, hits, f"canary failed to detect {label}")
        self.assertEqual(_scan_text("https://github.com/mrojefe/Oway /home/user/.oway @owner"), [])

    def test_no_forbidden_patterns_in_non_historical_tracked_files(self):
        offenders: list[str] = []
        for rel in _tracked_files():
            if _is_historical(rel):
                continue
            path = REPO / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            hits = _scan_text(text)
            if hits:
                offenders.append(f"{rel}: {', '.join(hits)}")
        self.assertEqual(offenders, [], "Forbidden hygiene patterns found:\n" + "\n".join(offenders))


class ReadmeHygieneTests(unittest.TestCase):
    """P4-04: README version badge and install examples use oway naming and current version."""

    def test_readme_badge_and_examples_updated(self):
        version = (REPO / "engine/VERSION").read_text(encoding="utf-8").strip()
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"version-{version}", readme)
        self.assertIn("/tmp/oway-example", readme)
        self.assertIn("oway@<marketplace>", readme)
        self.assertIn("oway@oway-local", readme)
        self.assertNotIn("/tmp/cgspec-example", readme)
        self.assertNotIn("cgspec@<marketplace>", readme)
        self.assertNotIn("cgspec@cgspec-local", readme)


class VersionParityTests(unittest.TestCase):
    """SemVer parity across all 4 manifests and engine/VERSION."""

    def test_all_four_manifests_match_engine_version_and_semver(self):
        version = (REPO / "engine/VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertEqual(version, "0.3.13")
        for rel in ("plugin.json", ".claude-plugin/plugin.json"):
            data = json.loads((REPO / rel).read_text(encoding="utf-8"))
            self.assertEqual(data["version"], version, f"{rel} version mismatch")
        mp = json.loads((REPO / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(mp["plugins"][0]["version"], version, "marketplace.json version mismatch")


if __name__ == "__main__":
    unittest.main()
