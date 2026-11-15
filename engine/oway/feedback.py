"""`oway feedback`: turn a gap found in a project into an issue for the Oway repo.

It never sends anything itself: it saves the note under `_oway/feedback/` and
prints a GitHub link and a `gh` command, so a lead or the owner sends it.
Secrets, e-mail addresses and personal paths are removed first.
"""
from __future__ import annotations

import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from . import ledger, setup
from .project import OwayError

DEFAULT_REPO = "mrojefe/cgspec"
SCRUB = [
    (re.compile(r"(?:ghp|gho|github_pat|sk|xox[bp])[-_][A-Za-z0-9_-]{8,}"), "[secret]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[email]"),
    (re.compile(r"(?:/home/|/Users/|[A-Z]:\\Users\\)[^\s)`'\"]*"), "[path]"),
]


def scrub(text: str) -> str:
    for pattern, repl in SCRUB:
        text = pattern.sub(repl, text)
    return text


def repo() -> str:
    pj = setup.default_platform() / "platform.json"
    if pj.exists():
        return json.loads(pj.read_text(encoding="utf-8")).get("feedback_repo", DEFAULT_REPO)
    return DEFAULT_REPO


def create(oway: Path, title: str, body: str) -> tuple[Path, str, str]:
    title, body = scrub(" ".join(title.split())), scrub(body.strip())
    if not title:
        raise OwayError("feedback needs a title")
    cfg = json.loads((oway / "config.json").read_text(encoding="utf-8"))
    body += f"\n\nOway version: {cfg.get('oway_version', '?')}. Sent with `oway feedback`."
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    fid = f"FB-{day}-{secrets.token_hex(2)}"
    path = oway / "feedback" / f"{fid}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nname: {fid}\ndescription: {title}\ntype: feedback\nstate: draft\n---\n\n"
                    f"# {title}\n\n{body}\n", encoding="utf-8")
    target = repo()
    url = f"https://github.com/{target}/issues/new?" + urlencode(
        {"title": f"[feedback] {title}", "body": body, "labels": "feedback"})
    cmd = f"gh issue create -R {target} --label feedback --title {json.dumps('[feedback] ' + title)} --body-file {path.as_posix()}"
    ledger.append(oway, f"feedback {fid} drafted: {title}")
    return path, url, cmd
