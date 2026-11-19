"""Canonical 1-file-per-role inventory, schema, and governance tests (P1-01..P1-03)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from tests.helpers import REPO

from oway import headers  # noqa: E402

ROLES_DIR = REPO / "docs/oway/roles"
TEMPLATE_PATH = REPO / "docs/oway/templates/role-card.md"

EXPECTED_ROLES: frozenset[str] = frozenset({
    # oway/ (6)
    "oway/leadoway.md",
    "oway/owayhelpers.md",
    "oway/leadowayboard.md",
    "oway/leadowayscout.md",
    "oway/scoutoway.md",
    "oway/keeperoway.md",
    # keeper/ (1)
    "keeper/leadkeeper.md",
    # product/ (6)
    "product/leadproduct.md",
    "product/advisorproduct.md",
    "product/leadproductboard.md",
    "product/leadproductscout.md",
    "product/scoutproduct.md",
    "product/keeperproduct.md",
    # uix/ (7)
    "uix/leaduix.md",
    "uix/advisoruix.md",
    "uix/leaduixboard.md",
    "uix/leaduixscout.md",
    "uix/scoutuix.md",
    "uix/uix-worker.md",
    "uix/keeperuix.md",
    # dev/ (13)
    "dev/leaddev.md",
    "dev/advisordev.md",
    "dev/leaddevboard.md",
    "dev/leaddevscout.md",
    "dev/scoutdev.md",
    "dev/devops.md",
    "dev/devbackend.md",
    "dev/devfrontend.md",
    "dev/devdata.md",
    "dev/devai.md",
    "dev/devmobile.md",
    "dev/dev-specialist.md",
    "dev/keeperdev.md",
    # qa/ (12)
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
    "qa/keeperqa.md",
    # shared/ (3)
    "shared/board-member.md",
    "shared/proof-matrix-author.md",
    "shared/adversarial-reviewer.md",
})

LEGACY_ROLES: frozenset[str] = frozenset({
    "oway/owayhelper.md",
    "keeper/keeperx.md",
    "dev/dev-builder.md",
    "dev/devproof.md",
    "shared/leadxboard.md",
    "shared/leadxscout.md",
    "shared/scoutx.md",
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
        if p.name != "README.md"
    )


def _extract_sections(text: str) -> dict[str, str]:
    """Return mapping of H2 heading title -> stripped section body."""
    parts = re.split(r"^##\s+(.+?)\s*$", text, flags=re.M)
    sections: dict[str, str] = {}
    for i in range(1, len(parts) - 1, 2):
        sections[parts[i].strip()] = parts[i + 1].strip()
    return sections


class RoleInventoryTests(unittest.TestCase):
    def test_exact_48_canonical_role_files_and_no_legacy_cards(self):
        actual = {p.relative_to(ROLES_DIR).as_posix() for p in _role_files()}
        self.assertEqual(len(EXPECTED_ROLES), 48)
        for legacy in sorted(LEGACY_ROLES):
            self.assertNotIn(legacy, actual, f"Legacy collapsed role card still present: {legacy}")
        missing = sorted(EXPECTED_ROLES - actual)
        extra = sorted(actual - EXPECTED_ROLES)
        self.assertEqual(missing, [], f"Missing canonical role cards: {missing}")
        self.assertEqual(extra, [], f"Unexpected extra role cards: {extra}")

    def test_roles_readme_links_all_48_cards_without_broken_links(self):
        readme = ROLES_DIR / "README.md"
        text = readme.read_text(encoding="utf-8")
        links = set(re.findall(r"\]\(([^)\s#]+)\)", text))
        for rel in sorted(EXPECTED_ROLES):
            self.assertIn(rel, links, f"docs/oway/roles/README.md does not link to {rel}")
        for link in sorted(links):
            if not re.match(r"^[a-z][a-z0-9+.-]*:", link, re.I):
                target = (readme.parent / link).resolve()
                self.assertTrue(target.exists(), f"docs/oway/roles/README.md has broken link: {link}")


class RoleSchemaTests(unittest.TestCase):
    def test_template_includes_proof_field(self):
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^proof:\s*\S+")

    def test_all_48_cards_have_valid_frontmatter_and_9_non_empty_sections(self):
        files = _role_files()
        self.assertEqual(len(files), 48)
        for path in files:
            rel = path.relative_to(ROLES_DIR).as_posix()
            text = path.read_text(encoding="utf-8")
            fm = headers.parse(text)
            self.assertIsNotNone(fm, f"{rel}: missing YAML frontmatter")
            assert fm is not None
            self.assertEqual(headers.problems(fm), [], f"{rel}: invalid Oway header")
            for key in REQUIRED_FM_KEYS:
                self.assertIn(key, fm, f"{rel}: missing frontmatter key '{key}'")
                self.assertTrue(fm[key].strip(), f"{rel}: empty frontmatter key '{key}'")
            self.assertEqual(fm["type"], "agent", f"{rel}: type must be 'agent'")
            self.assertEqual(fm["name"], path.stem, f"{rel}: frontmatter name must equal filename stem")

            sections = _extract_sections(text)
            for heading in REQUIRED_SECTIONS:
                self.assertIn(heading, sections, f"{rel}: missing section '## {heading}'")
                self.assertTrue(sections[heading], f"{rel}: empty section '## {heading}'")


class RoleGovernanceTests(unittest.TestCase):
    def test_advisor_files_only_for_top_team_leads_and_qa_subleads_advised_by_leadqa(self):
        advisor_stems = sorted(
            p.stem for p in _role_files() if p.stem.startswith("advisor")
        )
        self.assertEqual(
            advisor_stems,
            ["advisordev", "advisorproduct", "advisorqa", "advisoruix"],
            f"Unexpected advisor role files: {advisor_stems}",
        )
        for sublead in ("qa/leadqatester.md", "qa/leadqadelivery.md", "qa/leadqaarchitect.md"):
            text = (ROLES_DIR / sublead).read_text(encoding="utf-8")
            self.assertRegex(
                text,
                r"(?i)(advis\w*.*LeadQA|LeadQA.*advis\w*)",
                f"{sublead} must explicitly name LeadQA as its advisor",
            )

    def test_all_keepers_and_leadkeeper_enforce_read_only_constraints(self):
        keeper_paths = (
            "keeper/leadkeeper.md",
            "oway/keeperoway.md",
            "product/keeperproduct.md",
            "uix/keeperuix.md",
            "dev/keeperdev.md",
            "qa/keeperqa.md",
        )
        for rel in keeper_paths:
            text = (ROLES_DIR / rel).read_text(encoding="utf-8")
            self.assertRegex(
                text,
                r"(?i)read-only",
                f"{rel} must explicitly enforce read-only constraints",
            )

    def test_index_md_ownership_and_verification_split(self):
        delivery_text = (ROLES_DIR / "qa/leadqadelivery.md").read_text(encoding="utf-8")
        self.assertRegex(
            delivery_text,
            r"(?is)INDEX\.md.*(rebuild|script)|(rebuild|script).*INDEX\.md",
            "qa/leadqadelivery.md must state ownership of the INDEX.md rebuild script",
        )
        keeper_qa_text = (ROLES_DIR / "qa/keeperqa.md").read_text(encoding="utf-8")
        self.assertRegex(
            keeper_qa_text,
            r"(?is)INDEX\.md.*(verif\w*|check\w*)|(verif\w*|check\w*).*INDEX\.md",
            "qa/keeperqa.md must state verification of INDEX.md",
        )


if __name__ == "__main__":
    unittest.main()
