---
name: oway-uix
description: Design or revise a product experience from real references through task flows, grey behavior prototypes, and the real frontend, with a library of 117 MIT style packs and themes and anti-slop gates; full mode for Oway projects, light mode for om; handles responsive and mobile evidence explicitly.
---

# Design the experience
Created: unknown · Last edited: 2026-10-23T14:35:00Z

Pull request visual proof comes from CI artifacts tied to the PR commit; never use hand-attached images as proof. CI uses its own pinned Playwright, not the project's, and a journey or audit counts as PASS only with screenshots for every viewport; BLOCKED or PARTIAL means nothing was proven. That CI job is evidence, not a gate: read its summary and artifacts before calling a screen done. Keep journey names on one line with no control characters.

Read only what the current step needs, once per session: the [agent contract](../../engine/CONTRACT.md) and [method section 6](../../docs/METHOD.md) (that section only). Start from the user's goal and the locked layers in `docs/spines/03-EXPERIENCE.md`. Advance only the layer affected; layers 0-4 are disposable grey work, 5b-7 are the real frontend. A tweak inside locked zones and tokens is applied directly; a changed flow, zone, token or register reopens only the dependent layers, and you run `impact.py` and show the map first.

## Start from the problem, not the look

Before you draw, read `01-intent` (or `docs/spines/01-INTENT.md` in v0.3 checkouts): `LeadProduct` has already written who it is for, what job they are trying to get done, and how we will know it works. UIX reads it before drawing and never redoes it; any gap goes back to `LeadProduct`. `KeeperUIX` watches that design versions and screens do not drift apart. If the user cannot answer a design question, offer your concrete reading of the problem and let them correct it. Do not ask for a blank brief.

**Name what you feel:** if the user likes an effect without knowing its name, name it or ask for a screen recording.

Then classify the request, because each kind keeps something different:

| Kind | Changes | Must stay the same |
| --- | --- | --- |
| behavior | rules, states, permissions, flows | locked look; design these with the object model first (below) |
| layout | placement, grouping, order on a screen | every action, field, URL and step order for every role (list them first, then check them after) |
| appearance | type, colour, density, imagery | layout and behavior |
| content | words, labels, data shown | layout, behavior and stored data |
| motion | animation of existing behavior | behavior |

A request worded as visual can still be a behavior change (a new status, a new permission). Classify it by its effect, not its wording. An appearance tweak inside the locked visual direction is applied directly, without a comparison. Compare options only when the request would reopen that direction, and say so first. Behavior work such as approvals, permissions and audit trails is designed from the back: states, who may do what, what is recorded. Then come the screens.

## Show the artifact that answers the open question

Pick the artifact by the question the user must answer now. This chooses what to build within the layer you are working in; it never skips a layer whose lock is still open:

| Open question | Artifact |
| --- | --- |
| How does someone move through the product? | journey across screens |
| What happens under each condition? | state diagram (Mermaid) with a permission table |
| Where do things go on one screen? | grey wireframe |
| Which direction feels right? | side-by-side comparison of real pages, with your recommendation marked |
| Does it actually work? | clickable prototype with named states (see behavior coverage) |

Tell the user in one line: the current question, what you will show next, and the one decision you need from them. Explain the overall path once, in plain words, only when a new product starts. Pause for real choices: direction, scope, business rules, taste. Continue authorized craft work and checks without asking. Locking a layer still needs the user's recorded approval. Connected screens that serve one task are reviewed together as a journey, not approved one by one. If they want to go back, go back without arguing.

## Keep screens from rewriting the data

For each screen, write a data inventory in `docs/prototypes/<screen>/data-inventory.md` when you draw its wireframe: what it reads, what it writes, and which noun in `docs/spines/02-OOUX.md` each item comes from. A field the screen needs but the model lacks goes to the object model as a data request. It does not become a migration on the spot. Keep these four apart:

- **Domain:** the lasting nouns, their states and rules.
- **Storage:** the tables and columns.
- **API:** the response shape.
- **Screen state:** open dialogs, drafts, selection, filters.

