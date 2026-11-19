---
name: team-uix
description: UIX team contract: 8 design layers, real references, style packs, and pre-lock QA verification
type: team
state: draft
created: 2026-11-19
approved: no
owner: LeadUIX
updated: 2026-11-19 by LeadOway
proof: none
---

# Team UIX
Created: 2026-11-19T15:00:00Z · Last edited: 2026-11-19T15:00:00Z

Designs the user experience with the owner across Oway's 8 design layers (`0, 5a, 1..4, 5b, 6, 7`), starting from `spines/01-intent.md` and real browser references, iterating in versioned grey behavior prototypes, applying verified MIT style packs and design systems, and locking every screen only after independent QA scoring.

## Members
| Role | Card | Model |
| --- | --- | --- |
| LeadUIX | [leaduix.md](leaduix.md) | Decided at setup |
| AdvisorUIX | [advisoruix.md](advisoruix.md) | Dedicated advisor to LeadUIX |
| LeadUIXBoard | [leaduixboard.md](leaduixboard.md) | Decided at setup |
| LeadUIXScout | [leaduixscout.md](leaduixscout.md) | Decided at setup |
| ScoutUIX | [scoutuix.md](scoutuix.md) | Short-lived explorer |
| UIX worker (UIX1, UIX2...) | [uix-worker.md](uix-worker.md) | Build prototypes, tokens, and screens |
| KeeperUIX | [keeperuix.md](../keeper/keeperuix.md) | Read-only watcher under LeadKeeper |

## Shared Skills Loaded by TeamUIX
- [oway-uix](../../skills/oway-uix/SKILL.md): canonical 8-layer design workflow, `Not yet` rules, Layer 4 -> Layer 6 parity, and 65 anti-slop browser checks.
- [free-ui-ux-scout](../../skills/free-ui-ux-scout/SKILL.md): free real-reference scouting via `oway scout`, `oway style` (117 MIT style packs + 50 themes), and Chrome DevTools MCP live capture with interactive visual carousel blueprints.
- [frontend-ui-engineering](../../skills/frontend-ui-engineering/SKILL.md): disciplined component engineering, states, accessibility, and design-system hygiene.
- [browser-testing-with-devtools](../../skills/browser-testing-with-devtools/SKILL.md): live browser inspection, DOM/style measurement, responsive screenshots, and journey verification.

## How the work is split across the 8 layers
1. **Intent first**: read `spines/01-intent.md` before drawing; send scope gaps back to `LeadProduct`.
2. **Layer 0 (References + words) & Layer 5a (Register)**: `LeadUIXScout` + `ScoutUIX` capture up to 6 contrasting real browser references (`_oway/design/references/`) and `oway style` packs; `LeadUIX` presents them in a visual carousel, invites screenshot sketching, and uses `Name what you feel` or a screen recording to lock the aesthetic register.
3. **Layers 1 to 4 (UX before UI)**: `uix-worker` builds the task map (`1`), screen map + flows (`2`), grey wireframe with real labels (`3`, no colors/fonts/icons), and clickable grey behavior prototype + Playwright journeys (`4`). `LeadUIXBoard` compares 2–3 variants differing in layout/navigation mechanism before locking.
4. **Layers 5b to 7 (Tokens, Real Frontend, Motion)**: `uix-worker` authors DTCG `tokens.dtcg.json` (each token traced to register/reference, or `getdesign` / machine-checkable permissive design systems) and builds real frontend screens with mocked data inside `_oway/design/versions/vN/` + code, preserving Layer 4 Playwright journeys identically.
5. **Independent Lock**: `QATester` (never UIX) scores real browser screenshots against the critique rubric (`min >= 3`, `mean >= 3.5`), saving frozen visual baselines to `_oway/evidence/visual-baselines/` before `LeadUIX` hands off to `LeadDev`.

## Who talks to whom
Only `LeadUIX` talks to the owner, `LeadOway`, `LeadProduct`, `LeadDev`, and `LeadQA`. `UIX1..N`, `ScoutUIX`, `LeadUIXScout`, `LeadUIXBoard`, and `AdvisorUIX` communicate within TeamUIX only; `KeeperUIX` reports to `LeadKeeper` only.

## Limits
200 characters max per agent-initiated message; max 3 rounds per board; zero generated pictures or unverified images accepted as proof; DevFrontend never modifies locked UIX tokens without `LeadUIX` approval.
