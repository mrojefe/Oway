#!/usr/bin/env bash
# fetch_catalog.sh: build catalog/ from the two MIT upstream repos, at pinned commits.
# Usage: scripts/fetch_catalog.sh   (needs git and network; replaces catalog/)
# To update: change a SHA below, run it, check `style_hub.py list`, commit the new SHA.
set -euo pipefail
TYPEUI_REPO=https://github.com/bergside/awesome-design-skills
TYPEUI_SHA=f631a09b4fcc0166f2e2c1a8c81906ef680c57e8
HALLMARK_REPO=https://github.com/Nutlope/hallmark
HALLMARK_SHA=04977e15f3dfd6ee4b74c887dac3eb52665d6c92

HERE="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

get() { # $1 repo, $2 sha, $3 dir
  git init -q "$3"
  git -C "$3" fetch -q --depth 1 "$1" "$2"
  git -C "$3" checkout -q FETCH_HEAD
}
get "$TYPEUI_REPO" "$TYPEUI_SHA" "$TMP/typeui"
get "$HALLMARK_REPO" "$HALLMARK_SHA" "$TMP/hallmark"

NEW="$TMP/catalog"
mkdir -p "$NEW/typeui-styles" "$NEW/hallmark-themes/references" "$NEW/hallmark-themes/scripts"
for d in "$TMP/typeui/skills"/*/; do cp -r "$d" "$NEW/typeui-styles/"; done
find "$NEW" -name .DS_Store -delete
H="$TMP/hallmark/skills/hallmark"
cp "$H/references/themes/"* "$NEW/hallmark-themes/"
find "$H/references" -maxdepth 1 -name '*.md' -exec cp {} "$NEW/hallmark-themes/references/" \;
cp "$H/scripts/sloplint.mjs" "$H/scripts/theme.mjs" "$NEW/hallmark-themes/scripts/"
printf 'typeui-styles: %s@%s\nhallmark-themes: %s@%s\n' \
  "$TYPEUI_REPO" "$TYPEUI_SHA" "$HALLMARK_REPO" "$HALLMARK_SHA" > "$NEW/SOURCE.txt"

rm -rf "$HERE/catalog"; mv "$NEW" "$HERE/catalog"
echo "catalog ready: $(ls -d "$HERE/catalog/typeui-styles"/*/ | wc -l) styles, $(ls "$HERE/catalog/hallmark-themes"/*.md | grep -cv README) themes"
