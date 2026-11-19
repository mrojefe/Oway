---
name: team-product
description: Product team: intent interview, v1 scope, domain objects, and commercial research
type: team
state: draft
created: 2026-11-19
approved: no
owner: LeadProduct
updated: 2026-11-19 by LeadOway
proof: none
---

# Team Product
Created: 2026-11-19T15:00:00Z · Last edited: 2026-11-19T15:00:00Z

Turns the owner's words into clear v1 scope, intent, domain objects, delivery milestones context, and sourced market research before design or engineering begins.

## Members
| Role | Card | Model |
| --- | --- | --- |
| LeadProduct | [leadproduct.md](leadproduct.md) | Decided at setup |
| AdvisorProduct | [advisorproduct.md](advisorproduct.md) | Dedicated advisor to LeadProduct |
| LeadProductBoard | [leadproductboard.md](leadproductboard.md) | Decided at setup |
| LeadProductScout | [leadproductscout.md](leadproductscout.md) | Decided at setup |
| ScoutProduct | [scoutproduct.md](scoutproduct.md) | Short-lived explorer |
| KeeperProduct | [keeperproduct.md](../keeper/keeperproduct.md) | Read-only watcher under LeadKeeper |

## How the work is split
- **LeadProduct** interviews the owner (`interview-me`, `idea-refine`, `spec-driven-development`) to write `spines/01-intent.md`, `spines/02-objects.md`, and `spines/05-delivery.md`.
- **LeadProductScout** and **ScoutProduct** run primary-source competitor, buyer, pricing, demand, and risk studies (`research/RES-NNN`) for commercial goals.
- **AdvisorProduct** and **LeadProductBoard** challenge assumptions and scope boundaries before locking Stage 1 Brainstorming.

## Who talks to whom
Only `LeadProduct` talks to the owner, `LeadOway`, and peer leads (`LeadUIX`, `LeadDev`, `LeadQA`). Workers, scouts, and board members talk only within the Product team; `KeeperProduct` reports to `LeadKeeper` only.

## Limits
200 characters max per agent-initiated message; max 3 rounds per board; research files must cite verified `https://` primary sources; no silent scope growth.
