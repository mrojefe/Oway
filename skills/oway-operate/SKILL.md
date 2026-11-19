---
name: oway-operate
description: Run release, observation, incident response, drift repair, runbooks, or retirement for an installed Oway project.
---

# Operate the project (`oway-operate`)

## 1. Oway v0.4 Release, Keepers, & Post-Ship Operations (`LeadQADelivery` + `LeadKeeper`)

In Oway v0.4 (`docs/oway/how-work-flows.md` Stage 7 CI/CD and Stage 8 Follow-up):

1. **Releases & Sole Git Authority (`LeadQADelivery` + `QADelivery`)**:
   - `LeadQADelivery` holds sole Git and release authority (using [shipping-and-launch](../shipping-and-launch/SKILL.md) and [ci-cd-and-automation](../ci-cd-and-automation/SKILL.md)).
   - Before any release: verify `oway doctor`, `oway index --check`, and `oway check <slice> --head`; watch CI completion via non-polling `gh pr checks <pr> --watch` (never poll in a loop); prepare changelog and rollback plan; and escalate every `main` merge or production release through `LeadQADelivery -> LeadQA -> Owner`.
   - Right after deploy, run smoke tests and start the post-release watch window.
2. **Read-Only Keepers & Drift Detection (`LeadKeeper` + `KeeperX`)**:
   - Wake/sleep team keepers via `oway keeper wake <team>` and `oway keeper sleep <team>`; run `oway keeper scan`, `oway keeper verify`, and `oway keeper report`.
   - When code, docs (`_oway/INDEX.md`, spines), or deployed state disagree (`DRIFT` / `DOC_STALE`), report it to the lead and owner with replayable proof — never fix drift silently.
   - Every incident is triaged, logged in `_oway/LEDGER.md`, and turned into a new deterministic checker or rule; method-level lessons are drafted via `oway feedback` (saved for owner review, never sent automatically).

---

## 2. Core Operations & Legacy v0.3 Compatibility

Read only what the current step needs, once per session: the [agent contract](../../engine/CONTRACT.md), `_oway/spines/05-delivery.md` (`docs/spines/05-DELIVERY.md` in v0.3), active slices and [method section 10](../../docs/METHOD.md) (that section only). For a release, verify the CI governance check and profile checks at the exact revision, write release notes and rollback or forward-fix route, then seek the user's release approval before production. A preview is evidence only for its environment. Confirm smoke tests and observation with actual results.

For an incident, establish impact and current state first, contain within authorized access, keep a timestamped evidence trail, then record the incident as a project constraint and follow-up slice. For drift, compare deployed behavior, code and docs; show disagreements and their sources before deciding which truth to change. Keep deploy, restore and known-failure runbooks in the delivery spine or its folder.

Check real host capabilities before promising monitoring or a scheduled follow-up. Record an actual scheduler ID if created; otherwise leave a checkpoint and a resumption instruction. At known quota thresholds, follow the contract's bounded-work rule and the method's 25/15/5 and weekly 10 percent thresholds using actual telemetry only.
