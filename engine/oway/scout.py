"""Free design reference scout for the design skill: no API key, no paid service.

Ported from the owner's design_scout.py. Scouts real screenshots from godly.website and
land-book.com with plain HTTPS GETs, downloads them, and writes a markdown page with a
carousel block (Antigravity), a breakdown table and a plain image list for other tools.
Screenshots are references only: the rights belong to the sites.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
GODLY_IMG = r"https://cdn\.recent\.design/items/([a-zA-Z0-9]+)/0/poster/960\.webp"
LANDBOOK_LINK = r"<a[^>]+href=[\"|'](/websites/([^\"|']+))[\"|'][^>]*>.*?<img[^>]+src=[\"|']([^\"|']+)[\"|']"


def fetch(url: str, timeout: int = 12) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept": ACCEPT,
                                               "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as exc:  # network or site errors only warn
        print(f"[!] failed to fetch {url}: {exc}", file=sys.stderr)
        return None


def download(img_url: str, dest: Path) -> bool:
    req = urllib.request.Request(img_url, headers={"User-Agent": AGENT,
                                                   "Referer": urllib.parse.urljoin(img_url, "/")})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
    except Exception as exc:
        print(f"[!] failed to download {img_url}: {exc}", file=sys.stderr)
        return False
    if len(data) <= 1000:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def godly(query: str, limit: int) -> list[dict]:
    url = "https://godly.website/" + (f"?q={urllib.parse.quote(query)}" if query else "")
    raw = fetch(url)
    if not raw:
        return []
    ids = list(dict.fromkeys(re.findall(GODLY_IMG, raw.decode("utf-8", errors="ignore"))))
    return [{"source": "Godly (high craft)",
             "title": f"Aesthetic interface #{i + 1}" + (f" ({query.title()})" if query else ""),
             "image_url": f"https://cdn.recent.design/items/{item}/0/poster/960.webp",
             "ref_url": "https://godly.website", "platform": "web",
             "style": "High-craft modern web / fluid micro-interactions / dark and light themes",
             "tags": ["Modern craft", "Micro-interactions", "Typography hierarchy"]}
            for i, item in enumerate(ids[:limit])]


def landbook(query: str, limit: int) -> list[dict]:
    url = "https://land-book.com/" if not query else f"https://land-book.com/websites?search={urllib.parse.quote(query)}"
    raw = fetch(url)
    if not raw:
        return []
    out, seen = [], set()
    for link, slug, img in re.findall(LANDBOOK_LINK, raw.decode("utf-8", errors="ignore"), re.DOTALL):
        if img in seen or link in seen or "avatar" in img or "ad-small" in img:
            continue
        seen.update((img, link))
        out.append({"source": "Land-book (SaaS showcase)",
                    "title": re.sub(r"^\d+-", "", slug).replace("-", " ").title()[:45],
                    "image_url": img, "ref_url": f"https://land-book.com{link}", "platform": "web",
                    "style": "Production SaaS / high-conversion layouts / data display",
                    "tags": ["SaaS UI", "Dashboard", "Conversion flow"]})
        if len(out) >= limit:
            break
    return out


def markdown(refs: list[dict], query: str) -> str:
    """The reference page. Write your own token plan from the references; none is guessed here."""
    lines = ["# Curated UI/UX design references", ""]
    if query:
        lines += [f"> **Design target / focus**: `{query}`"]
    lines += ["> Free sources: Godly.website and Land-book. References only: the rights belong to the sites.", "",
              "## 1. Carousel (Antigravity)", "", "````carousel"]
    for i, ref in enumerate(refs):
        lines.append(f"![{ref['source']}: {ref['title']}]({ref.get('local_path', ref['image_url'])})")
        if i < len(refs) - 1:
            lines.append("<!-- slide -->")
    lines += ["````", "", "## 2. Breakdown", "",
              "| Reference | Source | Patterns | Platform | Link |", "| :--- | :--- | :--- | :--- | :--- |"]
    for ref in refs:
        lines.append(f"| **{ref['title']}** | `{ref['source']}` | {' / '.join(ref['tags'])} | "
                     f"`{ref['platform'].upper()}` | [view source]({ref['ref_url']}) |")
    lines += ["", "## 3. Plain list (tools without a carousel)", ""]
    for ref in refs:
        lines.append(f"- {ref['title']} ({ref['source']}): {ref['ref_url']}  image: {ref.get('local_path', ref['image_url'])}")
    lines += ["", "## 4. Anti-slop directives", "",
              "- Grounded palette: no generic purple or blue gradient buttons; one sharp accent.",
              "- Hairline borders (`border-neutral-200 dark:border-neutral-800`) instead of heavy shadows.",
              "- Strict type hierarchy, never default Inter alone.",
              "- Distinct `:hover`, `:focus-visible` and `:active` states; 150-200ms transitions.",
              "- Touch targets of at least 44x44px; WCAG AA contrast.",
              "", "## 5. Synthesis and token plan", "",
              "_Fill from the references above: dominant style, palette, type hierarchy; then map to a style pack with `oway style search`._", "",
              "Default starting palette (replace it from the references):", "",
              "- Canvas: light `#FBFBFD` / dark `#0A0A0C`",
              "- Surfaces and cards: light `#FFFFFF` / dark `#141417`, subtle inner bevel",
              "- Borders: light `#E5E5EB` / dark `#222227`",
              "- Primary accent: royal blue `#2563EB`, emerald `#10B981` or monochrome ink `#111827`", ""]
    return "\n".join(lines)


def scout(query: str, limit: int) -> list[dict]:
    refs, seen = [], set()
    for ref in godly(query, limit) + landbook(query, limit):
        if ref["image_url"] not in seen:
            seen.add(ref["image_url"])
            refs.append(ref)
    return refs


def run(query: str, dest_dir: Path, output_md: Path | None, limit: int = 3, as_json: bool = False) -> list[str]:
    refs = scout(query, limit)
    for i, ref in enumerate(refs, 1):
        ext = ".webp" if ".webp" in ref["image_url"] else ".png"
        name = f"ref_{i}_{re.sub(r'[^a-zA-Z0-9]', '_', ref['title'][:25])}{ext}"
        if download(ref["image_url"], dest_dir / name):
            ref["local_path"] = str((dest_dir / name).resolve())
    if output_md:
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(markdown(refs, query), encoding="utf-8")
    if as_json:
        return [json.dumps(refs, indent=2)]
    out = [f"scouted {len(refs)} references" + (f", page: {output_md}" if output_md else "")]
    return out + [f"  [{r['source']}] {r['title']} -> {r.get('local_path', r['image_url'])}" for r in refs]
