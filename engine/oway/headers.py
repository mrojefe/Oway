"""File headers: the front matter at the top of every Oway Markdown file."""
from __future__ import annotations

import re
from pathlib import Path

# One list, mirrored from docs/oway/rules.md "Types and their states".
TYPES: dict[str, tuple[str, ...]] = {
    "project": ("draft", "approved", "done"),
    "milestone": ("draft", "approved", "in-progress", "done"),
    "slice": ("draft", "approved", "in-progress", "in-review", "done", "blocked"),
    "matrix": ("draft", "frozen"),
    "spine": ("draft", "approved", "superseded"),
    "research": ("draft", "done"),
    "design": ("draft", "locked", "superseded"),
    "decision": ("proposed", "accepted", "superseded"),
    "agent": ("draft", "approved"),
    "team": ("draft", "approved"),
    "rule": ("draft", "approved"),
    "profile": ("draft", "approved"),
    "feedback": ("draft", "sent"),
}
REQUIRED = ("name", "description", "type", "state")
# Files that never carry a header (logs and generated files).
NO_HEADER = {"INDEX.md", "LEDGER.md", "INBOX.md"}

_FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def parse(text: str) -> dict[str, str] | None:
    """Return the header as a flat dict, or None when there is none."""
    m = _FM.match(text)
    if not m:
        return None
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.split(" #", 1)[0].strip().strip('"').strip("'")
        out[key.strip()] = value
    return out


def read(path: Path) -> dict[str, str] | None:
    return parse(path.read_text(encoding="utf-8"))


def set_fields(text: str, fields: dict[str, str]) -> str:
    """Set or add header fields, keeping every other line as it is."""
    m = _FM.match(text)
    if not m:
        raise ValueError("file has no header")
    lines = m.group(1).splitlines()
    for key, value in fields.items():
        for i, line in enumerate(lines):
            if line.split(":", 1)[0].strip() == key:
                lines[i] = f"{key}: {value}"
                break
        else:
            lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(lines) + "\n---\n" + text[m.end():]


def problems(header: dict[str, str] | None) -> list[str]:
    if header is None:
        return ["no header"]
    out = [f"header misses '{k}'" for k in REQUIRED if not header.get(k)]
    kind = header.get("type", "")
    if kind and kind not in TYPES:
        out.append(f"unknown type '{kind}'")
    elif kind and header.get("state") and header["state"] not in TYPES[kind]:
        out.append(f"state '{header['state']}' is not allowed for type '{kind}' "
                   f"({', '.join(TYPES[kind])})")
    return out
