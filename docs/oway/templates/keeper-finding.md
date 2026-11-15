# Template: keeper finding
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

One note per finding in the keeper registry (`notes/INDEX.md` plus one file each). A keeper only states facts; it never gives an instruction, a fix or a recommendation. See the keeper rules in [Rules](../rules.md#keeper-rules-learned-from-a-running-keeper).

```text
FINDING <TYPE> | <fact> | PROOF: <command + output, file:line, PID, UTC> | SINCE: <UTC>
```

Types: DRIFT, LOOP, STUCK, NO_PROGRESS, PACE, DESIGN, INTENT, DOC_STALE, FAKE_PROOF, HARDCODE, TAMPER, POLICY, SYSTEM.

After LeadKeeper has replayed the proof:

- to the lead concerned: one queued line starting with `[KEEPER]`;
- to the owner: at most 200 characters (title, fact, one proof), in the project language, no paths;
- not confirmed: logged as REJECTED, nobody is told.

Alert once, remind after 6 hours if still open, write one "resolved" line when fixed.
