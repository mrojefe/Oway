"""`oway headers`: fill `created` and `updated` in every header from Git.

An agent never types a date: `created` is the first commit that added the
file, `updated` the last commit that changed it (date and author). Files not
committed yet keep "not committed". With --check nothing is written and the
stale files are listed (for CI).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from . import headers
from .project import rel

NOT_COMMITTED = "not committed"


def _git(root: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def dates(root: Path, path: str) -> tuple[str, str]:
    log = _git(root, "log", "--follow", "--format=%cs %an", "--", path).splitlines()
    if not log:
        return NOT_COMMITTED, NOT_COMMITTED
    return log[-1].split(" ", 1)[0], f"{log[0].split(' ', 1)[0]} by {log[0].split(' ', 1)[1]}"


def run(root: Path, check: bool = False) -> list[str]:
    stale = []
    for f in sorted((root / "_oway").rglob("*.md")):
        name = rel(root, f)
        if f.name in headers.NO_HEADER or name.startswith(("_oway/keeper/", "_oway/evidence/")):
            continue
        text = f.read_text(encoding="utf-8")
        h = headers.parse(text)
        if h is None:
            continue
        created, updated = dates(root, name)
        if h.get("created") == created and h.get("updated") == updated:
            continue
        stale.append(name)
        if not check:
            f.write_text(headers.set_fields(text, {"created": created, "updated": updated}), encoding="utf-8")
    return stale
