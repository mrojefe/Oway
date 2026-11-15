# Template: proof matrix
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

One matrix per slice: `_oway/slices/<id>.matrix.md`. Drafted by a separate agent on a strong model, never by the builder; approved by the owner; then frozen (hashed). Only the verifier or `oway check` marks an item PASS. See [The proof loop](../proof-loop.md).

```markdown
---
name: s<NNN>-matrix
description: Proof matrix of s<NNN>
type: matrix
parent: s<NNN>-<short-title>
state: draft            # draft / frozen
created: <filled from Git>
approved: no
owner: LeadQATester
frozen_hash: <filled when frozen>
---

# S<NNN> proof matrix
Created: <date> · Last edited: <date>

| id | Interaction | Accepted proof | Medium | Verifier commands | Canary | State |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | <one thing the user does> | <what counts as proof> | video / screenshot + live output / command record | `<commands>` | <word planted in the real system, or none> | OPEN |
```

States: OPEN, SUBMITTED, PASS, FAIL, NEEDS_REVIEW, FAKE, BLOCKED. A reviewer answers only `{"verdict":"PASS|FAKE|INSUFFICIENT","reason":"one sentence","evidence_ids":[...]}`; anything else is UNREVIEWED, never PASS.
