# Oway method
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T15:00:00Z

**Oway** is the next version of CGSpec (v0.4): a method for running projects with teams of AI agents. It says who does what, how work is cut and proven, and which rules every agent follows. It is meant for any user; one real setup is shown only as an example.

## Status

This folder is the method part of v0.4. The engine (`engine/`), the installed skills and [METHOD.md](../METHOD.md) still describe and enforce v0.3; they change in later, small, tested pull requests, one slice at a time ([ADR-007](../adr/ADR-007-cgspec-becomes-oway.md)). Until a rule here is enforced by a hook, a script or CI, it is guidance, not a gate. The first tool commands now exist in `engine/oway/` (index, doctor, freeze, submit, check, stop hook, keeper, setup); [STATUS.md](../STATUS.md) says what they cover and what is still planned. Open points are tracked in the Oway working doc, not here.

## The files

| File | What it holds |
| --- | --- |
| [Teams and roles](teams-and-roles.md) | LeadOway and its team, LeadKeeper, the four teams (Product, UIX, Dev, QA), keepers, scouts, boards, the full communication, where agents remember |
| [How work flows](how-work-flows.md) | Step 0 setup and the OwayHelpers, the three first parts, Project > Milestone > Slice > Check, tiers, the 8 stages, testing during the work |
| [The proof loop](proof-loop.md) | The proof matrix, the per-item loop with a stop hook and a deterministic verifier, why an agent cannot cheat, the final review |
| [Design](design.md) | How the UIX team designs with the owner: principles, the 8 layers, being good looking, design systems, versions |
| [Versioning, docs and Git](versioning-docs-git.md) | Code is the truth, the Oway-to-GitHub map, approvals, Git per slice, SemVer, the pipeline |
| [Rules](rules.md) | Hard rules: file format and headers, indexes, code rules checked by tools, keeper rules, minimum checks per product type, ledger, quota |
| [Taking over a project](takeover.md) | Joining a project that already started: the order of steps, the CGSpec-to-Oway path table, ADRs from old docs, what waits for the owner |
| [Example setup](example-setup.md) | What a project looks like once Oway is set up: the repo tree, GitHub, one slice from start to end, the Platform |
| [Templates](templates/) | Blank files to start from: project, the five spines, milestone, slice, proof item, keeper finding, team, role card, ADR, profile |
| [Config schema](schemas/oway-config.schema.json) | What `_oway/config.json` may hold |
| [Role cards & teams](../../agents/README.md) | 49 canonical role cards (with unified `agents/keeper/`) + 5 `TEAM.md` contracts |
| [Canonical glossary](../GLOSSARY.md) | Shared Oway and om terminology |

## Glossary

See also the [canonical Oway and om glossary](../GLOSSARY.md). Role first, then team: LeadDev, KeeperQA. The last column gives the CGSpec v0.3 or earlier name when there was one.

| Name | What it is | How many | Earlier name |
| --- | --- | --- | --- |
| **Oway** | The method | One, for everyone | CGSpec, CGM |
| **Owner** ("you" in these files) | The person who approves goals, money, secrets and gates | One per project | User |
| **Platform** | The owner's shared setup: infra, AI accounts, profile, the installed Oway tool. Shared by all their projects | One per user or team of people | |
| **Profile** | How the owner codes, their rules, tools and accounts, written once by the OwayHelpers | One per owner | |
| **Capability** | A permission given at setup, with its own check. Example: a lead may message the owner on a chat channel | Per agent | Capability (CGSpec #53) |
| **Project** | What is built | Many | |
| **Milestone** | A big goal; groups several slices. Ends when they are done | Many per project | cg-plan (CGM) |
| **Slice** | One deliverable, done in days | Many per milestone | Slice |
| **Check** | One thing that must be true for the slice to be done: one line of the proof matrix | Many per slice | Acceptance criterion |
| **Proof item** | A check with its interaction, accepted proof, medium, verifier commands and canary | One per check | Matrix item (CGM) |
| **Test** | How a check is proven | One or more per check | |
| **LeadOway** | The project main. Orchestrates and talks to the owner. Never checks work itself and writes no product code | One per project | Lead, prime |
| **OwayHelpers** | Setup-only helpers under LeadOway: interview the owner, write the profile, set the watcher and quota tracking | During setup | |
| **LeadKeeper** | The top watcher. Verifies what the team keepers report and is the only keeper that talks to a lead; every verified warning also goes to the owner | One per project | |
| **KeeperX** (KeeperQA, KeeperOway...) | Read-only watcher of one team, awake only while it works; reports to LeadKeeper only | One per team | Sentinel (in the literature) |
| **Teams** | Product (scope), UIX (design, only with a UI), Dev (builds and proves each item), QA (judges the finished slice) | One of each per project | Product Owner, TeamWork, TeamQA |
| **LeadX** (LeadProduct, LeadUIX, LeadDev, LeadQA) | Runs a team. Only leads talk to the owner | One per team | Team main |
| **LeadXBoard** | Runs its team's boards, writes the summary; never gives an opinion | One per team | Council chair |
| **LeadXScout** / **ScoutX** | Runs the team's scouts / a short-lived explorer with one zone and its own skills | One / a capped number | |
| **Board** | Agents on different models answering one question | When needed | Council |
| **LeadQATester, LeadQADelivery, LeadQAArchitect** | QA's three sub-leads, each with numbered workers | One each | |
| **Dev builders** (DevBackend, DevFrontend, DevData, DevAI, DevMobile) | Picked per project at setup; DevOps is always there | As needed | Worker |
| **Index** | The list at the top of each folder; agents read it first. Rebuilt by a script | One per folder | |
| **Header** | Name, description and state at the top of every file | One per file | |
| **Ledger** | Append-only log of decisions and events, written by a script | One per project | `_memlog.md` |
| **Inbox** | Every message the owner sends, secrets removed | One per project | `00-INBOX.md` |
