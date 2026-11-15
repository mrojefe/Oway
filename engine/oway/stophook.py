"""Builder stop hook: a worker cannot stop while an item of its slice is OPEN or FAIL.

Claude Code: a `Stop` hook running `python3 <engine>/oway stop-hook` prints
{"decision": "block", "reason": ...}. Other hosts (pi `agent_before_settle`,
Git hooks): `--format plain` exits 2 with the reason on stderr.
Only workers get this hook; a role starting with "Lead" is never blocked.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import ledger, proof
from .project import OwayError

# Blocks in a row with no new evidence before the hook lets go and logs it,
# so a stuck worker cannot burn tokens forever.
MAX_IDLE_BLOCKS = 5


def active_slice(oway: Path) -> tuple[str | None, str]:
    cp = oway / "state" / "checkpoint.json"
    data = {}
    if cp.exists():
        try:
            data = json.loads(cp.read_text(encoding="utf-8"))
        except ValueError:
            data = {}
    return (os.environ.get("OWAY_SLICE") or data.get("slice"),
            os.environ.get("OWAY_ROLE") or data.get("role", ""))


def decide(root: Path) -> tuple[bool, str]:
    """(may_stop, reason)."""
    oway = root / "_oway"
    slice_id, role = active_slice(oway)
    if not slice_id:
        return True, "no active slice"
    if role.lower().startswith("lead"):
        return True, "leads are never blocked by this hook"
    try:
        digest, items = proof._frozen_items(oway, slice_id)
        st = proof.states(oway, slice_id, digest, items)
        chain_len = len(proof.read_chain(oway, slice_id))
    except proof.TamperError as exc:
        return False, f"{exc}. Restore the frozen matrix and verifiers; the keeper is told."
    except OwayError as exc:
        return True, f"hook not active: {exc}"
    todo = [(i, s) for i, s in st.items() if s["state"] in {"OPEN", "FAIL", "FAKE"}]
    blocked = [i for i, s in st.items() if s["state"] == "BLOCKED"]
    if not todo:
        return True, "all items PASS" if not blocked else f"BLOCKED items {', '.join(blocked)}: tell your lead"

    counter = oway / "state" / "stop-hook.json"
    seen = {}
    if counter.exists():
        try:
            seen = json.loads(counter.read_text(encoding="utf-8"))
        except ValueError:
            seen = {}
    idle = seen.get("idle", 0) + 1 if seen.get("slice") == slice_id and seen.get("chain") == chain_len else 1
    counter.parent.mkdir(parents=True, exist_ok=True)
    counter.write_text(json.dumps({"slice": slice_id, "chain": chain_len, "idle": idle}) + "\n",
                       encoding="utf-8")
    if idle > MAX_IDLE_BLOCKS:
        ledger.append(oway, f"{slice_id}: stop allowed after {MAX_IDLE_BLOCKS} blocks with no new "
                            f"evidence; open items {', '.join(i for i, _ in todo)}", who="stop-hook")
        return True, "stuck: stop allowed and logged for the lead"
    parts = []
    for i, s in todo:
        why = f": {s['last']['reason']}" if s["last"] else ""
        parts.append(f"{i} is {s['state']}{why}")
    return False, (f"Slice {slice_id} not done. " + "; ".join(parts) +
                   f". Fix it, then run `oway submit {slice_id} <item>`.")


def main(root: Path, stdin_text: str, fmt: str = "claude") -> tuple[int, str, str]:
    """Returns (exit code, stdout, stderr)."""
    try:
        json.loads(stdin_text) if stdin_text.strip() else {}
    except ValueError:
        pass  # the host's payload is not needed to decide
    may_stop, reason = decide(root)
    if may_stop:
        return 0, "", ""
    if fmt == "plain":
        return 2, "", reason + "\n"
    return 0, json.dumps({"decision": "block", "reason": reason}) + "\n", ""
