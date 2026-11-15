# Template: role card
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T15:00:00Z

One file per agent: LeadOway, a Dev builder (DevData), KeeperQA, or an agent created on the fly.

| Section | What goes in it |
| --- | --- |
| Header | name, description, type, state, created, approved, owner, updated |
| What it does | Numbered list of its jobs |
| Skills it loads | e.g. from agent-skills |
| What it reads and writes | Two columns |
| Who it talks to | Who it may contact and warn; only leads contact you |
| What it never does | Hard limits |
| Model | Decided later, per agent |
| Hooks and limits | Max retries, token budget, time limit |
| Message length | 200 characters for messages the agent starts; a little more only when the owner talks to it. Answer first, no greeting or recap, never drop "not", "never" or "only" |
| How many | One per project, or more |

```
---
name: <agent-name>   # e.g. LeadQA, ScoutDev, DevData; card in the Oway tool; a project override uses the same name in _oway/agents/<team>/
description: <one line: what this agent is for>   # shown in the index
type: agent        # see the types list in Rules
state: draft       # draft / approved
created: <date>    # filled by a script from Git
approved: no       # becomes "<date> by @your-github-username" after your GitHub review
owner: <agent>     # who keeps THIS FILE up to date, e.g. LeadOway or LeadQA; never the agent described here
updated: <date> by <agent>   # last edit and who made it; filled by a script
---

# <Role name>

## What it does
<numbered list of its jobs>

## Skills it loads
<skills, e.g. from agent-skills: interview-me, constraint-driven-development>

## What it reads and writes
| Reads | Writes |

## Who it talks to
<who it may contact, who it warns, and when; only leads contact you>

## What it never does
<hard limits>

## Model
<which AI model; decided later, per agent>

## Hooks and limits
<hooks the harness enforces; max retries, token budget, time limit>

## Message length
<200 characters for messages it starts; files over chat>

## How many
<one per project, or more>
```
