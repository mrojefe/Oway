"""oway doctor: check a project against the Oway rules that a script can check."""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import headers, hierarchy, index
from .project import rel

LINK = re.compile(r"\]\(([^)\s]+)\)")
ABSOLUTE_HOME = re.compile(r"(?<![\w/])(/home/|/Users/|[A-Z]:\\\\Users)")
BUILDERS = {"DevBackend", "DevFrontend", "DevData", "DevAI", "DevMobile"}
CONFIG_KEYS = {"schema", "oway_version", "language", "product_type", "teams", "keeper",
               "message_max_chars", "profile", "setup_pending", "path_classes", "legacy", "reviewer_command"}


def check_config(path: Path) -> list[str]:
    """A small, dependency-free subset of schemas/oway-config.schema.json."""
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"config.json is not valid JSON: {exc}"]
    out: list[str] = []
    if not isinstance(cfg, dict):
        return ["config.json must be an object"]
    for key in ("schema", "oway_version", "language", "teams", "path_classes"):
        if key not in cfg:
            out.append(f"config.json misses '{key}'")
    for key in sorted(set(cfg) - CONFIG_KEYS):
        out.append(f"config.json has unknown key '{key}'")
    if "oway_version" in cfg and not re.fullmatch(r"\d+\.\d+\.\d+", str(cfg["oway_version"])):
        out.append("config.json oway_version must be X.Y.Z")
    if "language" in cfg and not re.fullmatch(r"[a-z]{2}", str(cfg["language"])):
        out.append("config.json language must be a two-letter code, e.g. 'en' or 'fr'")
    mmc = cfg.get("message_max_chars", 200)
    if not isinstance(mmc, int) or not 0 <= mmc <= 200:
        out.append("config.json message_max_chars must be 0 to 200")
    teams = cfg.get("teams", {})
    if isinstance(teams, dict):
        for team in ("product", "dev", "qa"):
            if team not in teams:
                out.append(f"config.json teams misses '{team}'")
        builders = (teams.get("dev") or {}).get("builders", []) if isinstance(teams.get("dev"), dict) else []
        for b in builders:
            if b not in BUILDERS:
                out.append(f"config.json unknown Dev builder '{b}'")
    pc = cfg.get("path_classes", {})
    if isinstance(pc, dict) and "code" not in pc:
        out.append("config.json path_classes misses 'code'")
    return out


BARE_DOMAIN = re.compile(r"(?<![\w/.@(])(?:[a-z0-9-]+\.)+(?:com|ma|org|net|io|fr|gov|edu)\b(?![\w/])", re.I)


def content_rules(name: str, text: str, h: dict | None, oway: Path) -> list[str]:
    """Rules on what a file holds: research cites real sources (#97), a done slice has its walkthrough (#86)."""
    out = []
    kind = (h or {}).get("type")
    if kind == "research" and not name.endswith("RES-takeover-map.md"):
        body = text.split("\n---\n", 1)[-1]
        if not re.search(r"^#+ .*(source|référence|reference)", body, re.I | re.M):
            out.append(f"{name}: research has no Sources section")
        elif not re.search(r"\]\(https?://", body):
            out.append(f"{name}: research Sources have no full https link")
        plain = re.sub(r"\[[^\]]*\]\([^)]*\)|`[^`]*`|https?://\S+", "", body)
        for dom in sorted(set(m.group(0) for m in BARE_DOMAIN.finditer(plain)))[:3]:
            out.append(f"{name}: bare source '{dom}'; give the full link")
    if kind == "slice" and (h or {}).get("state") in {"in-review", "done"}:
        slice_id = Path(name).stem
        if not (oway / "slices" / f"{slice_id}.walkthrough.md").exists() and "## Walkthrough" not in text:
            out.append(f"{name}: a slice in {h['state']} needs its walkthrough ({slice_id}.walkthrough.md)")
    return out


def run(root: Path) -> list[str]:
    oway = root / "_oway"
    out: list[str] = []
    if not oway.is_dir():
        return ["_oway/ folder is missing"]
    cfg = oway / "config.json"
    out += [f"_oway/config.json: {p}" for p in check_config(cfg)] if cfg.exists() \
        else ["_oway/config.json is missing"]
    current: list[str] = []
    parsed_docs: list[tuple[str, Path, dict[str, str]]] = []
    for f in sorted(oway.rglob("*.md")):
        name = rel(root, f)
        text = f.read_text(encoding="utf-8")
        if f.name not in headers.NO_HEADER and not name.startswith(("_oway/keeper/", "_oway/evidence/")):
            h = headers.parse(text)
            out += [f"{name}: {p}" for p in headers.problems(h)]
            out += content_rules(name, text, h, oway)
            out += hierarchy.check_three_parts(name, text, h)
            if h:
                parsed_docs.append((name, f, h))
            if h and h.get("type") == "milestone" and h.get("current") == "true":
                current.append(name)
        for target in LINK.findall(text):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            if target.startswith("/"):
                out.append(f"{name}: link '{target}' is absolute; links stay relative")
                continue
            path = (f.parent / target.split("#", 1)[0]).resolve()
            if not path.exists():
                out.append(f"{name}: broken link '{target}'")
        if ABSOLUTE_HOME.search(text):
            out.append(f"{name}: points to a personal machine path (/home/..., /Users/...)")
    out += hierarchy.check_parents(parsed_docs, oway)
    if len(current) > 1:
        out.append(f"more than one milestone has current: true ({', '.join(current)})")
    out += [f"{rel(root, p)}: out of date, run `oway index`" for p in index.build(oway, check=True)]
    return out
