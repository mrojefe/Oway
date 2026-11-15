"""`oway upgrade`: move a project to the tool's version, one change list at a time.

A change list is `upgrades/<from>-to-<to>.json`:
{"from": "0.3.5", "to": "0.3.6", "moves": [["old/path", "new/path"]], "notes": "..."}
Moves use `git mv` when the project is a Git repository, so history follows.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from . import index, ledger
from .project import OwayError

HERE = Path(__file__).resolve().parent


def _key(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def steps_dir() -> Path:
    return Path(os.environ.get("OWAY_UPGRADES", HERE / "upgrades"))


def plan(current: str, target: str) -> list[dict]:
    steps = {}
    folder = steps_dir()
    for f in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        s = json.loads(f.read_text(encoding="utf-8"))
        steps[s["from"]] = s
    out, v = [], current
    while _key(v) < _key(target):
        step = steps.get(v)
        if step is None:
            break  # no change list: nothing moves between these versions
        out.append(step)
        v = step["to"]
    return out


def _move(root: Path, old: str, new: str) -> None:
    src, dst = root / old, root / new
    if not src.exists():
        return
    if dst.exists():
        raise OwayError(f"cannot move {old}: {new} already exists")
    dst.parent.mkdir(parents=True, exist_ok=True)
    git = subprocess.run(["git", "mv", old, new], cwd=root, capture_output=True, text=True)
    if git.returncode != 0:
        src.rename(dst)


def run(root: Path, target: str, dry_run: bool = False) -> list[str]:
    cfg_path = root / "_oway" / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    current = cfg["oway_version"]
    if _key(current) > _key(target):
        raise OwayError(f"project is on {current}, newer than the tool ({target}); upgrade the tool")
    if current == target:
        return [f"already on {target}"]
    lines = []
    for step in plan(current, target):
        lines.append(f"{step['from']} -> {step['to']}: {step.get('notes', '')}".rstrip(": "))
        for old, new in step.get("moves", []):
            lines.append(f"  move {old} -> {new}")
            if not dry_run:
                _move(root, old, new)
    lines.append(f"version {current} -> {target}")
    if not dry_run:
        cfg["oway_version"] = target
        cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        ledger.append(root / "_oway", f"Oway upgrade {current} -> {target}")
        index.build(root / "_oway")
    return lines
