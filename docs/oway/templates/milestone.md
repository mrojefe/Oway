# Template: milestone
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T15:00:00Z

One file per milestone: `_oway/milestones/<id>.md`. `kind` is `build` (slices with checks) or `business` (tasks without a proof matrix: replace the Slices table with a Tasks table: task, owner, visible result). Only one milestone has `current: true`. A script pushes a copy to the GitHub milestone; the file stays the truth.

```markdown
---
name: m<N>-<short-title>
description: <one line>
type: milestone
kind: build
current: false
parent: <project-id>
state: draft
created: <filled from Git>
approved: no
owner: LeadOway
updated: <filled by a script>
---

# M<N>: <title>
Created: <date> · Last edited: <date>

## 1. Main goal
<one sentence; the keepers read it first>

## 2. What you get
<concrete result at the end of the milestone>

## 3. The proof you will have
<the proof items that show the milestone is reached>

## Slices
| id | description | state | depends on |
| --- | --- | --- | --- |

## Side work allowed
<side work approved by the lead, each with its budget: rounds, tokens or hours>

## Risks
<what could stop it, and what is done about each>
```
