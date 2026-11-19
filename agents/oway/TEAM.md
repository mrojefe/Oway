---
name: team-oway
description: Oway orchestration team: LeadOway, setup helpers, cross-team board, scouts, and KeeperOway
type: team
state: draft
created: 2026-11-19
approved: no
owner: LeadOway
updated: 2026-11-19 by LeadOway
proof: none
---

# Team Oway
Created: 2026-11-19T15:00:00Z · Last edited: 2026-11-19T15:00:00Z

Project orchestration layer above the four delivery teams: turns the owner's goals into milestones and slices, confirms the three first parts, wakes LeadKeeper, and manages cross-team decisions.

## Members
| Role | Card | Model |
| --- | --- | --- |
| LeadOway | [leadoway.md](leadoway.md) | Decided at setup |
| OwayHelpers | [owayhelpers.md](owayhelpers.md) | Decided at setup (setup only) |
| LeadOwayBoard | [leadowayboard.md](leadowayboard.md) | Decided at setup |
| LeadOwayScout | [leadowayscout.md](leadowayscout.md) | Decided at setup |
| ScoutOway | [scoutoway.md](scoutoway.md) | Decided at setup |
| KeeperOway | [keeperoway.md](../keeper/keeperoway.md) | Read-only watcher under LeadKeeper |

## How the work is split
- **OwayHelpers** run only during Step 0 setup (profile interview, workspace scan, config, builder selection, `oway doctor`).
- **LeadOway** routes the owner to Product and UIX, confirms Goal / What you get / Proof matrix before work cuts, plans milestones and slices, and brings gates to the owner.
- **LeadOwayBoard** and **LeadOwayScout** handle cross-team trade-offs and cross-team research that no single team owns.
- **KeeperOway** (under [LeadKeeper](../keeper/leadkeeper.md)) watches LeadOway read-only so orchestration never drifts or does a team's job itself.

## Who talks to whom
LeadOway talks to the owner, the four team leads (`LeadProduct`, `LeadUIX`, `LeadDev`, `LeadQA`), `LeadKeeper`, and its own team. `KeeperOway` reports to `LeadKeeper` only.

## Limits
200 characters max per agent-initiated message (one line + link); at most 3 rounds per board; capped concurrent scouts; obeys common retry, token, and quota limits.
