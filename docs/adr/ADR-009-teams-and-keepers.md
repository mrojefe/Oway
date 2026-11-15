# ADR-009: Teams with leads, and read-only keepers that only warn
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

- **Status:** Accepted
- **Date:** 2026-11-15
- **Deciders:** the repository owner

## Context and problem statement

One agent doing everything loses the goal, and an agent that both builds and checks can make its own checks pass. In a real project two models reviewed one side task through five versions over four days while the main goal was paused; only the owner's manual stop ended it.

## Considered options

1. One agent with more rules. Rejected: agents follow fewer rules the more they are given.
2. A watcher that can stop work. Rejected: one bad judgment that spreads can stop the whole project.
3. Named teams with one lead each, and read-only keepers whose verified warnings go to the lead and the owner. Chosen.

## Decision and invariants

- LeadOway orchestrates and talks to the owner; it never checks work itself. Its own team: OwayHelpers (setup only), LeadOwayBoard, LeadOwayScout, and KeeperOway.
- Four teams: Product (scope), UIX (design, only with a UI), Dev (builds), QA (tests and judges). Dev builds, QA tests and judges. Each team has a lead, a board lead and a scout lead. Dev has a fixed core and builders picked per project.
- Only leads talk to the owner. Across teams, only leads talk. Messages point to files; they are not memory.
- One KeeperX per team, read-only, awake only while its team works, reporting to LeadKeeper only. LeadKeeper replays each proof, then warns the lead concerned and always the owner. Leads decide and act.
- Which agent runs on which model is decided later, per agent.

## Consequences

- Positive: loops are seen early (at round 3), builders never grade themselves, and the method grows through LeadKeeper's issues on this repository.
- Negative: more agents and more tokens; mitigated by short-lived workers and scouts.
- Full text: [Teams and roles](../oway/teams-and-roles.md).
