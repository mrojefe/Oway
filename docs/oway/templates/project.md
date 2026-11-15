# Template: project
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

One file per project: `_oway/project.md`. Short; the detail lives in the five spine files in `_oway/spines/`. It starts with the three first parts (see [How work flows](../how-work-flows.md#every-piece-of-work-starts-with-three-parts)).

```markdown
---
name: <project-id>
description: <one line: what this project is>
type: project
state: draft            # draft / approved / in-progress / done
created: <filled from Git>
approved: no            # becomes "<date> by @<github-username>" after the owner's review
owner: LeadOway
updated: <filled by a script>
---

# <Project name>
Created: <date> · Last edited: <date>

## 1. The goal
<one sentence>

## 2. What you get
<what the owner can open, click or run at the end>

## 3. The proof you will have
<the main proof items, and how each is shown: video, screenshot, query result; the full matrix is frozen per slice>

## Spines
- Intent: `spines/01-intent.md`: why, for whom, success, anti-goals, v1 boundary, parked ideas
- Objects: `spines/02-objects.md`: objects, states, rules, permissions
- Experience: `spines/03-experience.md`: style register, screens, flows (only with a UI)
- Architecture: `spines/04-architecture.md`: short context; every choice is an ADR in decisions/
- Delivery: `spines/05-delivery.md`: order of milestones, risks, KPIs

## Setup facts
- Language of the project: <language>
- Tier rules and release policy: <link to config.json>
- Teams switched on: <Product, UIX, Dev, QA>; Dev builders picked: <DevBackend, DevData...>
- Keeper report interval: <for example every 2 hours>
```
