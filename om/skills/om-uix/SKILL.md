---
name: om-uix
description: >-
  UI style hub for om, for web and mobile. 117 MIT styles and themes from bergside/awesome-design-skills (67 style packs) and Nutlope/hallmark (50 OKLCH themes and anti-slop gates). Use when building, styling or redesigning a UI with a named look (neobrutalism, glassmorphism, Swiss grid, bento, editorial, clay, retro, terminal...).
---

# om-uix: UI style hub

Licences: MIT only. `licenses/` holds both licence texts; keep them with the catalog.
- `catalog/typeui-styles/<slug>/` (SKILL.md + DESIGN.md), from [bergside/awesome-design-skills](https://github.com/bergside/awesome-design-skills).
- `catalog/hallmark-themes/<slug>.md` and `references/` (gates, craft, layout...), from [Nutlope/hallmark](https://github.com/Nutlope/hallmark).

## Commands
Run from this skill's own folder (the folder holding this file), whatever tool loaded it:
```bash
python3 scripts/style_hub.py list              # all styles and themes
python3 scripts/style_hub.py search <word>     # e.g. neobrutalism, glass, bento, mobile
python3 scripts/style_hub.py show <slug>       # tokens, type scale, components, do and don't
```

## Families
| Family | Style packs | Hallmark themes | Look |
| --- | --- | --- | --- |
| Neobrutalism | `neobrutalism`, `brutalism`, `bold` | `brutal`, `manifesto`, `broadside`, `sticker` | Thick black rules, hard offset shadows, sharp corners, vivid fills on warm paper |
| Swiss grid | `clean`, `minimal`, `modern`, `mono` | `grid`, `specimen`, `werkstatt`, `almanac` | Visible 12-column grid, grotesque sans + mono, black and white + one accent |
| Glass | `glassmorphism`, `sleek`, `cosmic`, `pulse` | `refract`, `lumen`, `dusk`, `midnight` | Blurred layered surfaces, 1px light borders, strict contrast |
| Bento SaaS | `bento`, `shadcn`, `impeccable`, `stitch`, `levels` | `studio`, `formwork`, `console`, `cobalt` | Multi-span grid cells, hairline borders, tonal elevation |
| Editorial | `editorial`, `paper`, `storytelling`, `terracotta` | `editorial`, `newsprint`, `vellum`, `atelier` | Display serif + clean sans, wide margins, warm paper |
| Retro and print | `retro`, `riso`, `dithered`, `pacman`, `sega`, `tetris` | `riso`, `halftone`, `pasteup`, `arcade`, `darkroom` | Risograph grain, halftone, 8-bit shapes |
| Tactile | `claymorphism`, `neumorphism`, `skeumorphism`, `friendly` | `kiln`, `terrazzo`, `coral`, `bloom` | Soft double shadows, depth, press states |

## Steps
1. Load the style first: `show <slug>`. Use its tokens; do not invent new ones.
2. Apply the craft gates in `catalog/hallmark-themes/references/gates.md` and `craft.md`: no default purple gradients, no cards inside cards, no fake side stripes on non-alerts, no low-contrast text.
3. Prove it in a real browser: video for scrolling and motion, screenshots for each state (om rule 1.1). On a Mission each interaction is a matrix line.
