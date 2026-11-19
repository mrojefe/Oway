# Oway documentation map
Created: unknown · Last edited: 2026-11-19T15:00:00Z

[oway/README.md](oway/README.md) is the Oway v0.4 method entry, paired with the [49 role cards and 5 team contracts](../agents/README.md), [36 shared skills](../skills/), and [`om/`](../om/README.md) for everyday medium tasks. [GLOSSARY.md](GLOSSARY.md) defines canonical Oway and `om` terms, [STATUS.md](STATUS.md) is the single implementation-status reference, and [CHANGELOG.md](../CHANGELOG.md) tracks releases. Legacy [METHOD.md](METHOD.md) remains for CGSpec v0.3 consumer compatibility ([ADR-007](adr/ADR-007-cgspec-becomes-oway.md)).

## Current implementation

| Area | Entry | Status |
| --- | --- | --- |
| Oway v0.4 method | [oway/README.md](oway/README.md) | Method, templates, `_oway/` layout, and `engine/oway/` CLI (`0.3.13`) |
| Agent roles & teams | [agents/README.md](../agents/README.md) | 49 canonical role cards (`keeper/` unified under `LeadKeeper`) + 5 `TEAM.md` contracts |
| Shared skill stack | [skills/](../skills/) | 10 `oway-*` skills, `free-ui-ux-scout`, and 25 MIT Addy Osmani skills synced via `oway sync` |
| Everyday medium mode | [om/README.md](../om/README.md) | `om-plan`, `om-assist`, `om-caps`, `om-review` |
| Canonical glossary | [GLOSSARY.md](GLOSSARY.md) | Shared Oway and `om` terminology |
| Agent operating contract | [CONTRACT.md](../engine/CONTRACT.md) | Installed short contract |
| Engine state and hook formats | [FORMATS.md](../engine/FORMATS.md) | Current formats and command contract |
| Legacy v0.3 engine spec | [METHOD.md](METHOD.md) | Retained for v0.3 consumer compatibility and `oway takeover --from cgspec-0.3` |
| Install, doctor and ledger | [engine/](../engine/) | Implemented; validation must cite the tested revision and skipped checks |
| Current research | [02-research/](_cgspec/02-research/README.md) | [RES-007](_cgspec/02-research/RES-007-claude-code-hooks-benchmark-and-hygiene-gates.md) hook taxonomy and [RES-008](_cgspec/02-research/RES-008-ostack-gstack-governance-philosophy-comparison.md) ostack/gstack comparison; queued spikes in [RESEARCH-QUEUE.md](_cgspec/02-research/RESEARCH-QUEUE.md) |

## Historical v0.1 records

The [five spines](spines/README.md), [earlier ADRs](adr/README.md), [research notes](_cgspec/02-research/README.md), [council notes](_cgspec/03-council/README.md) and [old ledger](_memlog.md) preserve earlier work. ADR-001 through ADR-005 are v0.1 history: their status labels, paths, tool and product-specific guarantees do not establish current behavior. [ADR-006](adr/ADR-006-main-branch-governance.md) is the current repository-specific governance decision; it is not a default imposed on consumer projects. Use the current Oway specification and `engine/` for new work.
