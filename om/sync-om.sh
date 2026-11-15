#!/usr/bin/env bash
# sync-om.sh: apply or check every om target in DEPLOYMENTS.md for this host (`hostname`).
#
# Usage:
#   ./sync-om.sh            apply: set missing links, regenerate OpenCode agent copies,
#                           retire old CGM paths (backed up first), then report
#   ./sync-om.sh --check    check only, change nothing (exit 1 on any drift)
#   ./sync-om.sh --dry-run  print what apply would do, change nothing
#
# Env: OM_HOST overrides `hostname`; OM_HOME overrides $HOME (both for tests).
set -euo pipefail

ROOT="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
REG="$ROOT/DEPLOYMENTS.md"
HOST="${OM_HOST:-$(hostname)}"
HOME_DIR="${OM_HOME:-$HOME}"
MODE=apply
for a in "$@"; do
  case "$a" in
    --check) MODE=check ;;
    --dry-run) MODE=dry ;;
    -h|--help) sed -n 2,10p "$0"; exit 0 ;;
    *) echo "unknown arg: $a" >&2; exit 2 ;;
  esac
done
BACKUP_DIR="$HOME_DIR/.om-deploy-backups/$(date +%Y%m%d-%H%M%S)"
FAIL=0

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

echo "host=$HOST  root=$ROOT  mode=$MODE"
rows="$(awk '/^```om-targets/{f=1;next} /^```/{f=0} f && $0 !~ /^#/ && NF' "$REG")"
n=0
while read -r host tool method target source; do
  [[ "$host" == "$HOST" ]] || continue
  n=$((n+1))
  target="${target/#\~/$HOME_DIR}"
  case "$method" in
    retire)
      if [[ ! -e "$target" && ! -L "$target" ]]; then echo "ok   [$tool] retired $target"
      elif [[ "$MODE" == check ]]; then echo "DRIFT [$tool] old path still there: $target"; FAIL=1
      else act "retire [$tool] $target" backup "$target"; fi
      continue ;;
  esac
  src="$ROOT/$source"
  [[ -e "$src" ]] || { echo "FAIL [$tool] source missing: $src"; FAIL=1; continue; }
  case "$method" in
    symlink)
      if [[ -L "$target" && "$(readlink -f "$target")" == "$(readlink -f "$src")" ]]; then
        echo "ok   [$tool] $target"
      elif [[ "$MODE" == check ]]; then echo "DRIFT [$tool] $target (want link -> $src)"; FAIL=1
      else act "link [$tool] $target -> $src" link "$target" "$src"; fi ;;
    opencode-agent)
      want="$(opencode_agent "$src")"
      if [[ -f "$target" && ! -L "$target" && "$(cat "$target")" == "$want" ]]; then
        echo "ok   [$tool] $target (copy)"
      elif [[ "$MODE" == check ]]; then echo "DRIFT [$tool] $target (copy differs from $source)"; FAIL=1
      else act "copy [$tool] $target <- $source" copy "$target" "$want"; fi ;;
    *) echo "FAIL unknown method '$method' for $target"; FAIL=1 ;;
  esac
done <<< "$rows"

[[ $n -gt 0 ]] || { echo "no rows for host '$HOST' in DEPLOYMENTS.md"; exit 1; }
[[ $FAIL -eq 0 ]] || { echo "RESULT: DRIFT/FAIL ($n targets)"; exit 1; }
echo "RESULT: OK ($n targets)"
