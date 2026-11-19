"""PR 5 Docs Consolidation, Delivery CI Watch, and Disposable-Consumer E2E tests (P5-01..P5-04)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import REPO, TempDir, git

OWAY_MOD = REPO / "engine/oway"
ALL_TOOLS = "pi,opencode,claude,codex,antigravity,oway"
CANARY = "cedar-7319"

THREE_PARTS = (
    "# {title}\n\n"
    "## 1. The goal\nShip the slice cleanly.\n\n"
    "## 2. What you get\nWorking greeting CLI.\n\n"
    "## 3. The proof you will have\nLive CLI output with canary and version.\n"
)

MATRIX_DOC = f"""---
name: s001-matrix
description: Proof matrix for s001
type: matrix
parent: s001
state: draft
approved: yes
owner: proof-matrix-author
verifiers: qa/verify.sh
---

# S001 proof matrix

| id | Interaction | Accepted proof | Medium | Verifier commands | Canary | State |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Run app greeting | Live output includes canary | screenshot + live output | `sh qa/verify.sh` | {CANARY} | OPEN |
| P2 | Check app version | CLI prints semver | command record | `python3 src/app.py --version` | none | OPEN |
"""

REVIEWER_PY = (
    "import json, re, sys\n"
    "text = sys.stdin.read()\n"
    "m = re.search(r'Evidence record (\\d+):', text)\n"
    "seq = int(m.group(1)) if m else 0\n"
    "print(json.dumps({'verdict': 'PASS', 'reason': 'verified live canary', 'evidence_ids': [seq]}))\n"
)

APP_TMPL = (
    "import sys\n"
    "if '--version' in sys.argv:\n"
    "    print('1.0.0')\n"
    "    raise SystemExit(0)\n"
    "print({msg!r})\n"
)


def _clean_env(home: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    for key in ("OM_TOOLS", "OM_OWAY_SKILLS", "OM_OWAY_AGENTS", "OM_HOME", "OWAY_ROLE"):
        env.pop(key, None)
    env["HOME"] = str(home)
    env["OWAY_PLATFORM"] = str(home / ".oway")
    if extra:
        env.update(extra)
    return env


def _run(cmd: list[str], cwd: Path, env: dict[str, str], stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), env=env, input=stdin, capture_output=True, text=True)


def _write_doc(path: Path, name: str, kind: str, parent: str, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"---\nname: {name}\ndescription: {title}\ntype: {kind}\n"
        f"state: draft\nparent: {parent}\n---\n\n"
    )
    path.write_text(header + THREE_PARTS.format(title=title), encoding="utf-8")


def _stage_slice_files(root: Path) -> None:
    oway = root / "_oway"
    _write_doc(oway / "milestones/m01.md", "m01", "milestone", "project", "Milestone 01")
    _write_doc(oway / "slices/s001.md", "s001", "slice", "m01", "Slice 001")
    (oway / "slices/s001.matrix.md").write_text(MATRIX_DOC, encoding="utf-8")
    (root / "qa").mkdir(exist_ok=True)
    (root / "qa/verify.sh").write_text("#!/bin/sh\npython3 src/app.py\n", encoding="utf-8")
    (root / "qa/reviewer.py").write_text(REVIEWER_PY, encoding="utf-8")
    (root / "src").mkdir(exist_ok=True)
    (root / "src/app.py").write_text(APP_TMPL.format(msg="hello without token"), encoding="utf-8")
    (oway / "state").mkdir(exist_ok=True)
    (oway / "state/checkpoint.json").write_text(
        json.dumps({"slice": "s001", "role": "DevBackend", "zone": ["src/**"]}),
        encoding="utf-8",
    )
    cfg_path = oway / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["reviewer_command"] = f"{sys.executable} {root / 'qa/reviewer.py'}"
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


class DocsConsolidationTests(unittest.TestCase):
    """P5-01: Canonical glossary, doc entry links, and 0.3.8-0.3.12 status/changelog."""

    def test_glossary_exists_with_core_terms_and_is_linked_from_entry_docs(self):
        glossary_path = REPO / "docs/GLOSSARY.md"
        self.assertTrue(glossary_path.is_file(), "docs/GLOSSARY.md must exist")
        glossary = glossary_path.read_text(encoding="utf-8")
        for term in ("Oway", "om", "Slice", "Proof matrix", "Keeper", "LeadQADelivery"):
            self.assertIn(term, glossary, f"docs/GLOSSARY.md missing term: {term}")

        expected_links = {
            "docs/README.md": "GLOSSARY.md",
            "docs/oway/README.md": "../GLOSSARY.md",
            "docs/oway/teams-and-roles.md": "../GLOSSARY.md",
            "docs/00-INDEX.md": "GLOSSARY.md",
        }
        for rel, target in expected_links.items():
            text = (REPO / rel).read_text(encoding="utf-8")
            self.assertIn(target, text, f"{rel} must link {target}")

        docs_readme = (REPO / "docs/README.md").read_text(encoding="utf-8")
        for target in ("oway/README.md", "GLOSSARY.md", "STATUS.md", "METHOD.md", "00-INDEX.md"):
            self.assertIn(target, docs_readme, f"docs/README.md missing link: {target}")

    def test_status_and_changelog_document_0_3_12_pr1_through_pr4(self):
        status = (REPO / "docs/STATUS.md").read_text(encoding="utf-8")
        changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
        for doc_name, text in (("docs/STATUS.md", status), ("CHANGELOG.md", changelog)):
            for token in ("0.3.12", "oway sync", "oway-uix", "LeadQADelivery"):
                self.assertIn(token, text, f"{doc_name} missing {token}")
        self.assertIn("48", status)
        self.assertIn("0.3.9", changelog)
        self.assertIn("0.3.10", changelog)
        self.assertIn("0.3.11", changelog)


class DeliveryCiWatchDocsTests(unittest.TestCase):
    """P5-02: LeadQADelivery and QADelivery non-polling CI watch rule."""

    def test_delivery_role_cards_codify_gh_pr_checks_watch_and_ban_polling_loops(self):
        for rel in ("docs/oway/roles/qa/leadqadelivery.md", "docs/oway/roles/qa/qadelivery.md"):
            text = (REPO / rel).read_text(encoding="utf-8")
            low = text.lower()
            self.assertIn("gh pr checks", text, f"{rel} must document gh pr checks")
            self.assertIn("--watch", text, f"{rel} must document --watch")
            self.assertIn("poll", low, f"{rel} must forbid polling CI in a loop")
            self.assertIn("loop", low, f"{rel} must explicitly forbid polling loops")


class DisposableConsumerE2ETests(unittest.TestCase):
    """P5-03: Full disposable-consumer E2E lifecycle via synced ~/.local/bin/oway."""

    def _run_platform_and_sync(self, home: Path, env: dict[str, str]) -> Path:
        r = _run([sys.executable, str(OWAY_MOD), "platform", "init", "--dir", str(home / ".oway")],
                 home, env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        profile = home / ".oway/profile.md"
        profile.write_text(profile.read_text(encoding="utf-8").replace("approved: no", "approved: yes"),
                           encoding="utf-8")

        sync_args = ["--tools", ALL_TOOLS, "--oway-skills", "--oway-agents", "--home", str(home)]
        dry = _run([sys.executable, str(OWAY_MOD), "sync", "--dry-run", *sync_args], home, env)
        self.assertEqual(dry.returncode, 0, dry.stdout + dry.stderr)
        self.assertEqual([p.name for p in home.iterdir()], [".oway"], "dry-run wrote outside .oway")

        applied = _run([sys.executable, str(OWAY_MOD), "sync", *sync_args], home, env)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        chk = _run([sys.executable, str(OWAY_MOD), "sync", "--check", *sync_args], home, env)
        self.assertEqual(chk.returncode, 0, chk.stdout + chk.stderr)

        oway_bin = home / ".local/bin/oway"
        self.assertTrue(oway_bin.is_symlink(), "synced ~/.local/bin/oway must exist")
        return oway_bin

    def _run_setup_and_freeze(self, root: Path, oway_bin: Path, env: dict[str, str]) -> None:
        ow = lambda *a, e=env, s=None: _run([str(oway_bin), "--root", str(root), *a], root, e, stdin=s)
        for args in (("setup", "--language", "en", "--builder", "DevBackend", "--claude-hook"),
                     ("doctor",), ("index", "--check")):
            res = ow(*args)
            self.assertEqual(res.returncode, 0, f"{args}: {res.stdout}{res.stderr}")

        _stage_slice_files(root)
        for args in (("index",), ("index", "--check"), ("doctor",)):
            res = ow(*args)
            self.assertEqual(res.returncode, 0, f"{args}: {res.stdout}{res.stderr}")

        git(root, "init", "-q")
        git(root, "add", "-A")
        git(root, "commit", "-qm", "init slice")
        for args in (("headers",), ("headers", "--check")):
            res = ow(*args)
            self.assertEqual(res.returncode, 0, f"{args}: {res.stdout}{res.stderr}")
        git(root, "add", "-A")
        git(root, "commit", "-qm", "git headers")

        bad_freeze = ow("freeze", "s001", e={**env, "OWAY_ROLE": "DevBackend"})
        self.assertEqual(bad_freeze.returncode, 2, bad_freeze.stdout + bad_freeze.stderr)
        ok_freeze = ow("freeze", "s001", e={**env, "OWAY_ROLE": "proof-matrix-author"})
        self.assertEqual(ok_freeze.returncode, 0, ok_freeze.stdout + ok_freeze.stderr)
        git(root, "add", "-A")
        git(root, "commit", "-qm", "freeze s001")

    def _run_guard_proof_and_keeper(self, root: Path, oway_bin: Path, env: dict[str, str]) -> None:
        ow = lambda *a, s=None: _run([str(oway_bin), "--root", str(root), *a], root, env, stdin=s)
        for blocked_rel in ("_oway/slices/s001.matrix.md", "README.md"):
            payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(root / blocked_rel)}})
            out = json.loads(ow("guard", s=payload).stdout)["hookSpecificOutput"]
            self.assertEqual(out["permissionDecision"], "deny", blocked_rel)
        ok_payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(root / "src/app.py")}})
        self.assertEqual(ow("guard", s=ok_payload).stdout, "")

        stop_open = json.loads(ow("stop-hook", s="{}").stdout)
        self.assertEqual(stop_open["decision"], "block")
        self.assertIn("OPEN", stop_open["reason"])

        fail_p1 = ow("submit", "s001", "P1")
        self.assertEqual(fail_p1.returncode, 1, fail_p1.stdout + fail_p1.stderr)
        (root / "src/app.py").write_text(APP_TMPL.format(msg=f"hello {CANARY}"), encoding="utf-8")
        git(root, "add", "src/app.py")
        git(root, "commit", "-qm", "add canary")

        pass_p1 = ow("submit", "s001", "P1")
        self.assertEqual(pass_p1.returncode, 0, pass_p1.stdout + pass_p1.stderr)
        self.assertIn("P1 NEEDS_REVIEW", ow("check", "s001").stdout)
        self.assertEqual(json.loads(ow("stop-hook", s="{}").stdout)["decision"], "block")

        rev_p1 = ow("review", "s001", "P1")
        self.assertEqual(rev_p1.returncode, 0, rev_p1.stdout + rev_p1.stderr)
        self.assertIn("PASS", rev_p1.stdout)
        self.assertEqual(ow("submit", "s001", "P2").returncode, 0)
        self.assertEqual(ow("check", "s001", "--head").returncode, 0)

        stop_done = ow("stop-hook", s="{}")
        self.assertEqual(stop_done.returncode, 0, stop_done.stderr)
        self.assertEqual(stop_done.stdout, "")

        for args in (("keeper", "wake", "dev"), ("keeper", "scan"), ("keeper", "status"),
                     ("keeper", "sleep", "dev"), ("index",), ("doctor",), ("index", "--check")):
            res = ow(*args)
            self.assertEqual(res.returncode, 0, f"{args}: {res.stdout}{res.stderr}")

    def test_full_disposable_consumer_lifecycle(self):
        with TempDir() as home, TempDir() as project:
            env = _clean_env(home)
            oway_bin = self._run_platform_and_sync(home, env)
            self._run_setup_and_freeze(project, oway_bin, env)
            self._run_guard_proof_and_keeper(project, oway_bin, env)


if __name__ == "__main__":
    unittest.main()
