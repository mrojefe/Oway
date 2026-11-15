"""`oway takeover --from cgspec-0.3`: move a CGSpec 0.3 project into `_oway/`.

Follows docs/oway/takeover.md. The old engine, skills and hooks are never
touched here: they are removed by hand, in their own commit, only after
`oway doctor` passes. Every move uses `git mv` when it can.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from . import doctor, headers, index, ledger, setup
from .project import OwayError, rel
from .upgrade import _move

SPINES = {"01-INTENT.md": "01-intent.md", "02-OOUX.md": "02-objects.md",
          "03-EXPERIENCE.md": "03-experience.md", "04-ARCHITECTURE.md": "04-architecture.md",
          "05-DELIVERY.md": "05-delivery.md"}
FILE_MOVES = [("docs/00-INBOX.md", "_oway/INBOX.md")] + [
    (f"docs/spines/{a}", f"_oway/spines/{b}") for a, b in SPINES.items()]
DIR_MOVES = [("docs/adrs", "_oway/decisions"), ("docs/adr", "_oway/decisions"),
             ("docs/slices", "_oway/slices"), ("docs/_cgspec/02-research", "_oway/research"),
             ("docs/prototypes/_snapshots", "_oway/evidence/visual-baselines"),
             ("docs/prototypes/_vision/references", "_oway/design/references"),
             ("docs/prototypes/_vision/user-references", "_oway/design/references"),
             ("docs/_cgspec/03-councils", "_oway/boards")]
TYPE_BY_FOLDER = {"spines": "spine", "decisions": "decision", "slices": "slice",
                  "research": "research", "design": "design", "boards": "research"}
STATE_BY_TYPE = {"decision": "proposed"}
KEEP_OUT = (".gitkeep",)


def _files(root: Path, folder: str) -> list[Path]:
    base = root / folder
    return sorted(p for p in base.rglob("*") if p.is_file() and p.name not in KEEP_OUT) if base.is_dir() else []


VERSIONED = re.compile(r"^v(\d+)[-_.]")
VISION = "docs/prototypes/_vision"


def _design_versions(root: Path) -> list[tuple[str, str]]:
    """Prototypes and screenshots named vN-... go to design/versions/vN/; others wait for the owner."""
    out = []
    if (root / VISION / "README.md").exists():
        out.append((f"{VISION}/README.md", "_oway/design/README.md"))
    for sub, dest in (("html-prototypes", ""), ("screenshots", "screenshots/")):
        for f in _files(root, f"{VISION}/{sub}"):
            m = VERSIONED.match(f.name)
            if m:
                out.append((rel(root, f), f"_oway/design/versions/v{m.group(1)}/{dest}{f.name}"))
    return out


def plan(root: Path) -> list[tuple[str, str]]:
    moves = [(a, b) for a, b in FILE_MOVES if (root / a).exists()] + _design_versions(root)
    for old_dir, new_dir in DIR_MOVES:
        for f in _files(root, old_dir):
            sub = f.relative_to(root / old_dir).as_posix()
            moves.append((rel(root, f), f"{new_dir}/{sub}"))
    return moves


def unknown(root: Path, moves: list[tuple[str, str]]) -> list[str]:
    """Project files under docs/ that the table does not cover: they wait for the owner."""
    moved = {a for a, _ in moves} | {"docs/_memlog.md", "docs/00-INDEX.md", "docs/_cgspec/project.json"}
    out = []
    for f in _files(root, "docs"):
        r = rel(root, f)
        if r in moved or r.startswith("docs/_cgspec/"):
            continue
        out.append(r)
    return out


LINK = re.compile(r"(\]\()([^)\s#]+)((?:#[^)\s]*)?\))")


def _relink(root: Path, moves: list[tuple[str, str]]) -> list[str]:
    """Rewrite relative links that point to a moved file, in moved files and root Markdown files."""
    where = {(root / a).resolve(): (root / b).resolve() for a, b in moves}
    back = {v: k for k, v in where.items()}
    targets = [root / b for a, b in moves if b.endswith(".md")] + sorted(root.glob("*.md"))
    changed = []
    for f in targets:
        if not f.exists():
            continue
        old_parent = back.get(f.resolve(), f.resolve()).parent
        text = f.read_text(encoding="utf-8")

        def fix(m: re.Match) -> str:
            target = m.group(2)
            if re.match(r"[a-z]+:", target) or target.startswith("/"):
                return m.group(0)
            old_abs = (old_parent / target).resolve()
            new_abs = where.get(old_abs, old_abs if old_abs.exists() else None)
            if new_abs is None:
                return m.group(0)
            return m.group(1) + os.path.relpath(new_abs, f.resolve().parent).replace(os.sep, "/") + m.group(3)

        new = LINK.sub(fix, text)
        if new != text:
            f.write_text(new, encoding="utf-8")
            changed.append(rel(root, f))
    return changed


def _add_header(path: Path, kind: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if headers.parse(text) is not None:
        return False
    title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), path.stem)
    state = STATE_BY_TYPE.get(kind, "draft")
    head = (f"---\nname: {path.stem.lower()}\ndescription: {title.replace(':', ' -')}\ntype: {kind}\n"
            f"state: {state}\napproved: no\nupdated: takeover from CGSpec 0.3\n---\n\n")
    path.write_text(head + text, encoding="utf-8")
    return True


def _config(root: Path, language: str) -> dict:
    old = root / "docs" / "_cgspec" / "project.json"
    path_classes = setup.PATH_CLASSES
    if old.exists():
        data = json.loads(old.read_text(encoding="utf-8"))
        path_classes = {k: v for k, v in data.get("path_classes", {}).items() if isinstance(v, list)}
        path_classes.setdefault("code", ["src/**"])
    return {"schema": 1, "oway_version": setup.VERSION_FILE.read_text().strip(), "language": language,
            "teams": {"product": True, "uix": (root / "docs" / "prototypes").is_dir(),
                      "dev": {"builders": []}, "qa": True},
            "message_max_chars": 200, "profile": "not set",
            "setup_pending": list(setup.PENDING) + ["files listed as unknown in the takeover map"],
            "path_classes": path_classes}


def run(root: Path, language: str, dry_run: bool = False) -> list[str]:
    if not (root / "docs" / "_cgspec" / "project.json").exists():
        raise OwayError("no docs/_cgspec/project.json: this is not a CGSpec 0.3 project")
    if (root / "_oway").exists():
        raise OwayError("_oway/ already exists; the takeover ran before")
    moves = plan(root)
    left = unknown(root, moves)
    lines = [f"move {a} -> {b}" for a, b in moves] + [f"unknown {u} (waits for the owner)" for u in left]
    if dry_run:
        return lines
    oway = root / "_oway"
    oway.mkdir()
    (oway / "config.json").write_text(json.dumps(_config(root, language), indent=2) + "\n", encoding="utf-8")
    for a, b in moves:
        _move(root, a, b)
    lines += [f"links fixed in {c}" for c in _relink(root, moves)]
    memlog = root / "docs" / "_memlog.md"
    old_log = memlog.read_text(encoding="utf-8") if memlog.exists() else ""
    (oway / "LEDGER.md").write_text(ledger.HEAD + "## Before Oway\n\n" + old_log.strip() + "\n\n## Oway\n\n",
                                    encoding="utf-8")
    for f in sorted(oway.rglob("*.md")):
        parts = f.relative_to(oway).parts
        if len(parts) > 1 and parts[0] in TYPE_BY_FOLDER and f.name not in headers.NO_HEADER:
            if _add_header(f, TYPE_BY_FOLDER[parts[0]]):
                lines.append(f"header {rel(root, f)}")
    if not (oway / "project.md").exists():
        (oway / "project.md").write_text(
            "---\nname: project\ndescription: Taken over from CGSpec 0.3\ntype: project\nstate: draft\n"
            "approved: no\n---\n\n# Project\n\nSee the spines. Setup pending: see config.json.\n",
            encoding="utf-8")
    research = oway / "research"
    research.mkdir(exist_ok=True)
    (research / "RES-takeover-map.md").write_text(
        "---\nname: res-takeover-map\ndescription: CGSpec 0.3 to Oway takeover map\ntype: research\n"
        "state: done\n---\n\n# Takeover map\n\n" + "".join(f"- {l}\n" for l in lines), encoding="utf-8")
    ledger.append(oway, f"takeover from CGSpec 0.3: {len(moves)} files moved, {len(left)} unknown; "
                        "map in research/RES-takeover-map.md; old engine kept until oway doctor passes")
    index.build(oway)
    problems = doctor.run(root)
    lines.append(f"doctor: {len(problems)} problems" if problems else "doctor: ok")
    lines += [f"  {p}" for p in problems]
    return lines
