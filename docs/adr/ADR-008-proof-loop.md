# ADR-008: The proof loop: a frozen matrix, a deterministic verifier, then a reviewer
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

- **Status:** Accepted
- **Date:** 2026-11-15
- **Deciders:** the repository owner

## Context and problem statement

Agents claim results they did not prove: edited tests, staged screenshots, mock data, "done" with nothing run. CGSpec v0.3 already rejects fixture-backed claims and replays red-green proof; CGM checked a full interaction matrix but only reviewed once at the end. The owner asked for a hook that makes the coding agent trigger a proof collector before it stops, with the result sent to a decision model.

## Considered options

1. Review once at the end of a slice (CGM). Rejected: defects are found late and loops get long.
2. Let the agent call a model judge directly. Rejected: the agent controls what the judge sees.
3. Per-item loop with a stop hook, a deterministic verifier and a separate reviewer, plus one final adversarial review. Chosen.

## Decision and invariants

- Principle: a proof is a fact that a process other than the agent observed and recorded; text the agent typed is only a claim.
- A separate agent drafts the exhaustive proof matrix; the owner approves it; it is then frozen (hashed) and outside the builder's write zone.
- For each item: the harness captures every command; a verifier script (no model) runs the item's commands, reads the canary and records the browser; only when needed, a reviewer on another model pool sees the evidence and command log, never the builder's summary, and answers a fixed JSON verdict. Anything else is UNREVIEWED, never PASS.
- A stop hook on builders, never on leads, refuses to stop while an item is OPEN or FAIL. At most 3 rounds per item, plus a token and time budget; then BLOCKED in the ledger.
- Only the verifier or `oway check` marks PASS. Evidence goes to an append-only, hash-chained ledger.
- One final adversarial review per slice re-runs the checks; a report never says "zero defects".

## Consequences

- Positive: an agent cannot finish without proof, and cannot write its own proof.
- Negative: more tooling (hooks per harness, verifier, ledger). Harnesses without hooks rely on Git hooks, CI and the lead running `oway check`.
- Full text: [The proof loop](../oway/proof-loop.md).
