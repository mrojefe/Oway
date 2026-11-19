# Oway and om Glossary
Created: 2026-11-19T13:10:00Z · Last edited: 2026-11-19T13:10:00Z

Canonical terms for **Oway** (the full multi-team method in [docs/oway/](oway/README.md)) and **om** (the light everyday workflow in `om/`). Role names put the role first and the team second (for example `LeadDev`, `KeeperQA`, `ScoutUIX`). Earlier CGSpec v0.3 or CGM names are listed in the last column where they existed.

## Methods and setup

| Term | Meaning | Earlier name |
| --- | --- | --- |
| **Oway** | The full method for running software projects with teams of AI agents: roles, proof loop, read-only keepers, and deterministic CLI/hook gates. | CGSpec, CGM |
| **om** | Light Oway for everyday work (Quick, Task, Mission sizes): same proof-first and anti-fake rules with less ceremony, synced across harnesses by `oway sync`. | CGM light |
| **Owner** | The human decision-maker who approves goals, money, secrets, irreversible actions, and release gates. | User |
| **Platform** | The owner's shared per-machine setup (`~/.oway`): profile, accounts, cached style catalog, and the installed `oway` binary shared across projects. | |
| **Profile** | How the owner works (rules, language, tools, accounts), written once during Step 0 and approved by the owner. | |
| **Capability** | A declared permission beyond the repo (browser session, chat channel, external service) paired with an executable probe and owner approval. | Capability (CGSpec #53) |

## Work hierarchy and proof loop

| Term | Meaning | Earlier name |
| --- | --- | --- |
| **Project** | The product being built; top node of `_oway/`. | |
| **Milestone** | A major goal grouping several slices (`parent: project`). Opens with the three first parts (goal, what you get, proof you will have). | cg-plan (CGM) |
| **Slice** | One bounded deliverable completed in days (`parent: <milestone>`), with its own frozen proof matrix and Git plan. | Slice |
| **Check** | One observable requirement that must be true for a slice to pass: a single row of the proof matrix. | Acceptance criterion |
| **Proof matrix** | The frozen Markdown table (`_oway/slices/<slice>.matrix.md`) authored by a separate agent (`proof-matrix-author` / `DevProof`) and locked by `oway freeze` with a SHA-256 hash covering items and verifier files. | Verification matrix |
| **Proof item** | One row of the proof matrix: interaction, accepted proof, medium (`command record`, `screenshot + live output`, etc.), verifier commands, canary, and state (`OPEN`, `FAIL`, `NEEDS_REVIEW`, `INSUFFICIENT`, `FAKE`, `PASS`, `BLOCKED`). | Matrix item |
| **Verifier** | A deterministic script or command declared in the proof matrix (`verifiers:`) and executed by `oway submit`. Builders cannot edit verifiers. | |
| **Canary** | A unique token expected in live verifier output so stale, mocked, or fabricated proof fails deterministically. | |
| **Stop hook** | Host hook (`oway stop-hook`) that blocks a builder from stopping while any matrix item is `OPEN`, `FAIL`, `NEEDS_REVIEW`, or `INSUFFICIENT`, while letting leads pass and capping idle loops. | |

## Teams, leads, keepers, and delivery

| Term | Meaning | Earlier name |
| --- | --- | --- |
| **LeadOway** | Project main that orchestrates teams and talks to the owner. Writes no product code and never self-checks work. | Lead, prime |
| **OwayHelpers** | Setup-only helpers under `LeadOway` that interview the owner, draft the profile, and configure watchers and quota tracking. | |
| **Teams** | Four specialist teams: **Product** (scope), **UIX** (design when a UI exists), **Dev** (builds and proves items), and **QA** (judges finished slices and owns delivery). | Product Owner, TeamWork, TeamQA |
| **LeadX** | Team lead (`LeadProduct`, `LeadUIX`, `LeadDev`, `LeadQA`). Only leads contact the owner. | Team main |
| **Board** | Cross-model panel (`LeadXBoard` + members on distinct models) convened to resolve a high-impact decision. | Council |
| **Scout** | Short-lived researcher (`LeadXScout` + `ScoutX`) scoped to one zone with its own skills. | |
| **DevProof** | Separate Dev-side author (`proof-matrix-author`) who drafts the proof matrix and verifier scripts before builders start; never builds product code. | |
| **Keeper** | Read-only sentinel (`KeeperOway`, `KeeperProduct`, `KeeperUIX`, `KeeperDev`, `KeeperQA`) that watches one team while awake, detects `TAMPER`, `LOOP`, `DRIFT`, and `FAKE_PROOF`, and reports only to `LeadKeeper`. | Sentinel |
| **LeadKeeper** | Top watcher that replays and verifies team keeper findings before warning the relevant lead and the owner (capped at 200 characters). | |
| **LeadQATester** | QA sub-lead overseeing `QATester` workers who independently re-run proof and probe edge cases on finished slices. | |
| **LeadQADelivery** | QA sub-lead holding sole Git management authority (branches, PRs, merges, tags, releases), supervising `QADelivery` workers, CI watch (`gh pr checks <pr> --watch`), security scans, changelogs, and `oway index`. | |
| **LeadQAArchitect** | QA sub-lead overseeing `QAArchitect` workers who check architecture fit and maintain static-analysis checkers. | |

## Repository records

| Term | Meaning | Earlier name |
| --- | --- | --- |
| **Index** | Folder summary (`INDEX.md`) rebuilt deterministically from YAML frontmatter by `oway index` and checked in CI with `oway index --check`. | |
| **Header** | Standard YAML frontmatter (`name`, `description`, `type`, `state`, `created`, `updated`, etc.) at the top of project files, synced from Git by `oway headers`. | |
| **Ledger** | Append-only event and decision log (`_oway/LEDGER.md`), written by `oway ledger`. | `_memlog.md` |
| **Inbox** | Scrubbed record of owner messages (`INBOX.md`), with secrets removed. | `00-INBOX.md` |
