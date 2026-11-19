"""Single-source 5-harness home installer (`oway sync` and `om/sync-om.sh`)."""

from __future__ import annotations

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

from .project import OwayError

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OM_ROOT = REPO_ROOT / "om"
SKILLS_ROOT = REPO_ROOT / "skills"
ROLES_ROOT = REPO_ROOT / "agents"
SUPPORTED_TOOLS = ("pi", "opencode", "claude", "codex", "antigravity", "oway")
OM_AGENTS = ("om-caps", "om-review", "om-assist")
PROTECTED_USER_FILES = (
    ".claude/CLAUDE.md",
    ".codex/AGENTS.md",
    ".gemini/config/AGENTS.md",
    ".gemini/GEMINI.md",
    ".pi/agent/AGENTS.md",
)
CLAUDE_TOOL_MAP = {"read_file": "Read", "run_command": "Bash", "search_web": "WebSearch"}
CLAUDE_DROP_TOOLS = {"send_message"}
BUILTIN_RETIRED = {
    "pi": [".pi/agent/skills/om-uix"],
    "opencode": [".config/opencode/skills/om-uix"],
    "claude": [".claude/skills/om-uix"],
    "codex": [".agents/skills/om-uix"],
    "antigravity": [".gemini/config/skills/om-uix"],
}


def render_opencode_agent(src: Path) -> str:
    text = src.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        raise OwayError(f"no frontmatter in {src}")
    fm, body = m.groups()
    desc = re.search(r"^description:.*(?:\n[ \t]+.*)*", fm, re.M)
    if not desc:
        raise OwayError(f"no description in {src}")
    return f"---\n{desc.group(0)}\nmode: subagent\n---\n{body}"


def render_claude_agent(src: Path) -> str:
    text = src.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return text
    fm, body = m.groups()
    out: list[str] = []
    in_tools = False
    for line in fm.splitlines():
        if re.match(r"^tools:\s*$", line):
            in_tools = True
            out.append(line)
            continue
        if in_tools:
            item = re.match(r"^([ \t]+-[ \t]+)(\S+)(.*)$", line)
            if item:
                name = item.group(2)
                if name in CLAUDE_DROP_TOOLS:
                    continue
                mapped = CLAUDE_TOOL_MAP.get(name, name)
                out.append(f"{item.group(1)}{mapped}{item.group(3)}")
                continue
            in_tools = False
        out.append(line)
    return f"---\n" + "\n".join(out) + f"\n---\n{body}"


def _expand(raw: str, home: Path) -> Path:
    s = raw.strip()
    if s.startswith("~/"):
        s = str(home) + s[1:]
    elif s == "~":
        s = str(home)
    s = s.replace("$HOME", str(home))
    return Path(s)


def _is_protected(target: Path, home: Path) -> bool:
    norm = os.path.normpath(str(target))
    return any(norm == os.path.normpath(str(home / rel)) for rel in PROTECTED_USER_FILES)


def _backup(path: Path, home: Path, backup_dir: Path, out: list[str]) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    prefix = str(home).rstrip("/") + "/"
    raw = str(path)
    rel = raw[len(prefix):] if raw.startswith(prefix) else raw.lstrip("/")
    dest = backup_dir / rel.replace("/", "__")
    shutil.move(str(path), str(dest))
    out.append(f"  backup: {path} -> {dest}")


def _skill_rows(tool: str, dest_dir: str, oway_skills: bool) -> list[tuple[str, str, str, Path]]:
    rows = [
        (tool, "symlink", f"{dest_dir}/om-plan", OM_ROOT / "skills/om-plan"),
        (tool, "symlink", f"{dest_dir}/om-assist", OM_ROOT / "skills/om-assist"),
        (tool, "symlink", f"{dest_dir}/oway-uix", SKILLS_ROOT / "oway-uix"),
    ]
    if oway_skills and SKILLS_ROOT.is_dir():
        for d in sorted(SKILLS_ROOT.iterdir()):
            if d.is_dir() and (d / "SKILL.md").is_file() and d.name != "oway-uix":
                rows.append((tool, "symlink", f"{dest_dir}/{d.name}", d))
    return rows


