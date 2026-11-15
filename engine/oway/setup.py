"""`oway platform init` and `oway setup`: the parts of Step 0 a script can do.

The rest (the owner interview, GitHub settings, the keeper interval) needs the
owner, so it is written to `setup_pending` instead of guessed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import index, ledger
from .project import OwayError

VERSION_FILE = Path(__file__).resolve().parent.parent / "VERSION"
TOOL_ROOT = Path(__file__).resolve().parent.parent.parent
PENDING = [
    "owner profile (OwayHelpers interview)",
    "keeper report interval",
    "quota tracking",
    "GitHub bot app, protected main, sync Action",
    "the three first parts: goal, scope, first milestone",
]
PATH_CLASSES = {
    "schema": ["**/migrations/**", "**/*.sql", "**/schema.prisma"],
    "api": ["**/api/**", "**/openapi.*", "**/*.proto"],
    "auth": ["**/auth/**"],
    "deps": ["**/package.json", "**/*lock*", "**/pyproject.toml", "**/requirements*.txt",
             "**/go.mod", "**/Cargo.toml"],
    "code": ["src/**", "app/**", "lib/**"],
}


def default_platform() -> Path:
    return Path(os.environ.get("OWAY_PLATFORM", Path.home() / ".oway"))


def platform_init(path: Path) -> list[str]:
    """Create the owner's Platform folder once. Never overwrites a file."""
    made = []
    files = {
        "platform.json": json.dumps({"schema": 1, "tool": str(TOOL_ROOT),
                                     "oway_version": VERSION_FILE.read_text().strip()}, indent=2) + "\n",
        "profile.md": ("---\nname: owner-profile\ndescription: How the owner works, written once "
                       "by the OwayHelpers\ntype: profile\nstate: draft\napproved: no\n---\n\n"
                       "# Owner profile\n\nNot set yet: the OwayHelpers fill it with the owner "
                       "at the first setup. See the profile template in the Oway docs.\n"),
    }
    path.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        target = path / name
        if not target.exists():
            target.write_text(text, encoding="utf-8")
            made.append(name)
    return made


def project_setup(root: Path, language: str, builders: list[str], uix: bool,
                  platform: Path | None = None, claude_hook: bool = False) -> list[str]:
    """Create `_oway/` for a project. Refuses when one exists (use the takeover steps)."""
    oway = root / "_oway"
    if oway.exists():
        raise OwayError("_oway/ already exists; this is a takeover or upgrade, not a setup")
    platform = platform or default_platform()
    profile = platform / "profile.md"
    pending = list(PENDING)
    if profile.exists() and "state: approved" in profile.read_text(encoding="utf-8"):
        pending.remove("owner profile (OwayHelpers interview)")
    cfg = {
        "schema": 1,
        "oway_version": VERSION_FILE.read_text().strip(),
        "language": language,
        "teams": {"product": True, "uix": uix, "dev": {"builders": builders}, "qa": True},
        "message_max_chars": 200,
        "profile": str(profile) if profile.exists() else "not set",
        "setup_pending": pending,
        "path_classes": PATH_CLASSES,
    }
    oway.mkdir(parents=True)
    (oway / "config.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    (oway / "project.md").write_text(
        "---\nname: project\ndescription: Not written yet\ntype: project\nstate: draft\n"
        "approved: no\nowner: LeadOway\n---\n\n# Project\n\n## 1. Main goal\nNot set: needs the owner.\n\n"
        "## 2. What you get\nNot set.\n\n## 3. The proof you will have\nNot set.\n\n## Setup pending\n"
        + "".join(f"- {p}\n" for p in pending), encoding="utf-8")
    made = ["_oway/config.json", "_oway/project.md"]
    ledger.append(oway, f"Oway setup, version {cfg['oway_version']}; pending: {len(pending)} items")
    made.append("_oway/LEDGER.md")
    if claude_hook:
        made.append(install_claude_stop_hook(root))
    index.build(oway)
    made.append("_oway/INDEX.md")
    return made


def install_claude_stop_hook(root: Path) -> str:
    """Add the builder Stop hook to the project's .claude/settings.json, keeping the rest."""
    path = root / ".claude" / "settings.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    cmd = f'python3 "{TOOL_ROOT / "engine" / "oway"}" stop-hook'
    hooks = data.setdefault("hooks", {})
    stop = hooks.setdefault("Stop", [])
    if not any(h.get("command") == cmd for entry in stop for h in entry.get("hooks", [])):
        stop.append({"hooks": [{"type": "command", "command": cmd}]})
    guard_cmd = cmd.replace(" stop-hook", " guard")
    pre = hooks.setdefault("PreToolUse", [])
    if not any(h.get("command") == guard_cmd for entry in pre for h in entry.get("hooks", [])):
        pre.append({"matcher": "Write|Edit|MultiEdit|NotebookEdit",
                    "hooks": [{"type": "command", "command": guard_cmd}]})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return ".claude/settings.json"


def install_pi_extension(root: Path) -> str:
    """Write the pi stop-hook extension to .pi/extensions/oway-stop.ts (project trust still applies)."""
    src = (Path(__file__).resolve().parent / "pi_extension.ts").read_text(encoding="utf-8")
    entry = str(TOOL_ROOT / "engine" / "oway")
    path = root / ".pi" / "extensions" / "oway-stop.ts"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(src.replace("__OWAY_ENTRY__", entry.replace("\\", "/")), encoding="utf-8")
    return ".pi/extensions/oway-stop.ts"
