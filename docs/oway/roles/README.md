# Oway role cards
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

One card per role, from the [role card template](../templates/role-card.md). The roles and how they fit are in [Teams and roles](../teams-and-roles.md). Board leads, scout leads and scouts have the same shape in every team, so they share one card each in `shared/`. All cards are drafts until the engine installs them.

| Folder | Card | What it is |
| --- | --- | --- |
| oway | [LeadOway](oway/leadoway.md) | The project main: orchestrates the teams and talks to the owner |
| oway | [OwayHelper](oway/owayhelper.md) | Setup-only helper: interviews the owner and prepares the project |
| oway | [LeadOwayBoard](oway/leadowayboard.md) | Runs LeadOway's boards for hard cross-team choices |
| oway | [LeadOwayScout](oway/leadowayscout.md) | Runs research that no single team owns |
| keeper | [LeadKeeper](keeper/leadkeeper.md) | The top watcher: verifies keeper findings and warns |
| keeper | [KeeperX](keeper/keeperx.md) | Read-only watcher of one team (KeeperProduct, KeeperUIX, KeeperDev, KeeperQA, KeeperOway) |
| product | [LeadProduct](product/leadproduct.md) | Runs the Product team: turns the owner's words into scope |
| uix | [LeadUIX](uix/leaduix.md) | Runs the UIX team: designs with the owner |
| uix | [UIX worker](uix/uix-worker.md) | UIX1, UIX2...: build the design artifacts |
| dev | [LeadDev](dev/leaddev.md) | Runs the Dev team: plans how each slice is built |
| dev | [DevOps](dev/devops.md) | Builds the product's environments, infrastructure and migrations |
| dev | [Dev builder](dev/dev-builder.md) | A builder picked for the project: DevBackend, DevFrontend, DevData, DevAI or DevMobile |
| qa | [LeadQA](qa/leadqa.md) | Runs the QA team: tests and judges |
| qa | [LeadQATester](qa/leadqatester.md) | Writes and runs the tests that prove each check |
| qa | [LeadQADelivery](qa/leadqadelivery.md) | Git, CI/CD, versions, releases, docs and the index script |
| qa | [LeadQAArchitect](qa/leadqaarchitect.md) | Reviews the architecture against the code rules and keeps the checkers |
| shared | [LeadXBoard](shared/leadxboard.md) | Runs the boards of one team (LeadProductBoard, LeadUIXBoard, LeadDevBoard, LeadQABoard) |
| shared | [LeadXScout](shared/leadxscout.md) | Runs the scouts of one team (LeadProductScout, LeadUIXScout, LeadDevScout, LeadQAScout) |
| shared | [ScoutX](shared/scoutx.md) | A short-lived explorer (ScoutProduct, ScoutUIX, ScoutDev, ScoutQA) |