def _oway_roles() -> list[Path]:
    if not ROLES_ROOT.is_dir():
        return []
    return sorted(p for p in ROLES_ROOT.glob("*/*.md")
                  if p.is_file() and p.name not in ("README.md", "TEAM.md"))


def _tool_rows(tool: str, oway_skills: bool, oway_agents: bool) -> list[tuple[str, str, str, Path]]:
    roles = _oway_roles() if oway_agents else []
    om_srcs = [(f"{a}.md", OM_ROOT / f"agents/{a}.md") for a in OM_AGENTS]
    if tool == "pi":
        rows = _skill_rows("pi", "~/.pi/agent/skills", oway_skills)
        rows += [("pi", "symlink", f"~/.pi/agent/prompts/{n}", s) for n, s in om_srcs]
        rows += [("pi", "symlink", f"~/.pi/agent/prompts/{r.name}", r) for r in roles]
        rows.append(("pi", "symlink", "~/.pi/agent/APPEND_SYSTEM.md", OM_ROOT / "rules/AGENTS.md"))
        return rows
    if tool == "opencode":
        rows = _skill_rows("opencode", "~/.config/opencode/skills", oway_skills)
        rows += [("opencode", "opencode-agent", f"~/.config/opencode/agents/{n}", s) for n, s in om_srcs]
        rows += [("opencode", "opencode-agent", f"~/.config/opencode/agents/{r.name}", r) for r in roles]
        rows.append(("opencode", "symlink", "~/.config/opencode/AGENTS.md", OM_ROOT / "rules/AGENTS.md"))
        return rows
    if tool == "claude":
        rows = _skill_rows("claude", "~/.claude/skills", oway_skills)
        rows += [("claude", "claude-agent", f"~/.claude/agents/{n}", s) for n, s in om_srcs]
        rows += [("claude", "symlink", f"~/.claude/agents/{r.name}", r) for r in roles]
        return rows
    if tool == "codex":
        rows = _skill_rows("codex", "~/.agents/skills", oway_skills)
        rows += [("codex", "symlink", f"~/.codex/agents/{n}", s) for n, s in om_srcs]
        rows += [("codex", "symlink", f"~/.codex/agents/{r.name}", r) for r in roles]
        return rows
    if tool == "antigravity":
        rows = [("antigravity", "symlink", "~/.gemini/config/plugins/om", OM_ROOT)]
        rows += _skill_rows("antigravity", "~/.gemini/config/skills", oway_skills)
        rows += [("antigravity", "symlink", f"~/.gemini/config/agents/{r.name}", r) for r in roles]
        return rows
    if tool == "oway":
        return [("oway", "symlink", "~/.local/bin/oway", OM_ROOT / "bin/oway")]
    return []


def _apply_symlink(tool: str, target: Path, src: Path, mode: str,
                   home: Path, backup_dir: Path, out: list[str]) -> bool:
    if target.is_symlink() and target.resolve() == src.resolve():
        out.append(f"ok   [{tool}] {target}")
        return True
    if mode == "check":
        out.append(f"DRIFT [{tool}] {target} (want link -> {src})")
        return False
    if mode == "dry":
        out.append(f"would link [{tool}] {target} -> {src}")
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        _backup(target, home, backup_dir, out)
    target.symlink_to(src)
    out.append(f"link [{tool}] {target} -> {src}")
    return True


def _apply_adapter(tool: str, method: str, target: Path, src: Path, mode: str,
                   home: Path, backup_dir: Path, out: list[str]) -> bool:
    want = render_opencode_agent(src) if method == "opencode-agent" else render_claude_agent(src)
    if target.is_file() and not target.is_symlink() and target.read_text(encoding="utf-8") == want:
        out.append(f"ok   [{tool}] {target} (copy)")
        return True
    if mode == "check":
        out.append(f"DRIFT [{tool}] {target} (copy differs from {src.name})")
        return False
    if mode == "dry":
        out.append(f"would copy [{tool}] {target} <- {src.name}")
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        _backup(target, home, backup_dir, out)
    target.write_text(want, encoding="utf-8")
    out.append(f"copy [{tool}] {target} <- {src.name}")
    return True


