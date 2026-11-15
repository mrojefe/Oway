# Template: decision (ADR)
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

One file per important decision. From agent-skills' documentation-and-adrs skill, with our header added.

| Section | What goes in it |
| --- | --- |
| Header | name, description, type: decision, state, created, approved, owner, updated |
| Context | Why a decision was needed |
| Decision | What we chose |
| Alternatives considered | Each one, and why it was rejected |
| Consequences | What this changes, good and bad |

```
---
name: adr-<number>-<short-title>
description: <the decision, in one line>
type: decision
state: proposed       # proposed / accepted / superseded by ADR-xxx
created: <date>
approved: no
owner: LeadQADelivery
updated: <date> by <agent>
---

# ADR-<number>: <title>

## Context
<why a decision was needed>

## Decision
<what we chose>

## Alternatives considered
<each one, and why it was rejected>

## Consequences
<what this changes, good and bad>
```

An ADR is never deleted. When a decision changes, a new ADR replaces it and the old one says "superseded by".
