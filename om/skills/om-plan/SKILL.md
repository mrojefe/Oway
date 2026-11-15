---
name: om-plan
description: >-
  om Mission workflow (Oway medium). Owner-started only: run it when the owner types /om-plan or asks for a Mission. One plan file, one approval packet (goal + proof matrix + restrictions), a capability check, one GO, autonomous work, one independent review, a walkthrough. Not for Quick or Task sizes.
---

# om-plan: the Mission size

Rules: `rules/AGENTS.md` (always on). This skill only adds the Mission steps.
Only the owner starts it. Without a confirmed goal, nothing is changed. `/om-assist` can be used at any time for side questions.

States: `DRAFT` -> `LOCKED` -> `EXECUTING` (-> `REPLANNING`) -> `REVIEW` -> `DONE`. A plan-only run ends at `HANDED_OFF`.

## 1. Draft (state DRAFT)
- Open the plan file at the first message, from [plan-template.md](references/plan-template.md). Fill it as the talk goes; chat only links to it.
- Restate the goal in one or two sentences, with what is out of scope.
- Scout open source first. Record each option and its checked licence (permissive only, rule 1.8).
- Check now what can be checked now (tools, accounts, access, docs). Write each real limit with its evidence.
- Write the proof matrix: every interaction the owner (or the end user) will have with the result, each with a real proof and its medium. Video when it scrolls, moves or is a multi-step flow; screenshot + live output for a fixed state; command output for non-UI work.
- Write the restrictions (secrets, protected paths, ports, services, Git) and the change zones.
- Ask: plan only, or plan and do it here? For plan only, name who runs it.

## 2. One approval packet
Show the owner, in one message with the plan link: goal, proof matrix, restrictions, real limits, and the question above. One explicit OK covers all of it. Silence, a question or your own text is not an OK. A later change to the goal or the matrix needs a new OK.

## 3. Capability check
Start `om-caps` with the goal, the matrix and what the owner said is available. Put its table in the plan. A `MISSING` item blocks the start: fix it or mark the dependent proof `BLOCKED` with the owner. `HUMAN_STEP` items go into the steps at their exact place.
For plan only: check against the machine that will run it; mark what you cannot check from here `UNVERIFIED_HERE` with the exact command to run first.

## 4. GO (state LOCKED)
Finish the plan (steps, human steps, cleanup, what the owner gets) and ask for one `GO`. The approval packet is not the GO. After GO the scope is locked. Plan only: stop here, state `HANDED_OFF`.

## 5. Work (state EXECUTING)
- Work alone. Chat only for a result, a needed pause or a block.
- Keep going on everything that is not blocked; collect non-urgent questions for the end.
- At a `HUMAN_STEP`, ask with exact instructions, check it at once, continue.
- A real crossroads: one decision packet ([decision-packet.md](references/decision-packet.md)), not many questions.
- The owner changes scope mid-way: stop and offer (1) finish the locked plan, then queue the change (recommended), or (2) pause and replan (`REPLANNING`).
- Clean scratch files, test containers, ports and processes before the review.

## 6. Review (state REVIEW)
Once, at the end. Start `om-review` with only the goal, restrictions, protected zones, matrix and evidence paths. Use another model when one is available; say so when it is not. On `FAIL`: fix, capture new real proof, review again until `PASS`. The owner may skip the review for a small Mission; record that in the plan.

## 7. Walkthrough (state DONE)
Write [walkthrough-template.md](references/walkthrough-template.md): one proof per matrix item with its revision and the command or action that made it, the restrictions proof, the review summary, every `BLOCKED` item with evidence, and what the owner can do now. Chat: the path and one line. The owner validates once, here.
