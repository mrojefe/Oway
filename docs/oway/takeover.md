# Taking over a project
Created: 2026-11-15T15:00:00Z · Last edited: 2026-11-15T15:00:00Z

How Oway joins a project that already has code or docs, including a project on CGSpec 0.3. Written from the CampusNest test run. Comment on any line.

## The one rule

**Never remove the old guard before the new one works.** Keep the old engine, hooks and skills until `oway doctor` passes on the project. Taking them out first leaves the project with no checks at all. The CampusNest test did that, and it was the first gap found.

## Order of steps

Each step is one commit on one branch, so any step can be reverted alone.

1. **Check the tool.** The Oway tool is installed on the Platform and `oway doctor --version` answers. If not, stop at step 3 and list what is missing (see "When the owner or the Platform is not there").
2. **Map.** Scouts list every file with the table below: old path, new path, type, state. The list goes to `_oway/research/RES-NNN-takeover-map.md`. Nothing moves yet.
3. **Move.** `git mv` each file to its new path, so history follows. Fix every link in the same commit; links stay relative.
4. **Headers.** Add the header to every moved file (types and states in [Rules](rules.md)). Old approvals follow "Approvals made before Oway, or outside GitHub" in [Rules](rules.md).
5. **Decisions.** Pull ADRs out of the spines (see "ADRs taken out of old docs" below).
6. **Index and ledger.** Run `oway index` and write the first ledger line: "takeover from CGSpec 0.3.4, map in RES-NNN".
7. **Doctor.** Run `oway doctor`. Files that still break a rule go in the legacy list, with your OK.
8. **Switch the guard.** Only now: install the Oway hooks, then remove the old engine, skills and hooks in their own commit. `AGENTS.md` points to Oway.
9. **Review.** One pull request. You approve it; nothing is merged without you.

## CGSpec 0.3 to Oway paths

| CGSpec 0.3 | Oway | Note |
| --- | --- | --- |
| `docs/00-INDEX.md` | `_oway/INDEX.md` | Rebuilt by `oway index`, not moved |
| `docs/00-INBOX.md` | `_oway/INBOX.md` | Log, no header |
| `docs/_memlog.md` | `_oway/LEDGER.md` | Old lines kept as they are, below a "Before Oway" line |
| `docs/_cgspec/project.json` | `_oway/config.json` | Keys renamed per [the config schema](schemas/oway-config.schema.json) |
| `docs/spines/01-INTENT.md` ... `05-DELIVERY.md` | `_oway/spines/01-intent.md` ... `05-delivery.md` | Lower case; `02-OOUX.md` becomes `02-objects.md` |
| `docs/adrs/` | `_oway/decisions/` | Same ADR numbers |
| `docs/slices/` | `_oway/slices/` | A slice without checks gets `state: draft` |
| `docs/prototypes/_vision/` | `_oway/design/` | One folder per version, see [Design](design.md) |
| `_vision/html-prototypes/vN-*.html` | `_oway/design/versions/vN/` | `prototype.html`, or `variant-a.html`, `variant-b.html`... |
| `_vision/screenshots/` | `_oway/design/versions/vN/screenshots/` | Split by version |
| `_vision/references/`, `user-references/` | `_oway/design/references/` | One folder, named by source (`you-...`, `competitor-...`) |
| `_vision/docs/*.md` | `_oway/research/` or `design/versions/vN/note.md` | An analysis is research; what one version tried is its note |
| logos, brand | `_oway/design/brand/` | |
| `docs/prototypes/_snapshots/` | `_oway/evidence/visual-baselines/` | |
| decisions shown as "approved in chat" | a ledger line | See [Rules](rules.md), old approvals |
| `docs/_cgspec/02-research/RES-NNN` | `_oway/research/RES-NNN` | Only research about this project; method research stays in the tool |
| councils | boards | A council file becomes a board summary in `research/` |
| `.agents/skills/cgspec-*`, `.agents/hooks.json` | removed at step 8 | The tool brings its own; nothing is copied |
| `.gitkeep` files, empty state files | removed | A folder exists only when it has a file |

A path not in this table is listed in the map as "unknown" and waits for you.

## ADRs taken out of old docs

Old spines often hold choices without a record. A scout may pull a choice into an ADR only when the source says it was chosen. The ADR gets:

- `state: proposed`, never accepted, unless the ledger or inbox shows your OK (then cite the line);
- "Alternatives: not recorded in the source" when there are none, instead of inventing some;
- a link back to the line in the spine it came from.

You confirm each one. Until then the spine keeps the text, and the ADR is a draft.

## When the owner or the Platform is not there

An agent alone cannot finish Step 0. It writes what is missing in `_oway/project.md`, under "Setup pending", and does not guess:

| Missing | Needs | Until then |
| --- | --- | --- |
| Owner profile | The OwayHelpers interview, on the Platform | `profile: not set`; LeadDev writes no `CONSTRAINTS.md` |
| Code rules (`CONSTRAINTS.md`) | The profile and the Dev talk | Default rules from [Rules](rules.md) apply |
| Keeper report interval, quota tracking | You, at setup | Keepers stay off |
| GitHub bot app, protected `main`, sync Action | You, in GitHub settings | Approvals are written as ledger lines |
| The three first parts (goal, scope, first milestone) | You | No slice can be approved |
| The Oway tool | Installed on the Platform | Keep the old engine (the one rule above) |

## Upgrade mode

When Oway itself gets a new version, the same steps run with the change list of that version in place of the table above.
