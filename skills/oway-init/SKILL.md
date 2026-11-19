---
name: oway-init
description: Install, verify, update, or uninstall the current Oway package and tool adapters in a project. For an existing unadopted project, use oway-adopt first.
---

# Initialize Oway (`oway-init`)

## 1. Oway v0.4 Platform & Project Setup (`_oway/`)

Oway is installed once on the owner's Platform (`~/.oway/` and the 5 AI harnesses via `oway sync`) and is **never copied into a consumer project** (`docs/oway/rules.md`: *"No copy of the tool"*):

1. **Sync the Platform & Harnesses (Once per Machine)**:
   ```bash
   oway platform init
   oway sync --tools pi,opencode,claude,codex,antigravity,oway --oway-skills --oway-agents
   oway sync --tools pi,opencode,claude,codex,antigravity,oway --oway-skills --oway-agents --check
   ```
2. **Owner Profile (`OwayHelpers`)**:
   - `OwayHelpers` checks `~/.oway/profile.md`. If missing (or `approved: no`), it interviews the owner once via [interview-me](../interview-me/SKILL.md) (coding rules, tools, accounts) and writes `~/.oway/profile.md`.
3. **Initialize a New Project (`oway setup`)**:
   - For an existing project with code or CGSpec v0.3 files, use [oway-adopt](../oway-adopt/SKILL.md) (`oway takeover --from cgspec-0.3`) first.
   - For a new project, run:
     ```bash
     oway setup --language <en|fr|...> --builder DevBackend [--builder DevFrontend ...] [--no-uix] [--claude-hook]
     oway install-hook --host claude   # or: oway install-hook --host pi
     oway headers
     oway index
     oway doctor
     ```
   - This creates `_oway/config.json`, `_oway/project.md` (starting with `## 1. The goal`, `## 2. What you get`, `## 3. The proof you will have`), `_oway/agents/README.md`, `_oway/LEDGER.md`, and `_oway/INDEX.md`. Work starts only when `oway doctor` exits `0`.

---

## 2. Legacy v0.3 Package Installer (`engine/install.py`)

Read only what the current step needs, once per session: the [agent contract](../../engine/CONTRACT.md) and the installed `docs/_cgspec/project.json` if present. This skill manages the package; project discovery and content migration belong to `oway-adopt`.

For a new project using the legacy v0.3 layout, identify its profile (`website`, `web-workspace`, `mobile`, `cli`, `headless`, `small`), topology (`single`, `monorepo`, `large-monorepo`, `polyrepo-governance`, `polyrepo-member`), and tools actually present. Use the plugin copy of `engine/install.py` and its `--help` to confirm syntax. The current install command is `python3 engine/install.py install --root <path> --profile <profile> --topology <topology> [--tools <comma-separated-tools>]`. Install only into the authorized repository. The installer owns generated files and has an uninstall manifest; inspect conflicts before acting on a nonempty tree.

For an installed 0.2.x or newer project, run `python3 engine/install.py verify --root <path>` before `upgrade` or `uninstall`. Run `upgrade` from the **new plugin copy**; it refreshes the vendored engine, Claude and Antigravity hooks, and Antigravity workspace skills, archiving replaced skill bytes. `uninstall` removes only unchanged owned files. Check `docs/_cgspec/01-engine/` and adapter wiring after the action, then run `python3 docs/_cgspec/01-engine/doctor.py --root <path>`. Record any adapter or CI capability that could not be verified. GitHub CI trust wiring, branch protection and remote approval settings need owner review; file creation alone does not activate them.

An earlier v0.1 layout is an adoption upgrade: route to `oway-adopt` for a path map, rollback and content checks before updating the version marker.
