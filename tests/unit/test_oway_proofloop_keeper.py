"""PR 3 Proof Loop, Hierarchy, Guard, Keeper Replay, and Git Authority tests (P3-01..P3-10)."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

from tests.helpers import REPO, TempDir, git, run_script, snapshot_tree

from oway import doctor, guard, index, keeper, proof, review, setup, stophook  # noqa: E402
from oway.project import OwayError

MATRIX_TMPL = """---
name: s001-matrix
description: Proof matrix of s001
type: matrix
parent: s001-hello
state: draft
approved: yes
owner: proof-matrix-author
verifiers: qa/verify_hello.sh
---

# S001 proof matrix

| id | Interaction | Accepted proof | Medium | Verifier commands | Canary | State |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Run app and verify | Proof has canary | {medium} | `sh qa/verify_hello.sh` | {canary} | OPEN |
| P2 | App prints version | Output has version | command record | `python3 app.py --version` | none | OPEN |
"""
ANSWER_PY = "import sys; sys.stdin.read(); print({!r})\n"


def _oway(root: Path, *args: str, stdin: str | None = None, env: dict | None = None):
    return run_script("oway", "--root", str(root), *args, stdin=stdin, env=env)


def _cp(oway: Path, data: dict) -> None:
    (oway / "state" / "checkpoint.json").write_text(json.dumps(data), encoding="utf-8")


def _init_project(
    root: Path,
    visual: bool = False,
    canary: str = "mango-4921",
    role: str = "DevBackend",
    freeze: bool = True,
    app_body: str = "print('hello')\n",
) -> Path:
    setup.project_setup(root, "en", ["DevBackend"], uix=True, platform=root / "no-platform")
    oway = root / "_oway"
    (root / "qa").mkdir(exist_ok=True)
    (root / "qa" / "verify_hello.sh").write_text("#!/bin/sh\npython3 app.py\n", encoding="utf-8")
    (oway / "slices").mkdir(exist_ok=True)
    medium = "screenshot + live output" if visual else "command record"
    (oway / "slices" / "s001.matrix.md").write_text(MATRIX_TMPL.format(medium=medium, canary=canary), encoding="utf-8")
    (oway / "state").mkdir(exist_ok=True)
    _cp(oway, {"slice": "s001", "role": role, "zone": ["src/**", "app.py"]})
    (root / "app.py").write_text(
        "import sys\nif '--version' in sys.argv:\n    print('1.0.0')\n    raise SystemExit\n" + app_body,
        encoding="utf-8",
    )
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "init")
    if freeze:
        proof.freeze(oway, "s001", role="proof-matrix-author")
    return oway


def _set_reviewer(root: Path, payload: str) -> None:
    script = root / "qa" / "reviewer.py"
    script.write_text(ANSWER_PY.format(payload), encoding="utf-8")
    git(root, "add", "qa/reviewer.py")
    git(root, "commit", "-qm", "configure reviewer")
    cfg_path = root / "_oway" / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["reviewer_command"] = f"{sys.executable} {script}"
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def _doc(path: Path, name: str, kind: str, parent: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nname: {name}\ndescription: {name}\ntype: {kind}\nstate: draft\nparent: {parent}\n---\n\n{body}\n",
        encoding="utf-8",
    )


class HierarchyDoctorTests(unittest.TestCase):
    """P3-01: Hierarchy templates & doctor.py three-first-parts + parent-link checks."""

    def test_project_and_proof_templates_conform(self):
        proj = (REPO / "docs/oway/templates/project.md").read_text(encoding="utf-8")
        self.assertNotIn("in-progress", proj)
        self.assertIn("draft / approved / done", proj)
        mat = (REPO / "docs/oway/templates/proof-item.md").read_text(encoding="utf-8")
        self.assertIn("verifiers:", mat)
        self.assertIn("INSUFFICIENT", mat)
        self.assertNotIn("SUBMITTED", mat)
        self.assertIn("owner: proof-matrix-author", mat)

    def test_doctor_validates_three_first_parts_and_parent_links(self):
        good = "# Doc\n\n## 1. The goal\nGoal.\n\n## 2. What you get\nOut.\n\n## 3. The proof you will have\nLive."
        with TempDir() as root:
            oway = _init_project(root, freeze=False)
            m01, s001 = oway / "milestones" / "m01.md", oway / "slices" / "s001-hello.md"
            _doc(m01, "m01", "milestone", "project", good)
            _doc(s001, "s001-hello", "slice", "m01", good)
            index.build(oway)
            self.assertEqual(doctor.run(root), [])

            _doc(m01, "m01", "milestone", "project", "# M01\n\n## 1. The goal\nG.\n\n## 2. What you get\nOut.")
            self.assertIn("proof you will have", "\n".join(doctor.run(root)).lower())

            _doc(s001, "s001-hello", "slice", "m01",
                 "# S1\n\n## 2. What you get\nO.\n\n## 1. The goal\nG.\n\n## 3. The proof you will have\nP.")
            self.assertIn("order", "\n".join(doctor.run(root)).lower())

            _doc(s001, "s001-hello", "slice", "m99-missing", good)
            self.assertIn("m99-missing", "\n".join(doctor.run(root)))


class GuardEnforcementTests(unittest.TestCase):
    """P3-02: Separate-agent proof matrix & _oway/state/* guard."""

    def test_state_denied_for_workers_and_evidence_frozen_denied_for_all(self):
        with TempDir() as root:
            oway = _init_project(root, freeze=False)
            for role in ("proof-matrix-author", "DevProof"):
                _cp(oway, {"slice": "s001", "role": role})
                self.assertIsNone(guard.reason(root, "_oway/slices/s001.matrix.md"))
                self.assertIsNone(guard.reason(root, "qa/verify_hello.sh"))

            _cp(oway, {"slice": "s001", "role": "DevBackend", "zone": ["src/**"]})
            self.assertIsNotNone(guard.reason(root, "_oway/state/checkpoint.json"))
            self.assertIsNotNone(guard.reason(root, "_oway/state/stop-hook.json"))

            proof.freeze(oway, "s001", role="proof-matrix-author")
            for role in ("DevBackend", "DevProof", "proof-matrix-author", "LeadDev", "LeadQA"):
                _cp(oway, {"slice": "s001", "role": role})
                self.assertIsNotNone(guard.reason(root, "_oway/evidence/s001.jsonl"), role)
                self.assertIsNotNone(guard.reason(root, "_oway/slices/s001.matrix.md"), role)


class FreezeRoleTests(unittest.TestCase):
    """P3-03: proof.freeze() role enforcement."""

    def test_builder_roles_cannot_freeze(self):
        for bad in ("DevBackend", "DevFrontend", "DevData", "DevAI", "DevMobile", "UIXDesign", "UIXCopy"):
            with TempDir() as root:
                oway = _init_project(root, freeze=False)
                with self.assertRaises(OwayError, msg=bad):
                    proof.freeze(oway, "s001", role=bad)

    def test_authorized_and_unset_roles_can_freeze(self):
        for ok in ("proof-matrix-author", "DevProof", "LeadDev", "LeadQA", "LeadOway", ""):
            with TempDir() as root:
                oway = _init_project(root, freeze=False)
                self.assertEqual(len(proof.freeze(oway, "s001", role=ok)), 64)

    def test_cli_respects_oway_role_env(self):
        with TempDir() as root:
            _init_project(root, freeze=False)
            r = _oway(root, "freeze", "s001", env=dict(os.environ, OWAY_ROLE="DevBackend"))
            self.assertEqual(r.returncode, 2)
            self.assertIn("cannot freeze", r.stderr.lower())


class StopHookStateTests(unittest.TestCase):
    """P3-04: Stop hook blocks INSUFFICIENT and NEEDS_REVIEW."""

    def test_blocks_needs_review_and_insufficient_allows_pass_and_blocked(self):
        with TempDir() as root:
            _init_project(root, visual=True, app_body="print('hello mango-4921')\n")
            _set_reviewer(root, '{"verdict":"INSUFFICIENT","reason":"missing mobile","evidence_ids":[1]}')
            proof.submit(root, "s001", "P1")
            proof.submit(root, "s001", "P2")

            may_stop, msg = stophook.decide(root)
            self.assertFalse(may_stop)
            self.assertIn("NEEDS_REVIEW", msg)
            self.assertNotIn("all items PASS", msg)

            review.run(root, "s001", "P1")
            may_stop, msg = stophook.decide(root)
            self.assertFalse(may_stop)
            self.assertIn("INSUFFICIENT", msg)
            self.assertNotIn("all items PASS", msg)

            for n in (2, 3):
                sub = proof.submit(root, "s001", "P1")
                _set_reviewer(root, f'{{"verdict":"INSUFFICIENT","reason":"missing {n}","evidence_ids":[{sub["seq"]}]}}')
                review.run(root, "s001", "P1")
            may_stop, msg = stophook.decide(root)
            self.assertTrue(may_stop)
            self.assertIn("BLOCKED", msg)


class SameDefectPivotTests(unittest.TestCase):
    """P3-05: 2-failure same-defect pivot (proof.py + stophook.py)."""

    def test_two_identical_failures_trigger_pivot_required(self):
        with TempDir() as root:
            oway = _init_project(root)
            self.assertFalse(proof.submit(root, "s001", "P1").get("pivot_required", False))
            self.assertTrue(proof.submit(root, "s001", "P1").get("pivot_required", False))
            digest, items = proof._frozen_items(oway, "s001")
            st = proof.states(oway, "s001", digest, items)["P1"]
            self.assertTrue(st.get("pivot_required", False))
            self.assertEqual(st["state"], "FAIL")
            may_stop, msg = stophook.decide(root)
            self.assertFalse(may_stop)
            self.assertIn("PIVOT_REQUIRED", msg)

    def test_two_identical_reviewer_rejections_trigger_pivot_required(self):
        with TempDir() as root:
            oway = _init_project(root, visual=True, app_body="print('hello mango-4921')\n")
            for _ in range(2):
                sub = proof.submit(root, "s001", "P1")
                _set_reviewer(root, f'{{"verdict":"INSUFFICIENT","reason":"clipped button","evidence_ids":[{sub["seq"]}]}}')
                review.run(root, "s001", "P1")
            digest, items = proof._frozen_items(oway, "s001")
            st = proof.states(oway, "s001", digest, items)["P1"]
            self.assertTrue(st.get("pivot_required", False))
            self.assertEqual(st["state"], "INSUFFICIENT")
            may_stop, msg = stophook.decide(root)
            self.assertFalse(may_stop)
            self.assertIn("PIVOT_REQUIRED", msg)

    def test_distinct_failure_reasons_do_not_trigger_pivot(self):
        with TempDir() as root:
            _init_project(root)
            proof.submit(root, "s001", "P1")
            (root / "app.py").write_text("import sys; sys.exit(2)\n", encoding="utf-8")
            self.assertFalse(proof.submit(root, "s001", "P1").get("pivot_required", False))
            may_stop, msg = stophook.decide(root)
            self.assertFalse(may_stop)
            self.assertNotIn("PIVOT_REQUIRED", msg)


class ReviewerHardeningTests(unittest.TestCase):
    """P3-06: Reviewer evidence_ids validation & round-3 BLOCKED ledger append."""

    def test_missing_or_wrong_evidence_id_records_unreviewed(self):
        with TempDir() as root:
            _init_project(root, visual=True, app_body="print('hello mango-4921')\n")
            _set_reviewer(root, '{"verdict":"PASS","reason":"looks ok","evidence_ids":[999]}')
            proof.submit(root, "s001", "P1")
            self.assertEqual(review.run(root, "s001", "P1")["verdict"], "UNREVIEWED")
            ok, lines = proof.check(root, "s001")
            self.assertFalse(ok)
            self.assertIn("P1 NEEDS_REVIEW", "\n".join(lines))

    def test_round_3_review_failure_appends_blocked_to_ledger(self):
        with TempDir() as root:
            oway = _init_project(root, visual=True, app_body="print('hello mango-4921')\n")
            for n in range(1, 4):
                sub = proof.submit(root, "s001", "P1")
                _set_reviewer(root, f'{{"verdict":"INSUFFICIENT","reason":"defect {n}","evidence_ids":[{sub["seq"]}]}}')
                review.run(root, "s001", "P1")
            text = (oway / "LEDGER.md").read_text(encoding="utf-8")
            self.assertIn("BLOCKED", text)
            self.assertIn("s001 P1", text)


class KeeperReplayTests(unittest.TestCase):
    """P3-07: LeadKeeper proof replay & neutral [KEEPER] warning."""

    def test_unconfirmed_proof_is_rejected_without_keeper_warning(self):
        with TempDir() as root:
            oway = _init_project(root)
            keeper.wake(oway, "dev")
            fid, _ = keeper.note(oway, "dev", "DRIFT", "missing file claim", "_oway/slices/nonexistent.md")
            ok, msg = keeper.replay(oway, fid)
            self.assertFalse(ok)
            self.assertIn("REJECTED", msg)
            self.assertNotIn("[KEEPER]", msg)
            self.assertEqual(next(f for f in keeper.findings(oway) if f["id"] == fid)["state"], "rejected")

            fid2, _ = keeper.note(oway, "dev", "LOOP", "failing cmd", "python3 -c 'import sys; sys.exit(1)'")
            r = _oway(root, "keeper", "replay", fid2)
            self.assertEqual(r.returncode, 1)
            self.assertIn("REJECTED", r.stdout)
            self.assertNotIn("[KEEPER]", r.stdout)

    def test_confirmed_proof_emits_neutral_keeper_warning_api_and_cli(self):
        with TempDir() as root:
            oway = _init_project(root)
            keeper.wake(oway, "dev")
            fid, _ = keeper.note(oway, "dev", "PACE", "ledger exists", "_oway/LEDGER.md")
            ok, msg = keeper.replay(oway, fid)
            self.assertTrue(ok)
            self.assertRegex(msg, r"^\[KEEPER\] PACE \| ledger exists \| PROOF: _oway/LEDGER\.md \| SINCE: \S+$")

            fid2, _ = keeper.note(oway, "dev", "PACE", "cmd passes", "python3 -c 'print(1)'")
            r = _oway(root, "keeper", "verify", fid2)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertRegex(r.stdout.strip(), r"^\[KEEPER\] PACE \| cmd passes \| PROOF: .* \| SINCE: \S+$")


class KeeperScanAndFocusTests(unittest.TestCase):
    """P3-08: Keeper work-class DRIFT, FAKE_PROOF / pivot scan(), and read-only invariant."""

    def test_work_class_drift_and_pivot_scan(self):
        with TempDir() as root:
            oway = _init_project(root)
            keeper.wake(oway, "dev")
            for wc in ("SIDE", "HARDENING"):
                _cp(oway, {"slice": "s001", "role": "DevBackend", "work_class": wc, "approved": False})
                keeper.scan(oway)
            drift_facts = "\n".join(f["fact"] for f in keeper.findings(oway) if f["type"] == "DRIFT")
            self.assertIn("SIDE", drift_facts)
            self.assertIn("HARDENING", drift_facts)

            _cp(oway, {"slice": "s001", "role": "DevBackend", "work_class": "MAIN"})
            proof.submit(root, "s001", "P1")
            proof.submit(root, "s001", "P1")
            keeper.scan(oway)
            loops = "\n".join(f["fact"] for f in keeper.findings(oway) if f["type"] == "LOOP")
            self.assertIn("PIVOT_REQUIRED", loops)

    def test_fake_proof_scan_and_readonly_invariant(self):
        with TempDir() as root:
            oway = _init_project(root, app_body="print('hello mango-4921 from /?mock=1')\n")
            proof.submit(root, "s001", "P1")
            before = snapshot_tree(root)
            keeper.wake(oway, "dev")
            self.assertTrue(keeper.scan(oway))
            fid = next(f["id"] for f in keeper.findings(oway) if f["type"] == "FAKE_PROOF")
            ok, msg = keeper.replay(oway, fid)
            self.assertTrue(ok, msg)
            self.assertIn("[KEEPER] FAKE_PROOF", msg)
            keeper.report(oway)
            after = snapshot_tree(root)
            changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
            self.assertTrue(changed)
            self.assertTrue(all(p.startswith("_oway/keeper/") for p in changed), changed)


class GitAuthorityDocsTests(unittest.TestCase):
    """P3-09: LeadQADelivery Git authority role docs."""

    def test_role_cards_encode_leadqadelivery_git_authority_and_escalation(self):
        cards = {p.stem: (REPO / p).read_text(encoding="utf-8") for p in (
            Path("docs/oway/roles/qa/leadqadelivery.md"), Path("docs/oway/roles/qa/qadelivery.md"),
            Path("docs/oway/roles/qa/leadqa.md"), Path("docs/oway/roles/dev/leaddev.md"),
        )}
        for name, text in cards.items():
            for token in ("LeadQADelivery", "QADelivery", "LeadQATester", "LeadQADelivery -> LeadQA -> Owner", "main"):
                self.assertIn(token, text, f"{name} missing {token}")
        self.assertIn("sole Git", cards["leadqadelivery"])
        self.assertIn("sole Git", cards["leaddev"])


class VersionAndCanaryTests(unittest.TestCase):
    """P3-10 / P4-05: SemVer parity across all 4 manifests (read dynamically from engine/VERSION)."""

    def test_all_four_manifests_match_engine_version(self):
        version = (REPO / "engine/VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        for rel_path in ("plugin.json", ".claude-plugin/plugin.json"):
            self.assertEqual(json.loads((REPO / rel_path).read_text(encoding="utf-8"))["version"], version)
        mp = json.loads((REPO / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(mp["plugins"][0]["version"], version)


if __name__ == "__main__":
    unittest.main()
