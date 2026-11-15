#!/usr/bin/env python3
"""style_hub.py: list, search and show the om-uix MIT UI styles.

Two catalogs, built by scripts/fetch_catalog.sh:
  1. typeui-styles: bergside/awesome-design-skills (67 style packs)
  2. hallmark-themes: Nutlope/hallmark (50 themes)
"""

import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TYPEUI_DIR = BASE_DIR / "catalog" / "typeui-styles"
HALLMARK_DIR = BASE_DIR / "catalog" / "hallmark-themes"

SYNONYMS = {
    "neobrutalism": ["neobrutalism", "neubrutalism", "neo-brutalism", "brutal", "brutalism"],
    "neobrutaliste": ["neobrutalism", "neubrutalism", "neo-brutalism", "brutal", "brutalism"],
    "neubrutalism": ["neobrutalism", "neubrutalism", "neo-brutalism", "brutal", "brutalism"],
    "brutalism": ["brutal", "brutalism", "neobrutalism", "neubrutalism", "neo-brutalism"],
    "glassmorphism": ["glassmorphism", "liquid-glass", "refract", "lumen"],
    "swiss": ["swiss", "grid", "minimal", "clean", "specimen", "werkstatt"],
    "bento": ["bento", "grid", "studio", "formwork"],
}


def need_catalog():
    if not TYPEUI_DIR.exists() and not HALLMARK_DIR.exists():
        sys.exit("No catalog yet. Run scripts/fetch_catalog.sh first.")


def typeui_slugs():
    return sorted(d.name for d in TYPEUI_DIR.iterdir() if d.is_dir()) if TYPEUI_DIR.exists() else []


def hallmark_files():
    if not HALLMARK_DIR.exists():
        return []
    return sorted(f for f in HALLMARK_DIR.glob("*.md") if f.name != "README.md")


def list_all():
    typeui = typeui_slugs()
    hallmark = [f.stem for f in hallmark_files()]
    print(f"=== 1. Style packs (awesome-design-skills, MIT): {len(typeui)} ===")
    print(", ".join(typeui))
    print(f"\n=== 2. Hallmark themes (MIT): {len(hallmark)} ===")
    print(", ".join(hallmark))


def expand_terms(query):
    q = query.lower().strip()
    terms = {q, q.replace("-", ""), q.replace(" ", "-")}
    for key, vals in SYNONYMS.items():
        if key in q or q in key:
            terms.update(vals)
    return sorted(terms)


def matches_any(text, terms):
    t = text.lower()
    return any(term in t for term in terms)


def field(text, name):
    for line in text.splitlines():
        if line.startswith(name + ":"):
            return line.split(":", 1)[1].strip()
    return ""


def search_styles(query):
    terms = expand_terms(query)
    print(f"Search '{query}' (terms: {', '.join(terms)})\n")
    hits = []
    for slug in typeui_slugs():
        skill = TYPEUI_DIR / slug / "SKILL.md"
        text = skill.read_text(encoding="utf-8", errors="ignore") if skill.exists() else ""
        if matches_any(slug, terms) or matches_any(text, terms):
            hits.append((slug, field(text, "description"), skill, TYPEUI_DIR / slug / "DESIGN.md"))
    print(f"[Style packs] ({len(hits)} matches):")
    for slug, desc, skill, design in hits[:10]:
        print(f"  - {slug}: {desc}\n    SKILL.md : {skill}\n    DESIGN.md: {design}")
    themes = []
    for f in hallmark_files():
        text = f.read_text(encoding="utf-8", errors="ignore")
        if matches_any(f.stem, terms) or matches_any(text, terms):
            themes.append((f.stem, field(text, "material"), f))
    print(f"\n[Hallmark themes] ({len(themes)} matches):")
    for slug, material, path in themes[:10]:
        print(f"  - {slug}: {material}\n    Theme file: {path}")


def show_style(slug):
    s = slug.lower().strip()
    found = False
    pack = TYPEUI_DIR / s
    if pack.is_dir():
        found = True
        print(f"=== Style pack: {s} (MIT) ===")
        for name in ("SKILL.md", "DESIGN.md"):
            fp = pack / name
            if fp.exists():
                print(f"\n--- {fp} ---\n{fp.read_text(encoding='utf-8', errors='ignore')}")
    theme = HALLMARK_DIR / f"{s}.md"
    if theme.exists():
        found = True
        print(f"\n=== Hallmark theme: {s} (MIT) ===\n{theme.read_text(encoding='utf-8', errors='ignore')}")
    if not found:
        print(f"No slug '{slug}'. Searching instead:\n")
        search_styles(slug)


def main():
    parser = argparse.ArgumentParser(description="om-uix style hub")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list every style pack and theme")
    sub.add_parser("search", help="search by keyword").add_argument("query")
    sub.add_parser("show", help="print a style's full text").add_argument("slug")
    args = parser.parse_args()
    need_catalog()
    if args.cmd == "list":
        list_all()
    elif args.cmd == "search":
        search_styles(args.query)
    else:
        show_style(args.slug)


if __name__ == "__main__":
    main()
