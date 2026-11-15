"""LEDGER.md: append-only log of decisions and events, one line each."""
from __future__ import annotations

import fcntl
import re
from datetime import datetime, timezone
from pathlib import Path

HEAD = "# Ledger\nAppend-only. Written by `oway ledger`, never edited by hand.\n\n"
LINE = re.compile(r"^- (L-\d{8}-\d{3}) ")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(oway: Path, text: str, who: str = "oway") -> str:
    """Append one line and return its id (L-YYYYMMDD-NNN)."""
    text = " ".join(text.split())
    if not text:
        raise ValueError("empty ledger line")
    path = oway / "LEDGER.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        body = fh.read()
        if not body:
            fh.write(HEAD)
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        n = sum(1 for line in body.splitlines()
                if (m := LINE.match(line)) and m.group(1)[2:10] == day)
        lid = f"L-{day}-{n + 1:03d}"
        fh.write(f"- {lid} {now()} {who}: {text}\n")
    return lid
