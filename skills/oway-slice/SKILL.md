---
name: oway-slice
description: Plan, build, test, and review a bounded feature or fix within an approved slice and its declared file scope.
---

# Deliver a bounded change (`oway-slice`)

## 1. Oway v0.4 Slice Workflow (`_oway/slices/`)

Every slice in an Oway project (`_oway/slices/sNNN-<slug>.md`, from `docs/oway/templates/slice.md`) starts at the very top with the **three first parts** (enforced by `oway doctor`):

1. **`## 1. The goal`**: one clear sentence.
2. **`## 2. What you get`**: what the owner can open, click, or run at the end.
3. **`## 3. The proof you will have`**: link to the separate frozen proof matrix (`_oway/slices/sNNN-<slug>.matrix.md`) and its hash.
4. Followed by **`## Start agreement`** (outcomes, accepted/rejected examples, out of scope, evaluation, owner checkpoint), **`## Git plan`** (base revision, branch/worktree, exclusive file ownership per builder, red -> green commit order), and **`## Budget`** (max 3 rounds per item, token/time limits).

### Roles & Execution Loop
- **Sizing (`T0`–`T3`)**: `LeadOway` sizes the change before any edit (`T0` <= 3 files and 40 lines; `T1` bounded slice <= 400 lines; `T2` feature; `T3` structural).
- **Proof Matrix Freeze**: Before any builder starts, `proof-matrix-author` drafts `_oway/slices/sNNN-<slug>.matrix.md` and the failing-first proof tests/verifiers. After owner approval, run `oway freeze sNNN` (builders are blocked from running `freeze` or editing `.matrix.md` / verifiers).
- **Build & Per-Item Proof Loop**: `LeadDev` assigns each Dev builder (`dev`, `devbackend`, `devfrontend`, `devdata`, `devai`, `devmobile`, `devops`, `dev-specialist`) its own worktree and exclusive files, using [incremental-implementation](../incremental-implementation/SKILL.md) and [test-driven-development](../test-driven-development/SKILL.md). For each item, the builder runs `oway submit sNNN P1`. `oway guard` blocks writes outside the builder's zone, and `oway stop-hook` prevents stopping while any item is `OPEN`, `FAIL`, `INSUFFICIENT`, or `NEEDS_REVIEW` (pivoting after 2 failures on the same defect; `BLOCKED` in `_oway/LEDGER.md` after 3 rounds).
- **Independent QA Review & Git Landing**: Once `oway check sNNN --head` passes, `LeadQATester` and `QATester` (or `adversarial-reviewer`) re-run every proof at the exact revision without reading the builder's summary (`oway review sNNN P1` for visual/reviewed items), write `_oway/slices/sNNN-<slug>.walkthrough.md`, and issue `PASS` or `FAIL`. Only after `LeadQATester` confirms `PASS` does `LeadQADelivery` (delegating to `QADelivery`) land the branch, wait for CI via non-polling `gh pr checks <pr> --watch`, run `oway index` (verified by `KeeperQA`), and escalate any `main` merge via `LeadQADelivery -> LeadQA -> Owner`.

---

## 2. Legacy v0.3 Consumer Compatibility (`docs/_cgspec/`)

For a project still running the v0.3 layout prior to `oway takeover --from cgspec-0.3`, read the [agent contract](../../engine/CONTRACT.md), active project state, affected spines and [method sections 3 and 7b](../../docs/METHOD.md) (that section only). Size the change before editing. Use `python3 docs/_cgspec/01-engine/cgspec_hook.py tier set --root <path> --tier <T0|T1|T2|T3> --reason <reason> --files <comma-separated-existing-files> --verify <how-to-check>` for T0, or `--slice <SLICE-NNN>` for T1+. Confirm exact syntax with `--help`. A true T0 stays within three existing files and forty changed lines, with no restricted change; otherwise escalate.

For T1+, create or update `docs/slices/SLICE-NNN-<slug>.md` with file scope, interfaces, acceptance criteria and named checks. Draft its `.start.json` with observable outcomes, evaluation, coverage, prerequisites and human checkpoints; obtain fresh approval, run `start ready`, then `start begin` for each eligible outcome before dependent implementation. Material definition changes require renewed approval/readiness. Criteria and test files are written and frozen before code by someone other than the builder; an author cannot approve or weaken its own tests. Capture a failing test at a real revision before implementation, then the passing test pair in `docs/_cgspec/06-evidence/`. Small projects and headless projects use their profile's actual checks; do not invent UI work.

Implement only within the slice scope and agreed ownership. Run the profile and tier checks from the method table, then doctor. At T1+ use one clean-context reviewer, different model when available, and label same-model review honestly. Findings block on correctness or stated requirements; taste suggestions stay optional. After two rounds on the same defect, change approach; at three rounds report BLOCKED with remaining defects. A PASS names the revision and checks run, and lists checks not run. Log the result and checkpoint.
