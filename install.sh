#!/usr/bin/env bash
#
# Install / sync the Rami Levy shopping skill from the canonical source
# folder (./skill) into every agent's skills directory.
#
# The skill is copied as a REAL directory (not a symlink): the Claude Code
# skill loader does not pick up symlinked skill folders.
#
# Run this after editing anything under ./skill to re-sync the installs.
#
#   bash install.sh
#
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/skill"
NAME="rami-levi-shopping-cart"

# Destinations: Claude Code (WSL) + cross-agent shared skills dir.
DESTS=(
  "$HOME/.claude/skills/$NAME"
  "$HOME/.agents/skills/$NAME"
)

for dest in "${DESTS[@]}"; do
  rm -rf "$dest"                 # also clears any old symlink at this path
  mkdir -p "$dest"
  cp -r "$SRC/." "$dest/"
  rm -rf "$dest/__pycache__"
  echo "installed -> $dest"
done

echo "Done. Restart the WSL 'claude' session (or run /reload-skills) to load it."
