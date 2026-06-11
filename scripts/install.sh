#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing dependencies..."
cd "$SCRIPT_DIR/.."
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
