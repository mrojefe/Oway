# om deployments (where om is installed)

Source of truth: the Oway repo, folder `om/`. Each host has a git clone; the clone's `om/` is the om root.
Suggested clone path on both hosts: `~/Desktop/_CG-Gov/Oway`. Update a host with `git pull`, then `./om/sync-om.sh`.
Host names are what `hostname` prints: laptop = `ojefe`, VPS = `vmi3298109`.

`sync-om.sh` reads the table below for the host it runs on. Add a row here first, then run it.
Methods: `symlink` (target -> om root/source), `opencode-agent` (generated copy, see below),
`retire` (an old CGM path: backed up to `~/.om-deploy-backups/<ts>/`, then removed; source column is `-`).

```om-targets
# host       tool         method          target                                    source
# ---------------- laptop (ojefe) ----------------
ojefe        opencode     symlink         ~/.config/opencode/skills/om-plan         skills/om-plan
ojefe        opencode     symlink         ~/.config/opencode/skills/om-uix          skills/om-uix
ojefe        opencode     symlink         ~/.config/opencode/skills/om-assist       skills/om-assist
ojefe        opencode     opencode-agent  ~/.config/opencode/agents/om-caps.md      agents/om-caps.md
ojefe        opencode     opencode-agent  ~/.config/opencode/agents/om-review.md    agents/om-review.md
ojefe        opencode     opencode-agent  ~/.config/opencode/agents/om-assist.md    agents/om-assist.md
ojefe        opencode     symlink         ~/.config/opencode/AGENTS.md              rules/AGENTS.md
ojefe        pi           symlink         ~/.pi/agent/skills/om-plan                skills/om-plan
ojefe        pi           symlink         ~/.pi/agent/skills/om-uix                 skills/om-uix
ojefe        pi           symlink         ~/.pi/agent/skills/om-assist              skills/om-assist
ojefe        pi           symlink         ~/.pi/agent/prompts/om-caps.md            agents/om-caps.md
ojefe        pi           symlink         ~/.pi/agent/prompts/om-review.md          agents/om-review.md
ojefe        pi           symlink         ~/.pi/agent/prompts/om-assist.md          agents/om-assist.md
ojefe        pi           symlink         ~/.pi/agent/APPEND_SYSTEM.md              rules/AGENTS.md
ojefe        antigravity  symlink         ~/.gemini/config/plugins/om               .
ojefe        dsh          symlink         ~/.dsh/skills/om-plan                     skills/om-plan
ojefe        dsh          symlink         ~/.dsh/skills/om-uix                      skills/om-uix
ojefe        dsh          symlink         ~/.dsh/skills/om-assist                   skills/om-assist
ojefe        dsh-dev      symlink         ~/Projects/deepseek-harness/apps/desktop/.desktop-build/development/home/skills/om-plan    skills/om-plan
ojefe        dsh-dev      symlink         ~/Projects/deepseek-harness/apps/desktop/.desktop-build/development/home/skills/om-uix     skills/om-uix
ojefe        dsh-dev      symlink         ~/Projects/deepseek-harness/apps/desktop/.desktop-build/development/home/skills/om-assist  skills/om-assist
ojefe        opencode     retire          ~/.config/opencode/skills/cgm-plan        -
ojefe        opencode     retire          ~/.config/opencode/skills/cgm-uix         -
ojefe        opencode     retire          ~/.config/opencode/skills/cgm-assist      -
ojefe        opencode     retire          ~/.config/opencode/agents/cgm-caps.md     -
ojefe        opencode     retire          ~/.config/opencode/agents/cgm-ad-rev.md   -
ojefe        opencode     retire          ~/.config/opencode/agents/cgm-assist.md   -
ojefe        pi           retire          ~/.pi/agent/skills/cgm-plan               -
ojefe        pi           retire          ~/.pi/agent/skills/cgm-uix                -
ojefe        pi           retire          ~/.pi/agent/skills/cgm-assist             -
ojefe        pi           retire          ~/.pi/agent/prompts/cgm-caps.md           -
ojefe        pi           retire          ~/.pi/agent/prompts/cgm-ad-rev.md         -
ojefe        pi           retire          ~/.pi/agent/prompts/cgm-assist.md         -
ojefe        antigravity  retire          ~/.gemini/config/plugins/cgm              -
ojefe        dsh          retire          ~/.dsh/skills/cgm-plan                    -
ojefe        dsh          retire          ~/.dsh/skills/cgm-uix                     -
ojefe        dsh          retire          ~/.dsh/skills/cgm-assist                  -
ojefe        dsh-dev      retire          ~/Projects/deepseek-harness/apps/desktop/.desktop-build/development/home/skills/cgm-plan    -
ojefe        dsh-dev      retire          ~/Projects/deepseek-harness/apps/desktop/.desktop-build/development/home/skills/cgm-uix     -
ojefe        dsh-dev      retire          ~/Projects/deepseek-harness/apps/desktop/.desktop-build/development/home/skills/cgm-assist  -
# ---------------- VPS (vmi3298109) ----------------
vmi3298109   opencode     symlink         ~/.config/opencode/skills/om-plan         skills/om-plan
vmi3298109   opencode     symlink         ~/.config/opencode/skills/om-uix          skills/om-uix
vmi3298109   opencode     symlink         ~/.config/opencode/skills/om-assist       skills/om-assist
vmi3298109   opencode     opencode-agent  ~/.config/opencode/agents/om-caps.md      agents/om-caps.md
vmi3298109   opencode     opencode-agent  ~/.config/opencode/agents/om-review.md    agents/om-review.md
vmi3298109   opencode     opencode-agent  ~/.config/opencode/agents/om-assist.md    agents/om-assist.md
vmi3298109   opencode     symlink         ~/.config/opencode/AGENTS.md              rules/AGENTS.md
vmi3298109   pi           symlink         ~/.pi/agent/skills/om-plan                skills/om-plan
vmi3298109   pi           symlink         ~/.pi/agent/skills/om-uix                 skills/om-uix
vmi3298109   pi           symlink         ~/.pi/agent/skills/om-assist              skills/om-assist
vmi3298109   pi           symlink         ~/.pi/agent/prompts/om-caps.md            agents/om-caps.md
vmi3298109   pi           symlink         ~/.pi/agent/prompts/om-review.md          agents/om-review.md
vmi3298109   pi           symlink         ~/.pi/agent/prompts/om-assist.md          agents/om-assist.md
vmi3298109   pi           symlink         ~/.pi/agent/APPEND_SYSTEM.md              rules/AGENTS.md
vmi3298109   antigravity  symlink         ~/.gemini/config/plugins/om               .
vmi3298109   opencode     retire          ~/.config/opencode/skills/cgm-plan        -
vmi3298109   opencode     retire          ~/.config/opencode/skills/cgm-uix         -
vmi3298109   opencode     retire          ~/.config/opencode/skills/cgm-assist      -
vmi3298109   opencode     retire          ~/.config/opencode/agents/cgm-caps.md     -
vmi3298109   opencode     retire          ~/.config/opencode/agents/cgm-ad-rev.md   -
vmi3298109   opencode     retire          ~/.config/opencode/agents/cgm-assist.md   -
vmi3298109   pi           retire          ~/.pi/agent/skills/cgm-plan               -
vmi3298109   pi           retire          ~/.pi/agent/skills/cgm-uix                -
vmi3298109   pi           retire          ~/.pi/agent/skills/cgm-assist             -
vmi3298109   pi           retire          ~/.pi/agent/prompts/cgm-caps.md           -
vmi3298109   pi           retire          ~/.pi/agent/prompts/cgm-ad-rev.md         -
vmi3298109   pi           retire          ~/.pi/agent/prompts/cgm-assist.md         -
vmi3298109   antigravity  retire          ~/.gemini/config/plugins/cgm              -
```

## Notes
- **OpenCode agents are copies.** OpenCode V2 drops agent files with the V1 `tools:` list (tested 2026-11-09), so `sync-om.sh` writes a copy with only `description` + `mode: subagent` + the body.
- **`~/.pi/agent/AGENTS.md` is the owner's own file.** om never touches it.
- **DSH `~/.dsh/AGENTS.md`** holds a hand-made condensed copy of the rules; update it by hand when `rules/AGENTS.md` changes.
- The old `~/Desktop/_CG-Gov/cgm/` folder is left in place; delete it yourself once om works.
- Reload after a sync: OpenCode `opencode reload`; pi `/reload`; Antigravity restart; DSH reloads by itself.
- Claude Code and Codex are not targets (removed tools).
