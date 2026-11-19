---
name: oway-forge
description: Turn a new product idea or feature request into researched intent, actors, scope, and an object model before design or build.
---

# Forge product intent (`oway-forge`)

## 1. Oway v0.4 Product Scope & Spines (`LeadProduct` + `_oway/spines/`)

In Oway v0.4, `LeadProduct` runs Stage 1 Brainstorming with the owner using [interview-me](../interview-me/SKILL.md), [idea-refine](../idea-refine/SKILL.md), and [spec-driven-development](../spec-driven-development/SKILL.md) (watched read-only by `KeeperProduct` under `LeadKeeper`):

1. **Three First Parts in `_oway/project.md` (and Every Milestone/Slice)**:
   - Every project, milestone, and slice file starts at the top in this exact order:
     1. **`## 1. The goal`**: one clear sentence.
     2. **`## 2. What you get`**: concretely what the owner can open, click, or run at the end.
     3. **`## 3. The proof you will have`**: the main checks and their proof medium (video, screenshot, query/command output).
2. **Commercial Research (`LeadProductScout` + `ScoutProduct`)**:
   - Determine the goal type (`money`, `learning`, `personal`, `client`). For a `money` goal, `LeadProductScout` dispatches `ScoutProduct` explorers to write `_oway/research/RES-NNN-<slug>.md` (competitors, who pays, pricing, demand evidence, risks) with a `## Sources` section containing full `https://` links (enforced by `oway doctor`).
3. **The Product Spines (`_oway/spines/`)**:
   - Write `_oway/spines/01-intent.md` (why, for whom, job to be done, success criteria, anti-goals, business model, v1 boundary, parked list).
   - Write `_oway/spines/02-objects.md` (domain objects, states, rules, permissions, and task-to-object trace; field lists move to the schema + tests once Dev starts).
   - Write `_oway/spines/05-delivery.md` (milestone order, risks, KPIs; each phase is a milestone file `_oway/milestones/mN-<slug>.md` starting with `## 1. Main goal`, `## 2. What you get`, `## 3. The proof you will have`).
   - Run `oway headers`, `oway index`, and `oway doctor` before handing off to `LeadUIX` (Stage 2 Design, if there is a UI) or `LeadDev` (Stage 3 Architecture).

---

## 2. Core Principles & Legacy v0.3 Compatibility

Read only what the current step needs, once per session: the [agent contract](../../engine/CONTRACT.md) and relevant existing spines. Determine the goal type: money, learning, personal, or client. For a money goal, research who pays, competing options, price, demand evidence and risks in `_oway/research/RES-NNN-<slug>.md` (or `docs/_cgspec/02-research/RES-NNN-<slug>.md` on v0.3 layouts), with source links and dated facts. State uncertainty; do not invent market validation.

Write `_oway/spines/01-intent.md` (`docs/spines/01-INTENT.md` in v0.3) with the goal, actors, real tasks, anti-goals, v0.1 boundary and parked ideas. Write `_oway/spines/02-objects.md` (`02-OOUX.md` in v0.3) with nouns, attributes, relations, hierarchy, permissions and important states. Trace each actor task to its nouns; check that none are orphaned. In a larger project, update only the relevant spine parts and links rather than rewriting all of them.

Open with the orientation from the contract: in at most five short lines, what we will do together, how this first part works, and what you need from them. Give a short progress update only when something materially changes or the user asks; do not prefix every reply. When this part is confirmed, move into design without repeating the introduction.

When an idea or option is easier to choose visually, use the [visual-choice guide](../oway-uix/references/visual-choices.md) now: show real images beside short labelled descriptions before asking for a choice. Do not wait for the design stage or make the user search for references. Keep purely technical or verbal choices concise without decorative imagery.

If the user says "just build it" before there is a minimum definition, push back once as the contract says. A minimum definition means three things: who it is for, the one job it must do, and how we will know it works. Write your own draft of those three lines and show it, so the fix takes minutes. A definition you wrote is not approval: build small work on it unless it is a costly guess, but anything that needs a slice waits for the user to approve the definition.

Show the user a concise, concrete interpretation and only the decisions that change product direction. Apply clear corrections directly. Log significant delegated choices and their reversibility in `_oway/LEDGER.md` (or through `memlog.py` in v0.3). The user should not need to know Oway stages to express an idea.
