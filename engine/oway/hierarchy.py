"""Hierarchy checks for doctor: three-first-parts ordering and parent links."""
from __future__ import annotations

import re
from pathlib import Path

HEADING_H2 = re.compile(r"^##\s+(.+?)\s*$", re.M)
PART_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("The goal", re.compile(r"^(?:\d+\.\s*)?(?:the\s+|main\s+)?goal\b", re.I)),
    ("What you get", re.compile(r"^(?:\d+\.\s*)?what\s+you\s+get\b", re.I)),
    ("The proof you will have", re.compile(r"^(?:\d+\.\s*)?(?:the\s+)?proof\s+you\s+will\s+have\b", re.I)),
)
PARENT_TYPE: dict[str, str] = {
    "milestone": "project",
    "slice": "milestone",
    "matrix": "slice",
}


def check_three_parts(name: str, text: str, h: dict[str, str] | None) -> list[str]:
    """Validate Goal, What you get, and Proof you will have ordering on project/milestone/slice."""
    if not h or h.get("type") not in ("project", "milestone", "slice"):
        return []
    kind = h["type"]
    body = text.split("\n---\n", 1)[-1]
    headings = [m.group(1).strip() for m in HEADING_H2.finditer(body)]
    if h.get("updated") == "takeover from CGSpec 0.3":
        return []
    if kind == "project" and not headings and h.get("description", "").startswith("Taken over"):
        return []
    if kind == "slice" and not h.get("parent") and [x.lower() for x in headings] == ["walkthrough"]:
        return []
    positions: list[int] = []
    missing: list[str] = []
    for label, pat in PART_PATTERNS:
        idx = next((i for i, hd in enumerate(headings) if pat.match(hd)), None)
        if idx is None:
            missing.append(label)
        else:
            positions.append(idx)
    out = [f"{name}: missing required section '{label}'" for label in missing]
    if not missing and not (positions[0] < positions[1] < positions[2]):
        out.append(f"{name}: three first parts out of order (expected Goal -> What you get -> Proof you will have)")
    return out


def _doc_keys(path: Path, oway: Path, h: dict[str, str]) -> set[str]:
    rel_oway = path.relative_to(oway).as_posix()
    keys = {path.stem, path.name, rel_oway}
    if h.get("name"):
        keys.add(h["name"])
    return {k.lower() for k in keys}


def check_parents(docs: list[tuple[str, Path, dict[str, str]]], oway: Path) -> list[str]:
    """Validate parent: links for milestone -> project, slice -> milestone, matrix -> slice."""
    by_type: dict[str, set[str]] = {}
    for _, path, h in docs:
        kind = h.get("type", "")
        if kind:
            by_type.setdefault(kind, set()).update(_doc_keys(path, oway, h))
    out: list[str] = []
    for name, _, h in docs:
        kind = h.get("type", "")
        parent = (h.get("parent") or "").strip()
        expected = PARENT_TYPE.get(kind)
        if not expected or not parent:
            continue
        if kind == "matrix" and "slice" not in by_type:
            continue
        candidates = by_type.get(expected, set())
        if parent.lower() not in candidates:
            out.append(f"{name}: broken parent '{parent}' (no matching {expected})")
    return out
