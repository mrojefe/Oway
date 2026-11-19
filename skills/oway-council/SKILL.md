---
name: oway-council
description: Research and resolve a consequential architecture, security, data, hosting, or product trade-off with a logged council and a proposed decision.
---

# Decide a consequential choice (`oway-council`)

## 1. Oway v0.4 Multi-Model Boards & ADRs (`_oway/boards/` & `_oway/decisions/`)

In Oway v0.4, multi-model councils are **Boards** run by each team's board lead (`LeadOwayBoard`, `LeadProductBoard`, `LeadUIXBoard`, `LeadDevBoard`, `LeadQABoard`):

1. **Board Execution (`_oway/boards/`)**:
   - Only `LeadOway`, `LeadProduct`, `LeadUIX`, `LeadDev`, or `LeadQA` starts a board.
   - The board lead frames one bounded question with constraints and primary sources, then launches independent `board-member` sessions on **different AI models**, one separate run per member (one agent writing all opinions itself is a fake).
   - At most 3 rounds per board. Each round log records model attribution, and the board lead writes a neutral synthesis in `_oway/boards/` (never giving an opinion itself) and delivers it to its team lead.
2. **Decision Records (`_oway/decisions/ADR-NNN-<slug>.md`)**:
   - Following [documentation-and-adrs](../documentation-and-adrs/SKILL.md) and `docs/oway/templates/adr.md`, every consequential choice (`type: decision`, `state: proposed`) is recorded in `_oway/decisions/ADR-NNN-<slug>.md` with Context, Decision, Alternatives considered, and Consequences.
   - An ADR is never deleted; when superseded, a new ADR replaces it and the old header state becomes `superseded`.

---

## 2. Core Rigor & Legacy v0.3 Compatibility (`docs/_cgspec/03-councils/`)

Read only what the current step needs, once per session: the [agent contract](../../engine/CONTRACT.md), affected spines, current ADRs and [method sections 7 and 7b](../../docs/METHOD.md) (that section only). Write one bounded question and decision criteria before proposals. Research authoritative sources; run a feasibility spike in `.cgspec-scratch/` when latency, cost, memory or failure behavior decides the choice.

For a consequential T3 choice, log a board in `_oway/boards/` (or a council in `docs/_cgspec/03-councils/COUNCIL-NNN-<slug>/` on v0.3 layouts): `00-brief`, round files per lens, and `99-outcome`. Compare simplicity/cost, security/reliability and scale/maintenance. Use distinct models when available and label a single-model council PARTIAL. The supervisor synthesizes; debaters do not approve. Keep the council at its spec cap of four agents. For an ordinary reversible choice, a scoped ADR and one independent reviewer suffice when the tier allows it.

After a T3 council proposes its ADR, have an independent reviewer who did not write the proposal or supervise the council challenge it using the strongest suitable model available in the host. Give the reviewer the source evidence, assumptions, threat model and reversibility criteria, not just the council's conclusion. If the model or evidence is unavailable, mark this final challenge PARTIAL. The reviewer reports; the user approves. Check the live model catalogue before recommending a model, and do not claim a model is stronger or cheaper without reliable evidence.

The outcome is a `proposed` ADR in `_oway/decisions/` (`docs/adrs/` in v0.3), with options, sources, measured trade-offs, reversibility and fitness checks. Explain the recommended option in plain terms and seek the user's decision where the spec requires it. Record explicit approval through a supported path; never infer it from an agent verdict. Reopen an ADR when its constraint or measured budget changes.
