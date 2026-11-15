# Template: slice
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

One file per slice: `_oway/slices/<id>.md`. It holds the start agreement (T1 and bigger) and the Git plan. Its proof matrix is a separate file, frozen and hashed once the owner approves it.

```markdown
---
name: s<NNN>-<short-title>
description: <one line>
type: slice
parent: m<N>-<short-title>
state: draft            # draft / approved / in-progress / in-review / done / blocked
tier: T1                # T0 / T1 / T2 / T3
release: patch          # patch / minor / major / none
created: <filled from Git>
approved: no
owner: LeadDev
updated: <filled by a script>
proof: evidence/<slice-id>/
---

# S<NNN>: <title>
Created: <date> · Last edited: <date>

## 1. The goal
<one sentence>

## 2. What you get
<what the owner can open, click or run>

## 3. The proof you will have
Proof matrix: `<slice-id>.matrix.md`, frozen at <hash>.

## Start agreement
- Outcomes the owner will see: <list>
- Accepted examples: <list>
- Rejected examples: <list>
- Out of scope: <list>
- How each outcome is evaluated: <list>
- When the owner is asked to check: <moment>

## Git plan
- Base revision: <sha>
- Branch or worktree: <name>
- Builders and the files each one owns: <table>
- Commit order: failing test, then implementation, then passing test

## Budget
- Rounds per item: 3 at most
- Tokens: <budget>  Time: <limit>
```