They often differ, so mock data is not a schema. Facts that must not change later, such as an issued total or a snapshot of an address, are stored. Display-only values, such as "due in 3 days", are calculated. Anything you filter, enforce or report on gets a real field, not loose JSON.

## Record decisions so nothing is lost

As you go, record each design decision with `memlog.py`:

- **The user's choices**, in their words.
- **Your own defaults**, with status `Delegated`.
- **Questions only the user can answer**, tagged `open-question`.

The session pack shows only the last few ledger headers, so also keep the open questions and your unconfirmed defaults in the checkpoint's `pending` list, along with the next action. Use `cgspec_hook.py checkpoint --update-file`. Remove an item from `pending` when the user answers it. A fresh session then resumes from the checkpoint, reading `docs/_memlog.md` only for detail, without the user pasting the brief again.

## Push back on design shortcuts

Apply the contract's push-back rule to these design shortcuts:

- Asking for high fidelity before the task and flow are agreed.
- Approving a prototype without trying the main journey.
- Reacting only to colour when the problem is the workflow.
- Asking for a database change because a screen moved.


## What to do at each layer, and what to load

Prototype files other than ordinary Markdown need the active change scope. Before a layer lock, include `docs/prototypes/_snapshots/<screen>-v*.html` in the approved slice scope as well as that screen's sources and journeys; if missing, amend the scope through the existing approval path before cutting the snapshot. Use the tier appropriate to the total change size. The lock approval and frozen hash do not replace scope approval. Journey JSON is test material and does not require another test of itself.

