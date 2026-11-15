"""Find the project root and its _oway folder."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path


class OwayError(Exception):
    """A user-facing error; the CLI prints it and exits 2."""


def find_root(start: Path | None = None) -> Path:
    here = (start or Path(os.environ.get("OWAY_ROOT", "."))).resolve()
    for p in (here, *here.parents):
        if (p / "_oway").is_dir():
            return p
    raise OwayError(f"no _oway/ folder at or above {here}")


def oway_dir(root: Path) -> Path:
    return root / "_oway"


def git_head(root: Path) -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()
