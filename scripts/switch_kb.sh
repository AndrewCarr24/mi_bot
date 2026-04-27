#!/usr/bin/env bash
# Repoint `data/` (the symlink the code reads from) at one of the KB homes.
#
# Usage:
#   ./scripts/switch_kb.sh mi             # production MI corpus (default)
#   ./scripts/switch_kb.sh financebench   # regression eval corpus
#
# Why a symlink: dsrag_kb resolves the KB path from `data/dsrag_store/`.
# Switching corpora by symlink-repoint avoids `mv data data.bak` patterns
# that on macOS can produce conflict-renamed siblings (`data 2/`, etc.)
# when Finder/Spotlight briefly hold the path.
set -euo pipefail

target="${1:-mi}"
case "$target" in
  mi)            target_dir="data.mi" ;;
  financebench)  target_dir="data.financebench" ;;
  *)
    echo "Usage: $0 {mi|financebench}" >&2
    exit 1
    ;;
esac

# Resolve to repo root from this script's location
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [ ! -d "$target_dir" ]; then
  echo "Error: $target_dir does not exist in $repo_root" >&2
  exit 2
fi

# Replace the existing data symlink/dir atomically. `ln -sfn` swaps the
# target without conflict-renaming when `data` is a symlink.
ln -sfn "$target_dir" data
echo "data → $target_dir ($(ls "$target_dir/parsed" 2>/dev/null | wc -l | xargs) markdowns, $(du -sh "$target_dir/dsrag_store" 2>/dev/null | cut -f1) store)"
