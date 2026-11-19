---
name: free-ui-ux-scout
description: Mandatory TeamUIX companion skill for Layer 0 design scouting, real-reference discovery, interactive carousel visual blueprints, and anti-slop grounding using 100% free tools (`oway scout`, `oway style`, and Chrome DevTools MCP on Godly, Land-book, Mobbin, Refero, and live apps).
---

# Free UI/UX Design Reference Scout

Grounded in [Oway UIX](../oway-uix/SKILL.md) and Oway's design rules: eliminate generic AI aesthetic slop by starting every UI task with **up to 6 real, browser-verified references**, captured live on disk and presented visually before touching layout or code.

100% free workflow — zero paid API keys, zero paywalls, zero invented mockups.

---

## Core Non-Negotiables

1. **Scout before designing (Layer 0)**: Read `spines/01-intent.md` first (never redo product scope), then bring up to 6 deliberately different real references, each with a concise caption and explicit trade-off.
2. **Real pages in a real browser**: References are opened in a real browser and screenshotted into `_oway/design/references/` (`you-<source>.png` or `competitor-<source>.png`), never generated as AI pictures.
3. **Interactive visual blueprint**: Present curated references to the Owner in a visual carousel artifact (alongside the extracted layout rhythm, surface hierarchy, palette, and typography plan) so the Owner can react directly (`"this is mine"`, `"not this"`, `"mix 2 and 4"`, or sketch directly on the screenshot).
4. **Name what you feel**: When the Owner describes a feel or effect without naming it, translate it into exact visual vocabulary using [visual-choices](../oway-uix/references/visual-choices.md) or ask for a short screen recording.
5. **Style packs & anti-slop discipline**: Ground directions in the 117 MIT style packs and 50 color themes via `oway style`, and enforce [craft gates](../oway-uix/references/craft.md) and [critique rubric](../oway-uix/references/critique-rubric.md).

---

## Step-by-Step Workflow

### 1. Scout Real References (Free Sources)

#### Method A: Built-in Oway CLI (`oway scout` + `oway style`)

1. Run deterministic reference discovery against Godly and Land-book:
   ```bash
   oway scout "<domain or aesthetic query>" --out _oway/design/references --limit 6
   ```
   See [inspiration-library](../oway-uix/references/inspiration-library.md) for cached catalog details and supported queries.
2. Search the 117 MIT style packs and 50 color themes before inventing tokens:
   ```bash
   oway style --search "<aesthetic or surface keywords>"
   ```

#### Method B: Live Browser Capture via Chrome DevTools MCP

When scouting dynamic apps, SaaS workflows, Mobbin/Refero flows, or competitor URLs:
1. Open the target URL with `chrome-devtools-mcp` (`new_page`).
2. Capture full-viewport and interaction states with `take_screenshot`, saving into `_oway/design/references/` with source-attributed names (e.g. `competitor-linear-inbox.png`).
3. Measure actual computed typography, spacing, surface colors, and contrast rather than guessing from memory.
4. Close the temporary tab with `close_page` when capture finishes.

---

### 2. Present the Visual Carousel & Style Blueprint

Save screenshots in `_oway/design/references/` and present up to 6 diverse directions in a `carousel` block (separated by `<!-- slide -->`) in your response or visual artifact. Notice in markdown carousels: use real paths that exist on disk (or bare `<img src="...">` tags in HTML prototypes) — never invent dead file paths.

Include alongside the references:
- **Reference summary**: source URL, layout structure, navigation mechanism, surface hierarchy, and why it fits `spines/01-intent.md`.
- **Style pack & theme candidate**: matching `oway style` pack and 5a Register draft (density, type feel, light/dark polarity, mood, one signature element, explicit anti-goals).
- **Invitation to react**: ask the Owner to pick, reject, mix two mechanisms, or annotate/sketch directly on any captured screenshot.

---

### 3. Hand Off Into the 8 Oway Design Layers

Once Layer `0` (References + words) and Layer `5a` (Register) are aligned with the Owner:
1. Hand off cleanly through [oway-uix](../oway-uix/SKILL.md):
   - Layer `1`: Task map (no visuals yet)
   - Layer `2`: Screen map + flows (no layout yet)
   - Layer `3`: Wireframe (grey boxes, real labels, zone names; no color/fonts/icons yet)
   - Layer `4`: Behaviour (clickable grey prototype with Playwright journeys & test IDs in `_oway/design/versions/vN/`)
   - Layer `5b`: Token sheet (DTCG JSON, every token traceable to measured reference or register)
   - Layer `6`: High fidelity (real frontend screens built by `uix-worker`, preserving Layer 4 journeys)
   - Layer `7`: Motion (bounded transitions derived from motion tokens)
2. Never lock a screen on self-judgment: require an independent `QATester` rubric score (`min >= 3`, `mean >= 3.5` across [critique-rubric](../oway-uix/references/critique-rubric.md)) and real browser screenshots tied to the commit.