| Layer | Do | Not yet | Load |
| --- | --- | --- | --- |
| 0 References | Start from the user's [personal inspiration library](references/inspiration-library.md) when it exists, then find up to 6 contrasting **real** references, with links and screenshots in `docs/prototypes/_vision/`, actually displayed per the [visual-choice guide](references/visual-choices.md); measure those the user likes. Sketching on a screenshot beats ranking options. Search with available web tools and project links. Also run `oway style search <word>` for the look the user names and offer the 2-3 closest [style packs](#style-library) beside the real references, built as real pages like the references, so the user reacts to looks they can see. If original images or video matter, align the user-visible IMAGE-WORD card before generation. If access fails, record the gap, invite optional links, and continue independent grey work without inventing references or locking reference-derived choices. | Any design of ours | [inspiration library](references/inspiration-library.md), [reference-extraction](references/reference-extraction.md); load [IMAGE-WORD and motion](references/image-word-and-motion.md) only when media matters; [RES-001](../../docs/_cgspec/02-research/RES-001-ui-design-systems-and-surface-profiles-benchmark.md), [RES-004](../../docs/_cgspec/02-research/RES-004-vibecoded-design-tells-and-high-craft-ergonomics.md) |
| 0-3 Compare directions | Only when a real direction choice is open: build 2-3 quick variations of the key screen that differ in mechanism (structure, density, navigation, type, mood), not just colour or button position. Make them real HTML pages in `docs/prototypes/_vision/variations/`, open them in the browser and screenshot them side by side. Give each one line on what it bets on, and mark your recommendation. The user reacts ("this one", "mix 2 and 3"); iterate on the winner and delete the rest. Use more only for a stated reason. For a vague request, first offer your reading of the problem or a cheap labelled sketch. | Final visual polish or locked tokens | [craft](references/craft.md) |
| 0-1 Register (5a) | Write the one-paragraph register (density, type, stance, mood, accent, signature element, avoid, deliberate choices), show it, lock it with the user's approval. | Token values | [register](references/register.md) |
| 1 Tasks | Actors and tasks in the spine, each with frequency and device. | Visuals | — |
| 2 Screens and flows | One row per screen with its main need (the focal point). | Layout | [craft](references/craft.md) section 1 |
| 3 Wireframes | Grey shell, zone IDs, real-looking data in realistic amounts, density from the register; the screen's data inventory. | Colour, fonts, icons | [craft](references/craft.md) sections 1-5, 8 |
| 4 Behavior | Clickable grey prototype with the [tweaks panel](references/tweaks-panel.js) included, so the user can try type, density, accent, radius and light/dark live and paste the values back, all states, `data-testid` on every control; journeys in `docs/prototypes/<screen>/journeys/`; `visual_audit.py` and `journey.py` provide quick iteration, while `verify.py` supersedes them as the single pre-show/pre-claim gate before showing a screen or claiming it works. Cut a snapshot with `bundle_prototype.py` when the user locks the layer. | Final look | [behavior coverage](references/behavior-coverage.md), [RES-002](../../docs/_cgspec/02-research/RES-002-anti-slop-constrained-ui-and-deterministic-gates.md) |
| 5b Token sheet | Derive every token from the register and measured references; each value says where it comes from (a style pack or theme counts as a source: name it with its licence). Set `design_tokens` in `docs/_cgspec/project.json` to the token sheet's project-relative path, so visual audit checks the intended sheet. | Screens | [tokens template](references/tokens.dtcg.json), [reference-extraction](references/reference-extraction.md), [craft](references/craft.md) sections 3-7 |
| 6 High fidelity | Real frontend, one key screen first, the tweaks panel kept until the user locks the look (then removed), components from recipes; a screen is locked only after a different reviewer scores its screenshots against the [critique rubric](references/critique-rubric.md) with no score below 3 (`min >= 3`) and mean at least 3.5 (`mean >= 3.5`), and after applying the [anti-slop gates](#style-library). | Layout changes | [craft](references/craft.md), [components](references/components.md), [critique rubric](references/critique-rubric.md), [RES-005](../../docs/_cgspec/02-research/RES-005-anthropic-design-plugin-structure-and-skills.md) for copy and handoff gaps |
| 7 Motion | Behaviors from layer 4 animated with motion tokens only. If media and text carry a shared story, lay out a timed storyboard against the clip before implementing it. | New behaviours | [IMAGE-WORD and motion](references/image-word-and-motion.md) when media matters; [RES-006](../../docs/_cgspec/02-research/RES-006-scroll-craft-skill-standard-and-verification.md) for scroll-driven pages |

Layers 0 to 4 stay a cheap grey prototype because screens change many times; from layer 5, design is built in the real frontend so nothing is rebuilt. The journeys written at layer 4 run unchanged on the real frontend; if it behaves differently, the build fails.

Each version lives in `_oway/design/versions/vN/` with its prototype, screenshots and a short note; a new version is cut only when a layer is locked. Each locked screen keeps a baseline (journeys + screenshots per state) in `_oway/evidence/visual-baselines/`; a later difference fails unless the user approves a new baseline.

## Style library
<a id="style-library"></a>

The unified style library carries two catalogs and one workflow, all MIT (commercial-friendly, no duty to publish your code):
1. **Style packs:** [bergside/awesome-design-skills](https://github.com/bergside/awesome-design-skills), 67 folders, each with a `SKILL.md` and a `DESIGN.md` (tokens, type scale, component anatomy, do and don't).
2. **Hallmark:** [Nutlope/hallmark](https://github.com/Nutlope/hallmark), 50 OKLCH material themes plus the 65 anti-slop browser gates (`gates.md`, `craft.md`, the other references, `sloplint.mjs`).

The catalog is not in Git and not in any project: `oway style fetch` downloads it once per machine, at pinned upstream commits, into `~/.cache/oway/styles` (or `$OWAY_STYLES`), with both licence texts. `oway` is the Oway tool (`python3 engine/oway` in a checkout; `om/bin/oway` is a launcher that `om/sync-om.sh --tools oway` puts on your PATH).

### Commands
```bash
oway style fetch                # once per machine
oway style list                 # all 117 packs and themes
oway style search <word>        # e.g. neobrutalism, glassmorphism, swiss, bento, mobile
oway style show <slug>          # full SKILL.md, DESIGN.md, OKLCH tokens, CSS checklists
oway style show neobrutalism    # also: brutal, glassmorphism, bento
```

### Core aesthetic archetypes
| Aesthetic family | Style pack slug | Hallmark theme | Key visual DNA |
| --- | --- | --- | --- |
| **Neobrutalism / Brutalism** | `neobrutalism`, `brutalism`, `bold` | `brutal`, `manifesto`, `broadside`, `sticker` | Thick 2px-4px solid black rules, hard offset shadows (`4px 4px 0 #000`), zero or sharp radius, vivid acid/primary fills (`#FDC800`, `#FF5722`) on warm paper (`#FBFBF9`). |
| **Swiss / International grid** | `clean`, `minimal`, `modern`, `mono` | `grid`, `specimen`, `werkstatt`, `almanac` | Exposed 12-column mathematical grid, grotesque sans + tabular mono, high-contrast black/white + single surgical accent. |
| **Glassmorphism and liquid glass** | `glassmorphism`, `sleek`, `cosmic`, `pulse` | `refract`, `lumen`, `dusk`, `midnight` | Translucent layered surfaces (`backdrop-filter: blur(16px)`), 1px specular border highlights (`rgba(255,255,255,0.18)`), strict WCAG contrast guards. |
| **Bento and modular SaaS** | `bento`, `shadcn`, `impeccable`, `stitch`, `levels` | `studio`, `formwork`, `console`, `cobalt` | Asymmetric multi-span CSS Grid cells, 1px hairline borders, tonal surface elevation without heavy drop shadows. |
| **Editorial and magazine** | `editorial`, `paper`, `storytelling`, `terracotta` | `editorial`, `newsprint`, `vellum`, `atelier` | High-contrast display serif paired with crisp sans body, generous negative space, warm paper stock. |
| **Retro / Y2K / print craft** | `retro`, `riso`, `dithered`, `pacman`, `sega`, `tetris` | `riso`, `halftone`, `pasteup`, `arcade`, `darkroom` | Duotone risograph grain, halftone dots, 8-bit/arcade geometry, or 80s/Y2K postmodern shapes. |
| **Tactile / clay / neumorphic** | `claymorphism`, `neumorphism`, `skeumorphism`, `friendly` | `kiln`, `terrazzo`, `coral`, `bloom` | Soft inner+outer dual shadows, tactile 3D surface depth, physical press states. |

### Workflow
1. **Select or propose style archetypes first.** Run `oway style show <slug>` to load the exact `SKILL.md` and `DESIGN.md`. If the user wants visual references from live websites alongside the style tokens, pair with `free-ui-ux-scout` or the `stitch` MCP (`upload_design_md` with the pack's `DESIGN.md`) when they are installed; otherwise use the browser. Nothing here depends on them.
2. **Enforce the anti-slop craft gates.** Read `hallmark-themes/references/gates.md` and `craft.md` in the catalog, and run `hallmark-themes/scripts/sloplint.mjs` when Node is available. Never fall back to uncurated AI purple gradients, nested cards-in-cards ("Cardocalypse"), fake `border-l-4` side stripes on non-alerts, or low-contrast text. The gates join the critique rubric. A flagged choice the user wants is recorded under "Deliberate choices", never silenced.
3. **Exhaustive interaction and visual proof.** Prove the implemented design in a real headless or live browser across every user interaction: a **video** for full-page scrolling and motion, high-resolution captures and live outputs for interactive flows.

How it fits the layers: a pack or theme is a **starting register and token source**, not a finished design. It never replaces the problem, the references or the user's reaction. Layer 0 offers the closest packs beside the real references; layers 5a and 5b record the pack in "Deliberate choices" and in the token sheet's provenance.

## Reference scouting (free)

From the free-ui-ux-scout skill, kept whole. It removes generic "AI aesthetic slop" (purple gradients, uncurated Inter fonts, low-contrast cards) by grounding every design in real, striking references. It is a 100% free workflow: no paid subscription, no API key, no paywall. Use it for layer 0 (References) and for the light mode's references step.

### Non-negotiables
1. **Research before implementation.** Never design from raw memory or default LLM habits. Scout references first.
2. **Visual proof in a carousel.** Present 3-5 real visual references to the user, before or alongside implementation, in a carousel artifact where the host has one (Antigravity), else side by side in the browser or an artifact. Each is a real screenshot with its source URL.
3. **Multi-source free scouting:**
   - **Godly.website:** cutting-edge web aesthetics, micro-interactions, dark and light themes, typography craft.
   - **Land-book.com:** production SaaS, dashboards, landing pages, conversion patterns.
   - **Mobbin and Refero via Chrome DevTools MCP:** live mobile (iOS/Android) and web-app flows browsed on the local machine, with zero subscription fees.
4. **Anti-AI-slop directives:**
   - Grounded palettes (no generic purple or blue gradient buttons).
   - Crisp hairline borders (`border-neutral-200 dark:border-neutral-800`).
   - Distinct `:hover`, `:focus-visible` and `:active` states.
   - Responsive, touch-friendly layouts (minimum 44x44px mobile touch targets).

### Workflow
**Step 1: scout references.**
- *Method A, instant multi-source scout CLI* (free, no key; the owner's `design_scout.py`, now part of the Oway tool):
  ```bash
  oway style scout "<query>" --dest-dir references --output-md design_references.md
  ```
  Examples: `oway style scout "fintech dashboard"`, `"mobile onboarding"`, `"dark mode analytics"`. It downloads 3 screenshots per source (godly.website, land-book.com; `--limit` changes it) and writes the references page: carousel block, breakdown table, plain list, anti-slop directives, and a token plan to fill in. In Antigravity put the page and images in the conversation's `<appDataDir>/brain/<conversation-id>/` folder. Scraped screenshots are references only; the rights belong to the sites. If the sites change their markup and the scout returns nothing, use Method B.
- *Method B, direct live browsing via Chrome DevTools MCP,* when a specific production site or public Mobbin/Refero page is asked for: `new_page` with the URL, then `take_screenshot` (the MCP saves it to the conversation's `brain/` folder, free), then `close_page`. With no such MCP, use the browser tool you have.

**Step 2: present the interactive carousel artifact.** In the conversation's artifact folder (`design_references.md`), write:
````markdown
# Curated Visual Design References

```carousel
![Reference 1: High Craft Layout]( /path/to/references/ref_1.webp)
<!-- slide -->
![Reference 2: Clean Data Table]( /path/to/references/ref_2.png)
<!-- slide -->
![Reference 3: Mobile Flow]( /path/to/references/ref_3.png)
```

## Design synthesis and token plan
- Dominant style: minimalist high-contrast surface with hairline borders.
- Palette: dark surface `#0A0A0C`, card `#141417`, border `#222227`, accent `#2563EB`.
- Typography hierarchy: tracking-tight headings, distinct mono badges, muted auxiliary labels.
````
In real use write each image path with no space after the opening bracket (the space above only keeps this skill's own link check quiet). Point the user to the artifact so they can inspect the inspiration. Where the host has no carousel, show the same images side by side in the browser and link the file.

**Step 3: align and implement.**
1. Ask or confirm which aesthetic direction the user prefers, or synthesize the sharpest elements. Write the design synthesis and token plan from the references you scouted (the page's default palette is only a starting point).
2. Implement with modern web primitives (Tailwind CSS, clean semantic HTML, or the target framework).
3. Validate against modern web guidance: WCAG AA contrast, smooth 150-200ms transitions, fluid responsiveness across viewport sizes.

## Light mode (om)

Use light mode when working under om (`om/rules/AGENTS.md` is loaded) or when the project has no `docs/spines/`. It behaves the same as full mode in every way that the user sees, and drops what needs the Oway engine and project files.

**Kept, in this order:**
1. **Problem first.** One line: who it is for, the job, how we will know it works. Offer your reading and let the user correct it; never ask for a blank brief.
2. **Classify the request** by its effect, with the kind table above (behavior, layout, appearance, content, motion). **Name what you feel:** if the user likes an effect without knowing its name, name it or ask for a screen recording.
3. **References first.** Scout (see Reference scouting) and show up to 6 real, captioned references: real pages opened in the browser and screenshotted, each saved with its source URL. Add the 2-3 closest style packs. The user reacts ("mine", "not this", "mix 2 and 4"); sketching on a screenshot beats ranking options. Never a generated picture instead of a page. If original image or video assets matter, align the `IMAGE-WORD` card first and record asset provenance and rights (references are inspiration only, not reuse rights).
4. **Variations only when the direction is open:** 2-3 real pages that differ in mechanism (structure, density, navigation), not in colour. Iterate on the winner, delete the rest.
5. **The artifact that answers the question** (the table above): journey, state diagram with permission table, grey wireframe, side-by-side, clickable prototype.
6. **Register in one paragraph,** then build in the real frontend with the chosen tokens. Propose an existing design system only when its permissive license, installable typed components, and machine-checkable / machine-readable tokens are verified; for a look with no package, extract tokens with `getdesign`.
7. **Review:** a different reviewer (`om-review`, or another model) scores the screenshots against the [critique rubric](references/critique-rubric.md): no score below 3, mean at least 3.5. Video for scroll and motion, screenshots for every state and viewport.

**Dropped:** the locked layers and approvals, `docs/spines/` and data inventories, `impact.py`, `verify.py`, `visual_audit.py`, `journey.py`, `memlog.py`, checkpoints, snapshots, CI baselines and the tweaks panel (unless asked). Notes, references and decisions go in a `design-notes.md` next to the work, or in the Mission plan.

**By size:**
- **Quick** (restyle, one screen): problem line, references, a style, the screen, proof (screenshots per viewport, video if it scrolls or moves). No layers.
- **Task:** add a grey wireframe before high fidelity when the layout is open.
- **Mission:** use the layers table. Each layer's output is a proof-matrix line in `om-plan`; the user's OK on the plan covers the locks. For a new product with many screens, use full mode in an Oway project instead.

## Rules

- The AI leads: bring references and options; do not ask the user to research or write the brief.
- Apply the [visual-choice guide](references/visual-choices.md) whenever images help a brainstorming or design choice: display real images beside labelled options, even before layer 0 - disk-only links/screenshots do not count. For a new product or direction, show up to 6 real references from anywhere public before your own design (marketing pages, docs, app-store screenshots, review articles, Dribbble/Behance, image search), each saved with its source URL, and let the user react before building variations. Reuse already-chosen references; do not reopen this for a tweak within locked choices.
- "Grey" means no brand colour yet, not ugly. Early prototypes and variations still need clean type, spacing and alignment (see craft.md), or the user cannot judge the experience behind them.
- A design proposal or variation is always a real page you built, opened in the browser tool and screenshotted - never a generated image standing in for a prototype, and never a long description instead of showing it. Separately, generated image/video *assets* for the product itself (landing pages, immersive spaces) are fine once real references and the IMAGE-WORD card are agreed: show the exact generation prompt, pass it unchanged to a reachable generator (connected Antigravity from any lead model, else a direct tool such as Codex image generation - never paraphrased through an intermediate model), then integrate the result with its provenance and rights recorded and its responsive crops/motion checked. Follow [IMAGE-WORD and motion](references/image-word-and-motion.md). A paid service or new provider needs the user's yes first, with its cost and license implications stated.
- Reference sources besides live products: Dribbble, Pinterest, Mobbin and similar galleries for references; 21st.dev and Taste Skill for component and layout ideas. Use them as references only; a component copied without mapping it to the project's tokens makes the design drift (section 6b), and its license must be checked before any code is reused.
- Optional polish check: on a web project, `npx impeccable detect <dir or http://localhost:PORT>` (Apache-2.0, free; run `npx impeccable telemetry off` first) lists generic-look patterns. Treat findings as warnings inside the locked register, like `visual_audit.py`; do not install its skills alongside this one without the user's yes, because two design instruction sets pull in different directions.
- An existing design system is an option only when scripts can check it: its installable typed components, machine-readable tokens, lint rules where available, and permissive license are verified (section 6b). For a look with no package, extract tokens instead (`getdesign` skill) or derive project tokens with provenance.
- Generic-look warnings are defaults to challenge, not taste decisions. A flagged choice the user wants is recorded under "Deliberate choices" in the register; never silence a warning the user has not seen.
- Never claim a screen is finished without the screenshots and the rubric result; show the screenshots to the user.
