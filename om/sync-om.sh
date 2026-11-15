#!/usr/bin/env bash
# sync-om.sh: link om into your agent tools, or check that it is.
#
# Usage:
#   ./sync-om.sh --tools pi,opencode,antigravity     apply
#   ./sync-om.sh --check [--tools ...]               check only, exit 1 on drift
#   ./sync-om.sh --dry-run [--tools ...]             print what apply would do
#
# Tools: --tools, else $OM_TOOLS, else the file ~/.config/om/tools.
# Optional files in ~/.config/om/: `extra` (method target source) and `retire` (paths).
# Env for tests: OM_HOME overrides $HOME.
set -euo pipefail

ROOT="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
HOME_DIR="${OM_HOME:-$HOME}"
CONF="$HOME_DIR/.config/om"
MODE=apply
TOOLS="${OM_TOOLS:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) MODE=check ;;
    --dry-run) MODE=dry ;;
    --tools) TOOLS="${2:?--tools needs a list}"; shift ;;
    -h|--help) sed -n 2,11p "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done
[[ -n "$TOOLS" || ! -f "$CONF/tools" ]] || TOOLS="$(grep -v '^#' "$CONF/tools" | tr '\n' ',' )"
[[ -n "$TOOLS" ]] || { echo "No tools chosen. Use --tools pi,opencode,antigravity (see DEPLOYMENTS.md)." >&2; exit 2; }

BACKUP_DIR="$HOME_DIR/.om-deploy-backups/$(date +%Y%m%d-%H%M%S)"
FAIL=0
n=0

expand() { local p="${1/#\~/$HOME_DIR}"; echo "${p//\$HOME/$HOME_DIR}"; }

backup() { # move a path out of the way, keeping it
  mkdir -p "$BACKUP_DIR"
  local dest="$BACKUP_DIR/$(echo "$1" | sed "s|^$HOME_DIR/||; s|/|__|g")"
  mv "$1" "$dest"
  echo "  backup: $1 -> $dest"
}

opencode_agent() { # OpenCode V2 agent file: description + mode, same body
  python3 - "$1" <<'PY'
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
m = re.match(r"---\n(.*?)\n---\n?(.*)", t, re.S)
if not m:
    sys.exit("no frontmatter in " + sys.argv[1])
fm, body = m.groups()
d = re.search(r"^description:.*(?:\n[ \t]+.*)*", fm, re.M)
if not d:
    sys.exit("no description in " + sys.argv[1])
sys.stdout.write("---\n" + d.group(0) + "\nmode: subagent\n---\n" + body)
PY
}

act() { # $1 = message; runs the rest only in apply mode
  local msg="$1"; shift
  if [[ "$MODE" == dry ]]; then echo "would $msg"; else "$@"; echo "$msg"; fi
}
link() { mkdir -p "$(dirname "$1")"; [[ -e "$1" || -L "$1" ]] && backup "$1"; ln -s "$2" "$1"; }
copy() { mkdir -p "$(dirname "$1")"; [[ -e "$1" || -L "$1" ]] && backup "$1"; printf '%s' "$2" > "$1"; }

target_row() { # $1 tool, $2 method, $3 target, $4 source (relative to om/, may be ../skills/...)
  local tool="$1" method="$2" target src
  target="$(expand "$3")"; src="$ROOT/$4"; n=$((n+1))
  [[ -e "$src" ]] || { echo "FAIL [$tool] source missing: $src"; FAIL=1; return; }
  case "$method" in
    symlink)
      if [[ -L "$target" && "$(readlink -f "$target")" == "$(readlink -f "$src")" ]]; then
        echo "ok   [$tool] $target"
      elif [[ "$MODE" == check ]]; then echo "DRIFT [$tool] $target (want link -> $src)"; FAIL=1
      else act "link [$tool] $target -> $src" link "$target" "$src"; fi ;;
    opencode-agent)
      local want; want="$(opencode_agent "$src")"
      if [[ -f "$target" && ! -L "$target" && "$(cat "$target")" == "$want" ]]; then
        echo "ok   [$tool] $target (copy)"
      elif [[ "$MODE" == check ]]; then echo "DRIFT [$tool] $target (copy differs from $4)"; FAIL=1
      else act "copy [$tool] $target <- $4" copy "$target" "$want"; fi ;;
    *) echo "FAIL unknown method '$method' for $target"; FAIL=1 ;;
  esac
}

skill_src() { [[ "$1" == cgspec-ui-ux ]] && echo "../skills/$1" || echo "skills/$1"; }

tool_rows() { # built-in targets of one tool
  local t="$1" s a
  case "$t" in
    pi)
      for s in om-plan cgspec-ui-ux om-assist; do target_row pi symlink "~/.pi/agent/skills/$s" "$(skill_src $s)"; done
      for a in om-caps om-review om-assist; do target_row pi symlink "~/.pi/agent/prompts/$a.md" "agents/$a.md"; done
      target_row pi symlink "~/.pi/agent/APPEND_SYSTEM.md" rules/AGENTS.md ;;
    opencode)
      for s in om-plan cgspec-ui-ux om-assist; do target_row opencode symlink "~/.config/opencode/skills/$s" "$(skill_src $s)"; done
      for a in om-caps om-review om-assist; do target_row opencode opencode-agent "~/.config/opencode/agents/$a.md" "agents/$a.md"; done
      target_row opencode symlink "~/.config/opencode/AGENTS.md" rules/AGENTS.md ;;
    antigravity)
      target_row antigravity symlink "~/.gemini/config/plugins/om" .
      target_row antigravity symlink "~/.gemini/config/skills/cgspec-ui-ux" "../skills/cgspec-ui-ux" ;;
    oway)
      target_row oway symlink "~/.local/bin/oway" bin/oway ;;
    *) echo "FAIL unknown tool '$t' (built in: pi, opencode, antigravity, oway)"; FAIL=1 ;;
  esac
}

echo "root=$ROOT  tools=${TOOLS%,}  mode=$MODE"
IFS=',' read -ra LIST <<< "$TOOLS"
for t in "${LIST[@]}"; do [[ -z "$t" ]] || tool_rows "$t"; done

if [[ -f "$CONF/extra" ]]; then
  while read -r method target source; do
    [[ -z "${method:-}" || "$method" == \#* ]] && continue
    target_row extra "$method" "$target" "$source"
  done < "$CONF/extra"
fi
if [[ -f "$CONF/retire" ]]; then
  while read -r path; do
    [[ -z "$path" || "$path" == \#* ]] && continue
    path="$(expand "$path")"; n=$((n+1))
    if [[ ! -e "$path" && ! -L "$path" ]]; then echo "ok   retired $path"
    elif [[ "$MODE" == check ]]; then echo "DRIFT old path still there: $path"; FAIL=1
    else act "retire $path" backup "$path"; fi
  done < "$CONF/retire"
fi

[[ $FAIL -eq 0 ]] || { echo "RESULT: DRIFT/FAIL ($n targets)"; exit 1; }
echo "RESULT: OK ($n targets)"
