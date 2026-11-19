---
name: oway-migrate
description: Plan and execute a large refactor, rename, repo split, data move, or other structural change while preserving behavior and a recovery route.
---

# Migrate safely (`oway-migrate`)

## 1. Oway v0.4 Structural Migration & Tool Upgrade (`_oway/`)

1. **Structural Product Migrations (`T3` Slice + ADR)**:
   - Any schema, auth, data, or cross-service migration is sized `T3` by `LeadOway` and requires an ADR in `_oway/decisions/ADR-NNN-<slug>.md` ([deprecation-and-migration](../deprecation-and-migration/SKILL.md)) plus a slice file `_oway/slices/sNNN-<slug>.md` starting at the top with `## 1. The goal`, `## 2. What you get`, and `## 3. The proof you will have`.
   - `DevOps` writes reversible `up` and `down` migrations tested against real database/service engines; `proof-matrix-author` freezes the migration checks (`oway freeze sNNN`) before execution.
2. **Upgrading Oway Layout Across Releases (`oway upgrade`)**:
   - When `_oway/` itself advances to a newer Oway schema or path rule, run `oway upgrade --dry-run` to preview `git mv` transitions, then `oway upgrade`, `oway index`, and `oway doctor`.

---

## 2. Core Discipline & Legacy v0.3 Compatibility

Read only what the current step needs, once per session: the [agent contract](../../engine/CONTRACT.md), [method section 10](../../docs/METHOD.md) (that section only), relevant ADRs and the current repo map. Declare T3 when the change is structural; identify affected and unreachable repos, consumers, history, CI paths, deployment order and owners. Obtain a baseline of behavior and tests at a named revision, then define intended changes and preserved behavior before edits.

Write a migration contract in a scoped slice and ADR: old/new contracts, data transformation and validation, side-by-side period, checkpoints, performance/security acceptance, observation period, and a recovery route proven before irreversible steps. A repo rename must cover aliases in the registry, imports, remotes, CI and links. Use `impact.py` only when it exists; otherwise trace indexed dependencies explicitly and label coverage limits.

Execute in bounded steps with checks after each transition. Keep both states observable until cutover. Do not infer infrastructure access as authorization to deploy or delete. Require the user's decision for consequential or irreversible steps, then report revision, evidence, unresolved dependencies and recovery state. The `oway-pivot` alias directs to this workflow.
