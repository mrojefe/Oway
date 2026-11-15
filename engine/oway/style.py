"""Style library of the design skill: MIT style packs and themes, fetched once per machine.

Two upstream catalogs, pinned to commits, kept outside any project in a cache:
  typeui-styles    bergside/awesome-design-skills  (style packs: SKILL.md + DESIGN.md)
  hallmark-themes  Nutlope/hallmark                (themes, craft and anti-slop references)
The cache is OWAY_STYLES, else ~/.cache/oway/styles.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .project import OwayError

SOURCES = {
    "typeui": ("https://github.com/bergside/awesome-design-skills",
               "f631a09b4fcc0166f2e2c1a8c81906ef680c57e8"),
    "hallmark": ("https://github.com/Nutlope/hallmark",
                 "04977e15f3dfd6ee4b74c887dac3eb52665d6c92"),
}
BRUTAL = ["neobrutalism", "neubrutalism", "neo-brutalism", "brutal", "brutalism"]
SYNONYMS = {
    "neobrutalism": BRUTAL, "neobrutaliste": BRUTAL, "neubrutalism": BRUTAL, "brutalism": BRUTAL,
    "glassmorphism": ["glassmorphism", "liquid-glass", "refract", "lumen"],
    "swiss": ["swiss", "grid", "minimal", "clean", "specimen", "werkstatt"],
    "bento": ["bento", "grid", "studio", "formwork"],
}


def catalog_dir() -> Path:
    return Path(os.environ.get("OWAY_STYLES") or Path.home() / ".cache" / "oway" / "styles")


def _git(*args: str, cwd: Path) -> None:
    done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if done.returncode:
        raise OwayError(f"git {args[0]} failed: {done.stderr.strip()[:200]}")


def _checkout(url: str, sha: str, dest: Path) -> Path:
    dest.mkdir(parents=True)
    _git("init", "-q", cwd=dest)
    _git("fetch", "-q", "--depth", "1", url, sha, cwd=dest)
    _git("checkout", "-q", "FETCH_HEAD", cwd=dest)
    return dest


def fetch(sources: dict[str, tuple[str, str]] | None = None) -> str:
    """Build the catalog from the pinned upstream commits; replaces the old one."""
    src = sources or SOURCES
    dest = catalog_dir()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        packs = _checkout(*src["typeui"], tmp_dir / "typeui")
        hall = _checkout(*src["hallmark"], tmp_dir / "hallmark") / "skills" / "hallmark"
        new = tmp_dir / "catalog"
        shutil.copytree(packs / "skills", new / "typeui-styles", ignore=shutil.ignore_patterns(".DS_Store"))
        shutil.copytree(hall / "references" / "themes", new / "hallmark-themes")
        refs = new / "hallmark-themes" / "references"
        refs.mkdir()
        for f in (hall / "references").glob("*.md"):
            shutil.copy(f, refs)
        (new / "hallmark-themes" / "scripts").mkdir()
        for name in ("sloplint.mjs", "theme.mjs"):
            if (hall / "scripts" / name).exists():
                shutil.copy(hall / "scripts" / name, new / "hallmark-themes" / "scripts")
        (new / "licenses").mkdir()
        shutil.copy(packs / "LICENSE", new / "licenses" / "LICENSE-awesome-design-skills-MIT.txt")
        shutil.copy(hall / "LICENSE", new / "licenses" / "LICENSE-hallmark-MIT.txt")
        (new / "SOURCE.txt").write_text("".join(f"{k}: {u}@{s}\n" for k, (u, s) in src.items()), encoding="utf-8")
        shutil.rmtree(dest, ignore_errors=True)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(new), dest)
    return f"{dest}: {len(_packs())} style packs, {len(_themes())} themes"


def _packs() -> list[Path]:
    root = catalog_dir() / "typeui-styles"
    return sorted(d for d in root.iterdir() if d.is_dir()) if root.is_dir() else []


def _themes() -> list[Path]:
    root = catalog_dir() / "hallmark-themes"
    return sorted(f for f in root.glob("*.md") if f.name != "README.md") if root.is_dir() else []


def _need_catalog() -> None:
    if not _packs() and not _themes():
        raise OwayError(f"no style catalog in {catalog_dir()}; run: oway style fetch")


def _field(text: str, name: str) -> str:
    for line in text.splitlines():
        if line.startswith(name + ":"):
            return line.split(":", 1)[1].strip()
    return ""


def _terms(query: str) -> list[str]:
    q = query.lower().strip()
    found = {q, q.replace("-", ""), q.replace(" ", "-")}
    for key, vals in SYNONYMS.items():
        if key in q or q in key:
            found.update(vals)
    return sorted(found)


def listing() -> list[str]:
    _need_catalog()
    packs, themes = [d.name for d in _packs()], [f.stem for f in _themes()]
    return [f"style packs ({len(packs)}): " + ", ".join(packs),
            f"themes ({len(themes)}): " + ", ".join(themes)]


def search(query: str) -> list[str]:
    _need_catalog()
    terms = _terms(query)
    out = [f"search '{query}' (terms: {', '.join(terms)})"]
    for pack in _packs():
        skill = pack / "SKILL.md"
        text = skill.read_text(encoding="utf-8", errors="ignore") if skill.exists() else ""
        if any(t in (pack.name + "\n" + text).lower() for t in terms):
            out.append(f"pack  {pack.name}: {_field(text, 'description')[:120]}")
    for theme in _themes():
        text = theme.read_text(encoding="utf-8", errors="ignore")
        if any(t in (theme.stem + "\n" + text).lower() for t in terms):
            out.append(f"theme {theme.stem}: {_field(text, 'material')[:120]}")
    return out


def show(slug: str) -> list[str]:
    _need_catalog()
    s, out = slug.lower().strip(), []
    pack = catalog_dir() / "typeui-styles" / s
    theme = catalog_dir() / "hallmark-themes" / f"{s}.md"
    for name in ("SKILL.md", "DESIGN.md"):
        if (pack / name).exists():
            out += [f"--- style pack {s}/{name} ---", (pack / name).read_text(encoding="utf-8", errors="ignore")]
    if theme.exists():
        out += [f"--- theme {s} ---", theme.read_text(encoding="utf-8", errors="ignore")]
    return out or [f"no style '{slug}'; searching instead:"] + search(slug)
