# ADR-007: CGSpec becomes Oway (v0.4), method first, engine in slices
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

- **Status:** Accepted
- **Date:** 2026-11-15
- **Deciders:** the repository owner

## Context and problem statement

CGSpec v0.3 enforces a strong per-slice proof engine, but it is run by one agent at a time and its method text lives in one long [METHOD.md](../METHOD.md). Separately, the owner ran CGM (a planning, proof-matrix and review method for pi agents) and a working keeper that watches agents. Real use showed two gaps: agents looped for days on side work while the main goal was paused, and work was split across two methods with different names. The owner wants one method, generic for any user, with named teams of agents, read-only watchers, and proofs an agent cannot fake.

## Considered options

1. Keep CGSpec and CGM separate. Rejected: two vocabularies and two sets of rules for the same work.
2. Start a new repository for the merged method. Rejected: loses CGSpec's tests, engine and history.
3. Evolve CGSpec in this repository into Oway v0.4, method first. Chosen.

## Decision and invariants

- CGSpec becomes **Oway**, version 0.4, in this repository.
- The method lands first, as separate files under [`docs/oway/`](../oway/README.md): teams and roles, how work flows, the proof loop, design, versioning/docs/Git, rules, an example setup, templates and role cards. One part per file; nothing is squashed into one catch-all file.
- The engine changes later, in small tested pull requests, one slice at a time. Until then [METHOD.md](../METHOD.md) stays the enforced v0.3 specification, and its sections stay intact because tests read them.
- The code and its tests are the source of truth. Method text that a hook, a script or CI does not yet enforce is guidance, not a gate.

## Consequences

- Positive: one vocabulary (role first: LeadQA, KeeperQA); CGM's proof matrix and CGSpec's verification become one loop; the method can be reviewed in small files.
- Negative: for a while the method describes more than the engine enforces. [STATUS.md](../STATUS.md) must say which parts are enforced.
- Follow-up engine slices: rename the consumer folder to `_oway/`, the `oway submit` and `oway check` commands with the stop hook, the frozen proof matrix, keeper wake and sleep, file headers filled from Git, the index script.

## Affected areas

`docs/oway/` (new), `docs/adr/`, `CHANGELOG.md`, `README.md`, `docs/STATUS.md`. No change to `engine/`.
