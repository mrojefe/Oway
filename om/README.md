# om (Oway medium)

om is the light version of [Oway](../README.md) for everyday work: browsing, installing an app, a quick fix, a small build, or a full mission. It keeps Oway's principles (real proof, stated limits, no forged approvals, the author is not the validator, files are the truth, very short chat) and drops the team structure.

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
| `DEPLOYMENTS.md` | Where each tool reads om, and your own optional settings | read by you |
| `sync-om.sh` | Links om into your tools, or checks that it is | `./sync-om.sh [--check\|--dry-run] --tools ...` |

## Install or update
Clone the repo anywhere, then:
```bash
git clone https://github.com/mrojefe/Oway && cd Oway     # once; later: git pull
om/skills/om-uix/scripts/fetch_catalog.sh                 # UI style catalog (not in Git)
om/sync-om.sh --dry-run --tools pi,opencode,antigravity   # see what changes
om/sync-om.sh --tools pi,opencode,antigravity             # apply; replaced paths are backed up
om/sync-om.sh --check --tools pi,opencode,antigravity     # must print RESULT: OK
```
Keep your tool list in `~/.config/om/tools` to skip `--tools`. Other tools and old paths to retire go in `~/.config/om/extra` and `~/.config/om/retire` (see `DEPLOYMENTS.md`). Then reload the tool: pi `/reload`, OpenCode `opencode reload`, Antigravity restart.
