"""The proof loop: frozen matrix, `oway submit`, `oway check`, evidence chain.

A matrix is `_oway/slices/<slice>.matrix.md`: a header and one Markdown table
(id, Interaction, Accepted proof, Medium, Verifier commands, Canary, State).
Only this module writes evidence, and an item's state comes from the evidence
chain, never from what an agent typed in the State column.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import headers, ledger
from .project import OwayError, git_head

MAX_ROUNDS = 3
OUTPUT_KEEP = 4000
GENESIS = "0" * 64
# Signs of staged proof in verifier output (proof-loop.md section 3).
FAKE_SIGNS = re.compile(r"\?mock=|route\.fulfill|\bMOCK_DATA\b|\bstaged\b screenshot", re.I)
COLUMNS = ("id", "interaction", "accepted proof", "medium", "verifier commands", "canary")


@dataclass
class Item:
    id: str
    interaction: str
    proof: str
    medium: str
    command: str
    canary: str


def matrix_path(oway: Path, slice_id: str) -> Path:
    return oway / "slices" / f"{slice_id}.matrix.md"


def evidence_path(oway: Path, slice_id: str) -> Path:
    return oway / "evidence" / f"{slice_id}.jsonl"


def _cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def parse_matrix(text: str) -> list[Item]:
    rows = [l for l in text.splitlines() if l.strip().startswith("|")]
    if len(rows) < 2:
        raise OwayError("matrix has no table")
    head = [c.lower() for c in _cells(rows[0])]
    missing = [c for c in COLUMNS if c not in head]
    if missing:
        raise OwayError(f"matrix table misses columns: {', '.join(missing)}")
    col = {name: head.index(name) for name in COLUMNS}
    items: list[Item] = []
    for line in rows[2:]:
        c = _cells(line)
        if len(c) < len(head):
            raise OwayError(f"matrix row has too few cells: {line.strip()}")
        cmd = c[col["verifier commands"]].strip()
        if cmd.startswith("`") and cmd.endswith("`"):
            cmd = cmd[1:-1]
        cmd = cmd.replace("\\|", "|")
        items.append(Item(c[col["id"]], c[col["interaction"]], c[col["accepted proof"]],
                          c[col["medium"]], cmd, c[col["canary"]].strip("` ")))
    ids = [i.id for i in items]
    if len(set(ids)) != len(ids):
        raise OwayError("matrix item ids are not unique")
    if not items:
        raise OwayError("matrix has no items")
    return items


def matrix_hash(items: list[Item]) -> str:
    """Hash of everything but the State column, so the state can never unfreeze it."""
    data = [[i.id, i.interaction, i.proof, i.medium, i.command, i.canary] for i in items]
    return hashlib.sha256(json.dumps(data, ensure_ascii=False).encode()).hexdigest()


def needs_review(item: Item) -> bool:
    """Visual proof (video, screenshot) needs the reviewer on top of the verifier."""
    return bool(re.search(r"video|screenshot", item.medium, re.I))


def frozen_digest(root: Path, h: dict[str, str], items: list[Item]) -> str:
    """Matrix hash plus the content of every verifier file named in `verifiers:`.

    So a worker can change neither the items nor the scripts that check them.
    """
    parts = [matrix_hash(items)]
    for name in [v.strip() for v in h.get("verifiers", "").split(",") if v.strip()]:
        path = (root / name).resolve()
        if not path.is_file() or root.resolve() not in path.parents:
            raise OwayError(f"verifier file '{name}' is missing or outside the project")
        parts.append(name + ":" + hashlib.sha256(path.read_bytes()).hexdigest())
    if len(parts) == 1:
        return parts[0]
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def load(oway: Path, slice_id: str) -> tuple[dict[str, str], list[Item]]:
    path = matrix_path(oway, slice_id)
    if not path.exists():
        raise OwayError(f"no matrix for slice {slice_id} ({path.name})")
    text = path.read_text(encoding="utf-8")
    h = headers.parse(text) or {}
    return h, parse_matrix(text)


FREEZE_ROLES = ("proof-matrix-author", "devproof", "lead")


def _norm_reason(text: str) -> str:
    return " ".join((text or "").lower().split())


def freeze(oway: Path, slice_id: str, role: str | None = None) -> str:
    caller = (role if role is not None else os.environ.get("OWAY_ROLE", "")).strip()
    if caller and not caller.lower().startswith(FREEZE_ROLES):
        raise OwayError(
            f"role '{caller}' cannot freeze the proof matrix; only proof-matrix-author, DevProof, or a Lead may"
        )
    path = matrix_path(oway, slice_id)
    h, items = load(oway, slice_id)
    if h.get("state") == "frozen":
        raise OwayError(f"matrix of {slice_id} is already frozen")
    digest = frozen_digest(oway.parent, h, items)
    text = headers.set_fields(path.read_text(encoding="utf-8"),
                              {"state": "frozen", "frozen_hash": digest})
    path.write_text(text, encoding="utf-8")
    ledger.append(oway, f"matrix of {slice_id} frozen, {len(items)} items, hash {digest[:12]}")
    return digest


def _frozen_items(oway: Path, slice_id: str) -> tuple[str, list[Item]]:
    h, items = load(oway, slice_id)
    if h.get("state") != "frozen" or not h.get("frozen_hash"):
        raise OwayError(f"matrix of {slice_id} is not frozen; the owner approves it, then `oway freeze`")
    digest = frozen_digest(oway.parent, h, items)
    if digest != h["frozen_hash"]:
        raise TamperError(f"TAMPER: matrix or verifiers of {slice_id} changed after freezing "
                          f"({digest[:12]} != {h['frozen_hash'][:12]})")
    return digest, items


class TamperError(OwayError):
    pass


# ---- evidence chain -------------------------------------------------------

def _record_hash(rec: dict) -> str:
    body = {k: v for k, v in rec.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read_chain(oway: Path, slice_id: str) -> list[dict]:
    """All records, after checking the chain. Raises TamperError when it is broken."""
    path = evidence_path(oway, slice_id)
    if not path.exists():
        return []
    prev, out = GENESIS, []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            rec = json.loads(line)
        except ValueError:
            raise TamperError(f"TAMPER: evidence line {n} of {slice_id} is not JSON") from None
        if rec.get("prev") != prev or _record_hash(rec) != rec.get("hash"):
            raise TamperError(f"TAMPER: evidence chain of {slice_id} broken at line {n}")
        prev = rec["hash"]
        out.append(rec)
    return out


def _append(oway: Path, slice_id: str, rec: dict) -> dict:
    path = evidence_path(oway, slice_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        chain = read_chain(oway, slice_id)
        rec = {"seq": len(chain) + 1, "prev": chain[-1]["hash"] if chain else GENESIS, **rec}
        rec["hash"] = _record_hash(rec)
        fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    return rec


# ---- submit and check -----------------------------------------------------

def states(oway: Path, slice_id: str, digest: str, items: list[Item]) -> dict[str, dict]:
    """Per item: state (OPEN/PASS/NEEDS_REVIEW/FAIL/FAKE/INSUFFICIENT/BLOCKED), rounds, last, pivot."""
    out = {i.id: {"state": "OPEN", "rounds": 0, "last": None, "pivot_required": False, "last_fail_reason": None}
           for i in items}
    needs = {i.id for i in items if needs_review(i)}
    for rec in read_chain(oway, slice_id):
        if rec.get("matrix_hash") != digest or rec.get("item") not in out:
            continue  # evidence for an older matrix never counts
        s = out[rec["item"]]
        s["last"] = rec
        is_review = rec.get("kind") == "review"
        if is_review and s["state"] != "NEEDS_REVIEW":
            continue  # a review counts only right after a verifier PASS
        if rec["verdict"] == "PASS":
            if rec["item"] in needs and not is_review:
                s["state"] = "NEEDS_REVIEW"
            else:
                s["state"] = "PASS"
                s["pivot_required"] = False
                s["last_fail_reason"] = None
        elif rec["verdict"] == "UNREVIEWED":
            s["state"] = "NEEDS_REVIEW"
        else:
            s["rounds"] += 1
            reason_norm = _norm_reason(rec.get("reason", ""))
            same_defect = bool(reason_norm and s["last_fail_reason"] == reason_norm)
            s["last_fail_reason"] = reason_norm
            if s["rounds"] >= MAX_ROUNDS:
                s["state"] = "BLOCKED"
                s["pivot_required"] = False
            else:
                s["state"] = rec["verdict"]
                s["pivot_required"] = same_defect
    return out


def submit(root: Path, slice_id: str, item_id: str, timeout: int = 600) -> dict:
    oway = root / "_oway"
    digest, items = _frozen_items(oway, slice_id)
    item = next((i for i in items if i.id == item_id), None)
    if item is None:
        raise OwayError(f"no item {item_id} in the matrix of {slice_id}")
    current = states(oway, slice_id, digest, items)[item_id]
    if current["state"] == "BLOCKED":
        raise OwayError(f"{item_id} is BLOCKED after {current['rounds']} rounds; tell your lead")
    if not item.command or item.command.lower() in {"none", "-"}:
        raise OwayError(f"{item_id} has no verifier command; it needs a reviewer, not submit")
    env = dict(os.environ, OWAY_SLICE=slice_id, OWAY_ITEM=item_id)
    try:
        r = subprocess.run(item.command, shell=True, cwd=root, capture_output=True,
                           text=True, timeout=timeout, env=env)
        code, output = r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired as exc:
        code, output = 124, f"timeout after {timeout}s\n{exc.stdout or ''}"
    reasons = []
    from .guard import zone_breaks  # late import: guard reads proof
    reasons += zone_breaks(root)
    if code != 0:
        reasons.append(f"verifier exited {code}")
    canary = item.canary
    if canary and canary.lower() not in {"none", "-"} and canary not in output:
        reasons.append(f"canary '{canary}' not in the output")
    if FAKE_SIGNS.search(output):
        verdict = "FAKE"
        reasons.append("output shows staged or mocked proof")
    else:
        verdict = "FAIL" if reasons else "PASS"
    reason_text = "; ".join(reasons) or "verifier passed"
    pivot = (verdict != "PASS" and current["rounds"] + 1 < MAX_ROUNDS
             and bool(_norm_reason(reason_text))
             and _norm_reason(reason_text) == current.get("last_fail_reason"))
    payload = {
        "ts": ledger.now(), "slice": slice_id, "item": item_id, "matrix_hash": digest,
        "rev": git_head(root), "command": item.command, "exit": code,
        "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
        "output_tail": output[-OUTPUT_KEEP:], "verdict": verdict, "reason": reason_text,
    }
    if pivot:
        payload["pivot_required"] = True
    rec = _append(oway, slice_id, payload)
    if verdict != "PASS" and current["rounds"] + 1 >= MAX_ROUNDS:
        ledger.append(oway, f"{slice_id} {item_id} BLOCKED after {MAX_ROUNDS} rounds: {rec['reason']}")
    return rec


def check(root: Path, slice_id: str, require_head: bool = False) -> tuple[bool, list[str]]:
    """True when every item is PASS (at HEAD, with require_head). Lines for the report."""
    oway = root / "_oway"
    digest, items = _frozen_items(oway, slice_id)
    st = states(oway, slice_id, digest, items)
    head = git_head(root) if require_head else None
    ok, lines = True, []
    for i in items:
        s = st[i.id]
        state = s["state"]
        if state == "PASS" and require_head and s["last"]["rev"] != head:
            state = "STALE"
        if state != "PASS":
            ok = False
        pivot = " PIVOT_REQUIRED" if s.get("pivot_required") else ""
        why = f" ({s['last']['reason']})" if s["last"] and state != "PASS" else ""
        lines.append(f"{i.id} {state} rounds={s['rounds']}{pivot}{why}")
    return ok, lines
