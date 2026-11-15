# om (Oway medium)

om is the light version of [Oway](../README.md) for everyday work: browsing, installing an app, a quick fix, a small build, or a full mission. It keeps Oway's principles (real proof, stated limits, no forged approvals, the author is not the validator, files are the truth, very short chat) and drops the team structure. om replaces CGM ("CortexGate Medium").

## Three sizes
| Size | For | What happens |
| --- | --- | --- |
| Quick | One action | Do it, one line with one proof |
| Task | A few steps that can be undone | Short todo, one proof per step |
| Mission | Big or risky work, or `/om-plan` | One approval packet, capability check, GO, work, one review, walkthrough |

Payments, deletes, messages to anyone, publishing and production changes always need the owner first, at every size.

## What is inside
| Path | What it is | Loaded as |
| --- | --- | --- |
| `rules/AGENTS.md` | The always-on rules | pi `APPEND_SYSTEM.md`, OpenCode `AGENTS.md`, Antigravity plugin rules |
| `skills/om-plan/` | Mission workflow + plan, walkthrough and decision templates | skill |
| `skills/om-uix/` | UI style hub (117 MIT styles and themes) | skill |
| `skills/om-assist/` | Starts the side assistant | skill |
| `agents/om-caps.md` | Capability check for a Mission | subagent (pi: prompt template) |
| `agents/om-review.md` | Independent review at the end of a Mission | subagent (pi: prompt template) |
| `agents/om-assist.md` | Side assistant, talks only with the owner | subagent (pi: prompt template) |
| `DEPLOYMENTS.md` | Every install target, per host | read by `sync-om.sh` |
| `sync-om.sh` | Applies or checks the targets; retires old CGM links | `./sync-om.sh [--check\|--dry-run]` |

## Install or update on a host
```bash
git clone https://github.com/mrojefe/Oway ~/Desktop/_CG-Gov/Oway   # once
cd ~/Desktop/_CG-Gov/Oway && git pull
./om/skills/om-uix/scripts/fetch_catalog.sh   # UI style catalog (not in Git)
./om/sync-om.sh --dry-run    # see what changes
./om/sync-om.sh              # apply; old paths are backed up in ~/.om-deploy-backups/
./om/sync-om.sh --check      # must print RESULT: OK
```
Then reload: pi `/reload`, OpenCode `opencode reload`, restart Antigravity.

## From CGM to om
| CGM | om |
| --- | --- |
| `cgm-plan` (7 phases, goal OK + matrix OK + GO) | `om-plan` (one approval packet + GO) |
| no small-task path | Quick and Task sizes in the rules |
| `cgm-ad-rev` | `om-review` |
| `cgm-caps`, `cgm-assist`, `cgm-uix` | `om-caps`, `om-assist`, `om-uix` |
| `_CG-Gov/cgm/` without Git | `om/` in the Oway repo |