def _process_row(row: tuple[str, str, str, Path], mode: str,
                 home: Path, backup_dir: Path, out: list[str]) -> bool:
    tool, method, raw_target, src = row
    target = _expand(raw_target, home)
    if _is_protected(target, home):
        out.append(f"FAIL [{tool}] protected user file: {target}")
        return False
    if not src.exists():
        out.append(f"FAIL [{tool}] source missing: {src}")
        return False
    if method == "symlink":
        return _apply_symlink(tool, target, src, mode, home, backup_dir, out)
    if method in ("opencode-agent", "claude-agent"):
        return _apply_adapter(tool, method, target, src, mode, home, backup_dir, out)
    out.append(f"FAIL unknown method '{method}' for {target}")
    return False


def _process_retire(path: Path, mode: str, home: Path, backup_dir: Path, out: list[str]) -> bool:
    if _is_protected(path, home):
        out.append(f"FAIL protected user file cannot be retired: {path}")
        return False
    if not path.exists() and not path.is_symlink():
        out.append(f"ok   retired {path}")
        return True
    if mode == "check":
        out.append(f"DRIFT old path still there: {path}")
        return False
    if mode == "dry":
        out.append(f"would retire {path}")
        return True
    _backup(path, home, backup_dir, out)
    out.append(f"retire {path}")
    return True


def _resolve_tools(tools_arg: str | None, conf_dir: Path) -> list[str]:
    raw = tools_arg if tools_arg is not None else os.environ.get("OM_TOOLS", "")
    if not raw and (conf_dir / "tools").is_file():
        lines = [ln.strip() for ln in (conf_dir / "tools").read_text(encoding="utf-8").splitlines()
                 if ln.strip() and not ln.strip().startswith("#")]
        raw = ",".join(lines)
    tools = [t.strip() for t in raw.split(",") if t.strip()]
    if not tools:
        raise OwayError("No tools chosen. Use --tools pi,opencode,claude,codex,antigravity,oway.")
    return tools


def _extra_rows(conf_dir: Path) -> list[tuple[str, str, str, Path]]:
    extra = conf_dir / "extra"
    if not extra.is_file():
        return []
    rows = []
    for line in extra.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) >= 3:
            rows.append(("extra", parts[0], parts[1], OM_ROOT / parts[2]))
    return rows


def _retire_paths(conf_dir: Path, tools: list[str], home: Path) -> list[Path]:
    paths: list[Path] = []
    for t in tools:
        for rel in BUILTIN_RETIRED.get(t, ()):
            p = home / rel
            if p.exists() or p.is_symlink():
                paths.append(p)
    retire = conf_dir / "retire"
    if retire.is_file():
        for line in retire.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                paths.append(_expand(s, home))
    return paths


def run(tools_arg: str | None = None, oway_skills: bool = False, oway_agents: bool = False,
        dry_run: bool = False, check: bool = False, home_dir: Path | None = None) -> tuple[int, list[str]]:
    home = Path(home_dir) if home_dir is not None else Path(os.environ.get("OM_HOME") or Path.home())
    conf_dir = home / ".config/om"
    tools = _resolve_tools(tools_arg, conf_dir)
    all_skills = oway_skills or os.environ.get("OM_OWAY_SKILLS") == "1"
    all_agents = oway_agents or os.environ.get("OM_OWAY_AGENTS") == "1"
    mode = "check" if check else ("dry" if dry_run else "apply")
    backup_dir = home / ".om-deploy-backups" / datetime.now().strftime("%Y%m%d-%H%M%S")

    out = [f"root={OM_ROOT}  tools={','.join(tools)}  mode={mode}"]
    ok = True
    count = 0
    for t in tools:
        if t not in SUPPORTED_TOOLS:
            out.append(f"FAIL unknown tool '{t}' (built in: {', '.join(SUPPORTED_TOOLS)})")
            ok = False
            continue
        for row in _tool_rows(t, all_skills, all_agents):
            count += 1
            ok = _process_row(row, mode, home, backup_dir, out) and ok

    for row in _extra_rows(conf_dir):
        count += 1
        ok = _process_row(row, mode, home, backup_dir, out) and ok

    for path in _retire_paths(conf_dir, tools, home):
        count += 1
        ok = _process_retire(path, mode, home, backup_dir, out) and ok

    out.append(f"RESULT: {'OK' if ok else 'DRIFT/FAIL'} ({count} targets)")
    return (0 if ok else 1), out
