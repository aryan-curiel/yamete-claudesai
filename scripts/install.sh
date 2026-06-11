#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/aryan-curiel/yamete-claudesai.git"
CLONE_DIR="${TMPDIR:-/tmp}/yamete-claudesai-install"

echo "Cloning yamete-claudesai..."
rm -rf "$CLONE_DIR"
git clone --depth 1 "$REPO_URL" "$CLONE_DIR"

echo "Installing dependencies..."
cd "$CLONE_DIR"
uv sync

echo "Applying default selections..."
uv run main.py apply scripts/default-selections.json

echo ""
echo "  ／ヽ"
echo " (● ●)  Your audio hooks are locked in, senpai~"
echo "  > ♪ <"
echo ""
echo "   You're Welcome! (´｡• ᵕ •｡\`) ♡"
echo ""
