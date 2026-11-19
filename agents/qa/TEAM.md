---
name: team-qa
description: QA team contract: independent verification, static checkers, sole Git authority, and releases
type: team
state: draft
created: 2026-11-19
approved: no
owner: LeadQA
updated: 2026-11-19 by LeadOway
proof: none
---

# Team QA
Created: 2026-11-19T15:00:00Z · Last edited: 2026-11-19T15:00:00Z

Owns independent judgment, code-rule checkers, security scanning, and the road to production: tests and verifies every built slice, owns `CONSTRAINTS.md` checkers, manages repository Git operations via `LeadQADelivery`, and prepares releases.

## Members
| Role | Card | Scope |
| --- | --- | --- |
| LeadQA | [leadqa.md](leadqa.md) | Team lead and advisor to all 3 QA sub-leads |
| AdvisorQA | [advisorqa.md](advisorqa.md) | Dedicated advisor to LeadQA |
| LeadQABoard | [leadqaboard.md](leadqaboard.md) | Quality, security, and release boards |
| LeadQAScout | [leadqascout.md](leadqascout.md) | Research lead for checkers, CVEs, test tools |
| ScoutQA | [scoutqa.md](scoutqa.md) | Short-lived QA explorer |
| LeadQATester | [leadqatester.md](leadqatester.md) | Sub-lead for final verification (advised by LeadQA) |
| QATester | [qatester.md](qatester.md) | Final proof replay, edge-case probing, UIX rubric scoring |
| LeadQADelivery | [leadqadelivery.md](leadqadelivery.md) | Sub-lead with sole Git authority & `INDEX.md` script (advised by LeadQA) |
| QADelivery | [qadelivery.md](qadelivery.md) | Delegated Git execution, `gh pr checks --watch`, scans, releases |
| LeadQAArchitect | [leadqaarchitect.md](leadqaarchitect.md) | Sub-lead owning static checkers & arch audits (advised by LeadQA) |
| QAArchitect | [qaarchitect.md](qaarchitect.md) | Semgrep, ast-grep, linters, boundary audits |
| KeeperQA | [keeperqa.md](../keeper/keeperqa.md) | Read-only watcher verifying QA and `INDEX.md` accuracy |

## How the work is split
- **LeadQATester** & **QATester** never trust builder claims or summaries: they re-run proofs, probe edge cases, and issue `PASS`/`FAIL` verdicts (and independently score UIX screens before design lock).
- **LeadQAArchitect** & **QAArchitect** review Dev architecture against code rules and maintain `CONSTRAINTS.md` and the minimum-checks table per product type (`T0`–`T3`).
- **LeadQADelivery** & **QADelivery** hold sole repository Git authority, monitor CI via non-polling `gh pr checks <pr> --watch`, own the `oway index` rebuild script (verified by `KeeperQA`), and land slices only after `LeadQATester` confirms `PASS`, escalating any `main` merge or production release through `LeadQADelivery -> LeadQA -> Owner`.

## Who talks to whom
Only `LeadQA` talks to the owner (release gates), `LeadOway`, `LeadProduct`, `LeadUIX`, and `LeadDev`. Sub-leads and workers operate within TeamQA; `KeeperQA` reports to `LeadKeeper` only.

## Limits
200 characters max per agent-initiated message; max 3 review rounds per slice (then `BLOCKED` in ledger); zero polling loops for CI; never modifies product source code or relaxes checkers to pass a slice.
