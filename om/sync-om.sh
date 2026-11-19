#!/usr/bin/env bash
# sync-om.sh: thin wrapper around `python3 engine/oway sync`.
# Preserves OM_HOME, OM_TOOLS, OM_OWAY_SKILLS, OM_OWAY_AGENTS and all sync flags.
set -euo pipefail

REPO="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
exec python3 "$REPO/engine/oway" sync "$@"
