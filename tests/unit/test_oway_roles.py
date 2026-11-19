"""Canonical 1-file-per-role inventory, schema, skill mapping, TEAM.md, and UIX governance tests."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from tests.helpers import REPO

from oway import headers  # noqa: E402

ROLES_DIR = REPO / "agents"
SKILLS_DIR = REPO / "skills"
TEMPLATE_PATH = REPO / "docs/oway/templates/role-card.md"

EXPECTED_ROLES: frozenset[str] = frozenset({
    # oway/ (5)
    "oway/leadoway.md",
    "oway/owayhelpers.md",
    "oway/leadowayboard.md",
    "oway/leadowayscout.md",
    "oway/scoutoway.md",
    # keeper/ (6, all watchers unified under LeadKeeper)
    "keeper/leadkeeper.md",
    "keeper/keeperoway.md",
    "keeper/keeperproduct.md",
    "keeper/keeperuix.md",
    "keeper/keeperdev.md",
    "keeper/keeperqa.md",
    # product/ (5)
    "product/leadproduct.md",
    "product/advisorproduct.md",
    "product/leadproductboard.md",
    "product/leadproductscout.md",
    "product/scoutproduct.md",
    # uix/ (6)
    "uix/leaduix.md",
    "uix/advisoruix.md",
    "uix/leaduixboard.md",
    "uix/leaduixscout.md",
    "uix/scoutuix.md",
    "uix/uix-worker.md",
    # dev/ (13)
    "dev/leaddev.md",
    "dev/advisordev.md",
    "dev/leaddevboard.md",
    "dev/leaddevscout.md",
    "dev/scoutdev.md",
    "dev/dev.md",
    "dev/devops.md",
    "dev/devbackend.md",
    "dev/devfrontend.md",
    "dev/devdata.md",
    "dev/devai.md",
    "dev/devmobile.md",
    "dev/dev-specialist.md",
    # qa/ (11)
    "qa/leadqa.md",
    "qa/advisorqa.md",
    "qa/leadqaboard.md",
    "qa/leadqascout.md",
    "qa/scoutqa.md",
    "qa/leadqatester.md",
    "qa/qatester.md",
    "qa/leadqadelivery.md",
    "qa/qadelivery.md",
    "qa/leadqaarchitect.md",
    "qa/qaarchitect.md",
    # shared/ (3)
    "shared/board-member.md",
    "shared/proof-matrix-author.md",
    "shared/adversarial-reviewer.md",
})

EXPECTED_TEAM_FILES: frozenset[str] = frozenset({
    "oway/TEAM.md",
    "product/TEAM.md",
    "uix/TEAM.md",
    "dev/TEAM.md",
    "qa/TEAM.md",
})

REQUIRED_FM_KEYS: tuple[str, ...] = (
    "name",
    "description",
    "type",
    "state",
    "created",
    "approved",
    "owner",
    "updated",
    "proof",
)

REQUIRED_SECTIONS: tuple[str, ...] = (
    "What it does",
    "Skills it loads",
    "What it reads and writes",
    "Who it talks to",
    "What it never does",
    "Model",
    "Hooks and limits",
    "Message length",
    "How many",
)


def _role_files() -> list[Path]:
    return sorted(
        p for p in ROLES_DIR.rglob("*.md")
        if p.name not in ("README.md", "TEAM.md")
    )


def _extract_sections(text: str) -> dict[str, str]:
    """Return mapping of H2 heading title -> stripped section body."""
    parts = re.split(r"^##\s+(.+?)\s*$", text, flags=re.M)
    sections: dict[str, str] = {}
    for i in range(1, len(parts) - 1, 2):
        sections[parts[i].strip()] = parts[i + 1].strip()
    return sections


class RoleInventoryTests(unittest.TestCase):
    def test_exact_49_canonical_role_files_and_5_team_contracts(self):
        actual_roles = {p.relative_to(ROLES_DIR).as_posix() for p in _role_files()}
        actual_teams = {p.relative_to(ROLES_DIR).as_posix() for p in ROLES_DIR.glob("*/TEAM.md")}
        self.assertEqual(len(EXPECTED_ROLES), 49)
        self.assertEqual(sorted(EXPECTED_ROLES - actual_roles), [])
        self.assertEqual(sorted(actual_roles - EXPECTED_ROLES), [])
        self.assertEqual(actual_teams, set(EXPECTED_TEAM_FILES))
        old_roles_files = [
            p.relative_to(REPO).as_posix()
            for p in (REPO / "docs/oway/roles").rglob("*.md")
            if p.name != "README.md"
        ]
        self.assertEqual(old_roles_files, [], "Old role cards must not linger in docs/oway/roles/")

    def test_roles_readme_links_all_49_cards_and_team_files_cleanly(self):
        readme = ROLES_DIR / "README.md"
        text = readme.read_text(encoding="utf-8")
        links = set(re.findall(r"\]\(([^)\s#]+)", text))
        for rel in sorted(EXPECTED_ROLES | EXPECTED_TEAM_FILES):
            self.assertIn(rel, links, f"agents/README.md does not link to {rel}")
        for link in sorted(links):
            if not re.match(r"^[a-z][a-z0-9+.-]*:", link, re.I):
                target = (readme.parent / link).resolve()
                self.assertTrue(target.exists(), f"agents/README.md has broken link: {link}")


class RoleSchemaTests(unittest.TestCase):
    def test_all_49_cards_and_5_team_files_have_valid_frontmatter_and_sections(self):
        files = _role_files()
        self.assertEqual(len(files), 49)
        for path in files:
            rel = path.relative_to(ROLES_DIR).as_posix()
            text = path.read_text(encoding="utf-8")
            fm = headers.parse(text)
            self.assertIsNotNone(fm, f"{rel}: missing YAML frontmatter")
            assert fm is not None
            self.assertEqual(headers.problems(fm), [], f"{rel}: invalid Oway header")
            for key in REQUIRED_FM_KEYS:
                self.assertIn(key, fm, f"{rel}: missing '{key}'")
                self.assertTrue(fm[key].strip(), f"{rel}: empty '{key}'")
            self.assertEqual(fm["type"], "agent", f"{rel}: type must be 'agent'")
            self.assertEqual(fm["name"], path.stem, f"{rel}: name must match stem")
            sections = _extract_sections(text)
            for heading in REQUIRED_SECTIONS:
                self.assertTrue(sections.get(heading), f"{rel}: missing/empty '## {heading}'")

        for rel in sorted(EXPECTED_TEAM_FILES):
            fm = headers.parse((ROLES_DIR / rel).read_text(encoding="utf-8"))
            self.assertIsNotNone(fm, f"{rel}: missing YAML frontmatter")
            assert fm is not None
            self.assertEqual(headers.problems(fm), [], f"{rel}: invalid TEAM header")
            self.assertEqual(fm["type"], "team", f"{rel}: type must be 'team'")


class RoleGovernanceAndSkillsTests(unittest.TestCase):
    def test_every_skill_loaded_by_a_role_card_exists_in_skills_dir(self):
        self.assertTrue((SKILLS_DIR / "free-ui-ux-scout/SKILL.md").is_file())
        for path in _role_files():
            sections = _extract_sections(path.read_text(encoding="utf-8"))
            raw = sections["Skills it loads"].strip()
            if raw.lower().startswith("none"):
                continue
            for slug in [s.strip() for s in raw.split(",") if s.strip()]:
                self.assertTrue(
                    (SKILLS_DIR / slug / "SKILL.md").is_file(),
                    f"{path.relative_to(ROLES_DIR)}: missing skills/{slug}/SKILL.md",
                )

    def test_team_uix_cards_and_team_md_enforce_8_layers_and_design_skills(self):
        team_uix = (ROLES_DIR / "uix/TEAM.md").read_text(encoding="utf-8")
        leaduix = (ROLES_DIR / "uix/leaduix.md").read_text(encoding="utf-8")
        worker = (ROLES_DIR / "uix/uix-worker.md").read_text(encoding="utf-8")
        keeper_uix = (ROLES_DIR / "keeper/keeperuix.md").read_text(encoding="utf-8")
        for text, name in ((team_uix, "uix/TEAM.md"), (leaduix, "uix/leaduix.md")):
            for tok in ("8", "01-intent", "oway-uix", "free-ui-ux-scout", "QATester", "3.5"):
                self.assertIn(tok, text, f"{name} missing {tok}")
        for rel in ("uix/leaduix.md", "uix/leaduixscout.md", "uix/scoutuix.md", "uix/uix-worker.md"):
            card = (ROLES_DIR / rel).read_text(encoding="utf-8")
            self.assertIn("free-ui-ux-scout", card, f"{rel} must load free-ui-ux-scout")
            self.assertIn("oway-uix", card, f"{rel} must load oway-uix")
        self.assertIn("tokens.dtcg.json", worker)
        self.assertIn("65 anti-slop", worker)
        self.assertIn("QATester", keeper_uix)
        self.assertRegex(keeper_uix, r"(?i)read-only")

    def test_advisor_and_keeper_governance_rules(self):
        advisors = sorted(p.stem for p in _role_files() if p.stem.startswith("advisor"))
        self.assertEqual(advisors, ["advisordev", "advisorproduct", "advisorqa", "advisoruix"])
        for sublead in ("qa/leadqatester.md", "qa/leadqadelivery.md", "qa/leadqaarchitect.md"):
            self.assertRegex((ROLES_DIR / sublead).read_text(encoding="utf-8"), r"(?i)LeadQA")
        for keeper_name in ("leadkeeper.md", "keeperoway.md", "keeperproduct.md", "keeperuix.md", "keeperdev.md", "keeperqa.md"):
            p = ROLES_DIR / "keeper" / keeper_name
            self.assertTrue(p.is_file(), f"missing keeper/{keeper_name}")
            self.assertRegex(p.read_text(encoding="utf-8"), r"(?i)read-only")
        self.assertRegex((ROLES_DIR / "qa/leadqadelivery.md").read_text(encoding="utf-8"), r"(?is)INDEX\.md.*script")
        self.assertRegex((ROLES_DIR / "keeper/keeperqa.md").read_text(encoding="utf-8"), r"(?is)INDEX\.md")


if __name__ == "__main__":
    unittest.main()
