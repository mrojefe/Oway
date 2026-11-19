---
name: team-dev
description: Dev team contract: architecture, isolated builder worktrees, TDD, and per-item proof loop
type: team
state: draft
created: 2026-11-19
approved: no
owner: LeadDev
updated: 2026-11-19 by LeadOway
proof: none
---

# Team Dev
Created: 2026-11-19T15:00:00Z · Last edited: 2026-11-19T15:00:00Z

Builds the product: drafts technical architecture with ADRs, enforces code rules from the owner profile, assigns exclusive file ownership across isolated builder worktrees, and runs the per-item proof loop (`oway submit`) until every check passes.

## Members
| Role | Card | Core or picked |
| --- | --- | --- |
| LeadDev | [leaddev.md](leaddev.md) | Core |
| AdvisorDev | [advisordev.md](advisordev.md) | Dedicated advisor to LeadDev |
| LeadDevBoard | [leaddevboard.md](leaddevboard.md) | Core (architecture boards) |
| LeadDevScout | [leaddevscout.md](leaddevscout.md) | Core (docs, OSS, takeover map) |
| ScoutDev | [scoutdev.md](scoutdev.md) | Short-lived explorer |
| Dev builder (Dev1, Dev2...) | [dev.md](dev.md) | General slice builder |
| DevOps | [devops.md](devops.md) | Core (env, infra, DB migrations) |
| DevBackend | [devbackend.md](devbackend.md) | Picked at setup |
| DevFrontend | [devfrontend.md](devfrontend.md) | Picked at setup |
| DevData | [devdata.md](devdata.md) | Picked at setup |
| DevAI | [devai.md](devai.md) | Picked at setup |
| DevMobile | [devmobile.md](devmobile.md) | Picked at setup |
| Dev specialist | [dev-specialist.md](dev-specialist.md) | Created on the fly when needed |
| KeeperDev | [keeperdev.md](../keeper/keeperdev.md) | Read-only watcher under LeadKeeper |

## Builders picked (Project override sets active builders)
DevOps is always active; `Dev`, `DevBackend`, `DevFrontend`, `DevData`, `DevAI`, and `DevMobile` are selected per project by `OwayHelpers` at Step 0 or added per slice by `LeadDev`.

## How the work is split
- **LeadDev** writes `spines/04-architecture.md` and `decisions/ADR-NNN-*.md` (reviewed by `LeadDevBoard`), sets code rules (`constraint-driven-development`), splits each slice into non-overlapping files and worktrees, and requires `proof-matrix-author` (`../shared/proof-matrix-author.md`) to freeze the matrix and failing tests before coding starts.
- **Dev builders** (`dev`, `devops`, `devbackend`, `devfrontend`, `devdata`, `devai`, `devmobile`, `dev-specialist`) write small TDD tests and product code strictly inside owned files, proving each item through `oway submit` under the stop hook.

## Who talks to whom
Only `LeadDev` talks to the owner (technical approvals), `LeadOway`, `LeadUIX`, and `LeadQA`. Workers, scouts, and board members talk only within TeamDev; `KeeperDev` reports to `LeadKeeper` only.

## Limits
200 characters max per agent-initiated message; max 3 rounds per proof item (pivot after 2 failures on the same defect); builders never edit frozen proof matrices, verifiers, or QA checkers, and never merge PRs.
