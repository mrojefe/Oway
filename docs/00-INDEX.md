# Oway documentation map
Created: unknown · Last edited: 2026-11-19T13:10:00Z

[oway/README.md](oway/README.md) is the v0.4 Oway method entry. [GLOSSARY.md](GLOSSARY.md) defines canonical Oway and om terms. [METHOD.md](METHOD.md) is the v0.3 engine specification. [STATUS.md](STATUS.md) is the single implementation-status reference. [CHANGELOG.md](../CHANGELOG.md) maps package versions to changes.

## Current implementation

| Area | Entry | Status |
| --- | --- | --- |
| Oway v0.4 method | [oway/README.md](oway/README.md) | Method, templates, 48 role cards, and `engine/oway/` CLI (`0.3.12`) |
| Canonical glossary | [GLOSSARY.md](GLOSSARY.md) | Shared Oway and om terminology |
| Method and design path (v0.3) | [METHOD.md](METHOD.md) | Current v0.3 engine specification; implementation limits are in STATUS |
| Agent operating contract | [CONTRACT.md](../engine/CONTRACT.md) | Installed short contract |
| Engine state and hook formats | [FORMATS.md](../engine/FORMATS.md) | Current formats and command contract |
| Install, doctor and ledger | [engine/](../engine/) | Implemented; validation must cite the tested revision and skipped checks |
| Source ingestion and v0.1 adoption | [engine/](../engine/) | Implemented; independent safety review open |
| Browser journeys, visual audit, prototype bundling, impact map | [engine/](../engine/) | Implemented; browser-backed and agent-driven review open |
| Workflow skills | [skills/](../skills/) | Nine skills plus pivot alias; runtime rehearsal pending |
| Team roles | [teams-and-roles.md](oway/teams-and-roles.md) | Oway v0.4 role cards and keeper specs |
| Project templates | [templates/](../templates/) | Packaged; consumer validation remains project-specific |
| Current research | [02-research/](_cgspec/02-research/README.md) | [RES-007](_cgspec/02-research/RES-007-claude-code-hooks-benchmark-and-hygiene-gates.md) hook taxonomy and [RES-008](_cgspec/02-research/RES-008-ostack-gstack-governance-philosophy-comparison.md) ostack/gstack comparison concluded 2026-10-30; queued spikes in [RESEARCH-QUEUE.md](_cgspec/02-research/RESEARCH-QUEUE.md) |

## Historical v0.1 records

The [five spines](spines/README.md), [earlier ADRs](adr/README.md), [research notes](_cgspec/02-research/README.md), [council notes](_cgspec/03-council/README.md) and [old ledger](_memlog.md) preserve earlier work. ADR-001 through ADR-005 are v0.1 history: their status labels, paths, tool and product-specific guarantees do not establish current behavior. [ADR-006](adr/ADR-006-main-branch-governance.md) is the current repository-specific governance decision; it is not a default imposed on consumer projects. Use the current specification and `engine/` for new work.
