# Installing om

om lives in this repo, in `om/`. Each tool reads it through links, so a `git pull` updates every tool at once. `sync-om.sh` creates and checks those links. The repo holds no machine names and no personal paths: what is yours stays in `~/.config/om/` (see "Your own settings").

## Built-in tools

Pick the tools you use with `--tools` (or `OM_TOOLS`, or the file `~/.config/om/tools`). Add `--oway-skills` (or `OM_OWAY_SKILLS=1`) to also link every `oway-*` skill of the Oway method, not only the om ones.

| Tool | Skills | Agents | Rules (always on) |
| --- | --- | --- | --- |
| `pi` | `~/.pi/agent/skills/om-plan`, `om-assist`, `oway-uix` (links) | `~/.pi/agent/prompts/om-*.md` (links; pi has no agent files, so agents load as prompts) | `~/.pi/agent/APPEND_SYSTEM.md` (link) |
| `opencode` | `~/.config/opencode/skills/om-plan`, `om-assist`, `oway-uix` (links) | `~/.config/opencode/agents/om-*.md` (copies, see below) | `~/.config/opencode/AGENTS.md` (link) |
| `claude` | `~/.claude/skills/<name>` (links) | none | none: your own `~/.claude/CLAUDE.md` is never touched |
| `antigravity` | plugin: `~/.gemini/config/plugins/om` links to `om/` (it carries `om-plan` and `om-assist`); only the shared skills go to `~/.gemini/config/skills/`: `oway-uix` (and every `oway-*` with `--oway-skills`) | same plugin | same plugin (`rules/AGENTS.md`) |
| `oway` | none | none | `~/.local/bin/oway` links to `om/bin/oway`, so agents can run `oway style ...` from anywhere |

Reload after a sync: pi `/reload`, OpenCode `opencode reload`, Antigravity restart.

## Your own settings (optional, never in the repo)

| File | One entry per line | Use |
| --- | --- | --- |
| `~/.config/om/tools` | tool names, e.g. `pi` | which built-in tools to sync here |
| `~/.config/om/extra` | `method target source` | other places: `symlink ~/.mytool/skills/om-plan skills/om-plan` or `opencode-agent <target> agents/om-caps.md`. `source` is relative to `om/`. |
| `~/.config/om/retire` | a path | old paths to back up and remove, for example links to a tool you replaced. Backed up under `~/.om-deploy-backups/<time>/`. |

`~` and `$HOME` work in targets. Lines starting with `#` are ignored.

## Notes
- **The design skill is shared with Oway.** `oway-uix` lives in `skills/` at the repo root and has a full mode (Oway projects) and a light mode (om). pi, OpenCode and Antigravity link it straight from there. Its style library is not in Git: run `oway style fetch` once per machine (cache in `~/.cache/oway/styles`).
- **OpenCode agents are copies.** OpenCode V2 drops agent files with a V1 `tools:` list, so the script writes a copy with only `description` + `mode: subagent` + the body.
- **Files the script never touches:** your own global rules (for example `~/.gemini/config/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.pi/agent/AGENTS.md`). If they name old skills, edit them by hand.
- **Antigravity** merges the plugin's `rules/AGENTS.md` by itself, so rules you also keep in a global file load twice.
- The script moves, never deletes: replaced paths go to `~/.om-deploy-backups/<time>/`.
