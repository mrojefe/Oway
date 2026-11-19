"""Builder write zones (docs/oway/proof-loop.md: matrix and verifiers outside the builder's write zone).

The active slice and the builder's zone come from `_oway/state/checkpoint.json`:
{"slice": "s012", "role": "DevBackend", "zone": ["src/api/**", "tests/api/**"]}
A builder may never write the matrix, the verifier files, evidence, keeper files
or anything outside its zone. Two layers: `oway guard` for the host's
pre-tool hook (Claude Code PreToolUse), and `zone_breaks` at `oway submit`,
which reads Git and so also catches shell writes outside the zone that the
hook cannot see (changes to the matrix or verifiers are caught by the frozen hash).
"""
from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path

from . import headers, proof
from .stophook import active_slice

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
PROTECTED = ("_oway/evidence/*", "_oway/keeper/*", "_oway/state/*", "_oway/slices/*.matrix.md", "_oway/LEDGER.md")
FREE_ROLES = ("lead", "devproof", "proof-matrix-author")


def _is_frozen_matrix(root: Path, path: str) -> bool:
    if not _match(path, ["_oway/slices/*.matrix.md"]):
        return False
    target = root / path
    return target.is_file() and (headers.read(target) or {}).get("state") == "frozen"


def _checkpoint(oway: Path) -> dict:
    cp = oway / "state" / "checkpoint.json"
    try:
        return json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
    except ValueError:
        return {}


def _match(path: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, g) or fnmatch.fnmatch(path, g.rstrip("*").rstrip("/") + "/*")
               for g in globs)


def reason(root: Path, path: str, check_protected: bool = True) -> str | None:
    """Why this role may not write `path` (relative to root), or None when it may."""
    if check_protected:
        if _match(path, ["_oway/evidence/*"]):
            return f"{path} is proof or Oway state; no role may write evidence directly (owner: the tool)"
        if _is_frozen_matrix(root, path):
            return f"{path} is proof or Oway state; an already-frozen matrix cannot be edited by any role"
    oway = root / "_oway"
    slice_id, role = active_slice(oway)
    if not slice_id or role.lower().startswith(FREE_ROLES):
        return None
    protected = list(PROTECTED)
    matrix = proof.matrix_path(oway, slice_id)
    if matrix.exists():
        h = headers.read(matrix) or {}
        protected += [v.strip() for v in h.get("verifiers", "").split(",") if v.strip()]
    if check_protected and _match(path, protected):
        return f"{path} is proof or Oway state; a builder never writes it (owner: proof-matrix-author or the tool)"
    zone = _checkpoint(oway).get("zone")
    if zone and not _match(path, zone):
        return f"{path} is outside your zone for {slice_id} ({', '.join(zone)})"
    return None


def pre_tool(root: Path, payload: str) -> str:
    """Claude Code PreToolUse: print a deny decision for a write outside the zone."""
    try:
        data = json.loads(payload) if payload.strip() else {}
    except ValueError:
        return ""
    if data.get("tool_name") not in WRITE_TOOLS:
        return ""
    target = (data.get("tool_input") or {}).get("file_path") or (data.get("tool_input") or {}).get("notebook_path")
    if not target:
        return ""
    p = Path(target)
    p = p if p.is_absolute() else root / p
    try:
        rel_path = p.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return ""  # outside the project: not Oway's to judge
    why = reason(root, rel_path)
    if not why:
        return ""
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": "deny",
                                              "permissionDecisionReason": why}}) + "\n"


def zone_breaks(root: Path) -> list[str]:
    """Changed files (staged, unstaged, untracked) that break the zone, from Git."""
    try:
        r = subprocess.run(["git", "status", "--porcelain", "-uall"], cwd=root,
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if r.returncode != 0:
        return []
    out = []
    for line in r.stdout.splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        if path.startswith("_oway/"):
            continue  # Oway's own files: the frozen hash and the evidence chain guard them
        why = reason(root, path, check_protected=False)
        if why:
            out.append(why)
    return out
