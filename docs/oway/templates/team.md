# Template: team
Created: 2026-11-15T15:00:00Z · Last edited: 2026-11-15T15:00:00Z

One file per team switched on: `_oway/agents/<team>/TEAM.md`. It links to the role cards in the Oway tool and never copies them. An override file with the same name as a card adds this project's rules to it.

```markdown
---
name: team-<team>
description: <one line>
type: team
parent: <project-id>
state: draft
created: <filled from Git>
approved: no
owner: Lead<Team>
updated: <filled by a script>
---

# Team <Team>
Created: <date> · Last edited: <date>

## Members
| Role | Card | Override | Model |
| --- | --- | --- | --- |
| Lead<Team> | <link to the tool's card> | <file here, or "none"> | <set at setup> |

## Builders picked (Dev team only)
<DevBackend, DevData...; DevOps is always there>

## How the work is split
<who takes what, in a few lines>

## Who talks to whom
<only the lead talks to the owner and to the other leads; KeeperX reports to LeadKeeper only>

## Limits
<message length, scouts cap, review rounds (max 3)>
```
