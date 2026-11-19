# Oway role cards
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-19T10:48:00Z

Canonical 1-file-per-role agent cards (48 total), from the [role card template](../templates/role-card.md). The team topology and governance rules are in [Teams and roles](../teams-and-roles.md). All cards are drafts until approved.

## Oway orchestration (`oway/`, 6)

| Card | What it is |
| --- | --- |
| [LeadOway](oway/leadoway.md) | The project main: orchestrates the teams and talks to the owner |
| [OwayHelpers](oway/owayhelpers.md) | Setup-only helpers: interview the owner and prepare the project |
| [LeadOwayBoard](oway/leadowayboard.md) | Runs LeadOway's boards for hard cross-team choices |
| [LeadOwayScout](oway/leadowayscout.md) | Runs cross-team research that no single team owns |
| [ScoutOway](oway/scoutoway.md) | Short-lived cross-team explorer under LeadOwayScout |
| [KeeperOway](oway/keeperoway.md) | Read-only sentinel watching LeadOway and the Oway orchestration layer |

## Keeper leadership (`keeper/`, 1)

| Card | What it is |
| --- | --- |
| [LeadKeeper](keeper/leadkeeper.md) | The top read-only watcher: verifies keeper findings and warns |

## Product team (`product/`, 6)

| Card | What it is |
| --- | --- |
| [LeadProduct](product/leadproduct.md) | Runs the Product team: turns the owner's words into scope |
| [AdvisorProduct](product/advisorproduct.md) | Dedicated advisor to LeadProduct on scope, positioning, and trade-offs |
| [LeadProductBoard](product/leadproductboard.md) | Runs LeadProduct's multi-model boards for product trade-offs |
| [LeadProductScout](product/leadproductscout.md) | Runs the Product team's scouts for market, user, and competitor research |
| [ScoutProduct](product/scoutproduct.md) | Short-lived Product team explorer under LeadProductScout |
| [KeeperProduct](product/keeperproduct.md) | Read-only sentinel watching the Product team |

## UIX team (`uix/`, 7)

| Card | What it is |
| --- | --- |
| [LeadUIX](uix/leaduix.md) | Runs the UIX team: designs with the owner across the 8 layers |
| [AdvisorUIX](uix/advisoruix.md) | Dedicated advisor to LeadUIX on craft, usability, and anti-slop rigor |
| [LeadUIXBoard](uix/leaduixboard.md) | Runs LeadUIX's multi-model boards to compare design directions and critiques |
| [LeadUIXScout](uix/leaduixscout.md) | Runs the UIX team's scouts for real design references and style packs |
| [ScoutUIX](uix/scoutuix.md) | Short-lived UIX explorer under LeadUIXScout |
| [UIX worker](uix/uix-worker.md) | UIX1, UIX2...: build prototypes, token sheets, and real frontend screens |
| [KeeperUIX](uix/keeperuix.md) | Read-only sentinel watching the UIX team and locked design versions |

## Dev team (`dev/`, 13)

| Card | What it is |
| --- | --- |
| [LeadDev](dev/leaddev.md) | Runs the Dev team: plans architecture and how each slice is built |
| [AdvisorDev](dev/advisordev.md) | Dedicated advisor to LeadDev on architecture, boundaries, and technical risk |
| [LeadDevBoard](dev/leaddevboard.md) | Runs LeadDev's multi-model architecture and stack boards |
| [LeadDevScout](dev/leaddevscout.md) | Runs the Dev team's scouts for official docs, libraries, and codebase mapping |
| [ScoutDev](dev/scoutdev.md) | Short-lived Dev team explorer under LeadDevScout |
| [DevOps](dev/devops.md) | Builds the product's environments, infrastructure, and database migrations |
| [DevBackend](dev/devbackend.md) | Dev builder for APIs, data models, and backend business logic |
| [DevFrontend](dev/devfrontend.md) | Dev builder connecting locked UIX frontend screens to the real backend |
| [DevData](dev/devdata.md) | Dev builder for data extraction, parsing, and transformation pipelines |
| [DevAI](dev/devai.md) | Dev builder for prompts, model calls, evaluation harnesses, and agent logic |
| [DevMobile](dev/devmobile.md) | Dev builder for iOS, Android, or cross-platform mobile apps |
| [Dev specialist](dev/dev-specialist.md) | On-the-fly specialist Dev builder instantiated for domain-specific slices |
| [KeeperDev](dev/keeperdev.md) | Read-only sentinel watching the Dev team |

## QA team (`qa/`, 12)

| Card | What it is |
| --- | --- |
| [LeadQA](qa/leadqa.md) | Runs the QA team: tests, verifies, judges, and owns the road to production |
| [AdvisorQA](qa/advisorqa.md) | Dedicated advisor to LeadQA on verification strategy, risk, and release readiness |
| [LeadQABoard](qa/leadqaboard.md) | Runs LeadQA's multi-model boards for quality, security, and release trade-offs |
| [LeadQAScout](qa/leadqascout.md) | Runs the QA team's scouts for checkers, test tooling, and security advisories |
| [ScoutQA](qa/scoutqa.md) | Short-lived QA team explorer under LeadQAScout |
| [LeadQATester](qa/leadqatester.md) | QA sub-lead for final verification and edge-case probing of built slices |
| [QATester](qa/qatester.md) | QA tester worker executing verification replays, browser checks, and edge-case probes |
| [LeadQADelivery](qa/leadqadelivery.md) | QA sub-lead for Git, CI/CD, versions, releases, docs, and the `INDEX.md` rebuild script |
| [QADelivery](qa/qadelivery.md) | QA delivery worker running CI tasks, security scans, docs hygiene, and release prep |
| [LeadQAArchitect](qa/leadqaarchitect.md) | QA sub-lead reviewing architecture against code rules and owning static checkers |
| [QAArchitect](qa/qaarchitect.md) | QA architecture worker running structural checks, code-rule audits, and static rules |
| [KeeperQA](qa/keeperqa.md) | Read-only sentinel watching the QA team and verifying `INDEX.md` accuracy |

## Shared roles (`shared/`, 3)

| Card | What it is |
| --- | --- |
| [Board member](shared/board-member.md) | Independent multi-model board member giving one isolated opinion per round |
| [Proof matrix author](shared/proof-matrix-author.md) | Drafts the exhaustive proof matrix, verifiers, and failing-first proof tests; never builds |
| [Adversarial reviewer](shared/adversarial-reviewer.md) | Independent fresh-session reviewer on another model that tries to break built work |
