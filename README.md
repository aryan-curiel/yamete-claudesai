# yamete-claudesai

A Textual TUI for mapping audio files to [Claude Code](https://claude.ai/code) lifecycle hooks. Every time Claude starts thinking, stops, asks a question, or errors out — you hear it.

![Python](https://img.shields.io/badge/python-3.13+-blue) ![Textual](https://img.shields.io/badge/textual-TUI-purple) ![macOS](https://img.shields.io/badge/macOS-only-lightgrey)

> **macOS only** — uses `afplay` to play sounds.

## What it does

Claude Code supports [lifecycle hooks](https://docs.anthropic.com/en/docs/claude-code/hooks) that run shell commands at points like `PreToolUse`, `PostToolUse`, `Stop`, `Notification`, and more. This app writes `afplay <file>` commands into `~/.claude/settings.json` for whichever hooks you choose, so Claude Code triggers your audio files automatically.

## Demo

```
╔══════════════════════════════════════════════════╗
║  yamete-claudesai                    [Confirm] ║
╠══════════════╦═══════════════════════════════════╣
║ Audio Files  ║ Hook Assignments                  ║
║──────────────║───────────────────────────────────║
║ arigato.mp3  ║ Stop          → arigato.mp3       ║
║ anime-nani   ║ Notification  → anime-nani.mp3    ║
║ oh-yeah.mp3  ║ PreToolUse    → (none)            ║
║ what.mp3   ↵ ║ PostToolUse   → (none)            ║
║ ...          ║ ...                               ║
╚══════════════╩═══════════════════════════════════╝
```

## Included sounds

The `sounds/` directory ships with a starter pack:

| File | Description |
|------|-------------|
| `yamate-kudesai.mp3` | "Yamete kudasai!" |
| `arigato.mp3` | Short "arigatou" |
| `arigato-long.mp3` | Longer "arigatou gozaimasu" |
| `anime-nani.mp3` | "Nani?!" |
| `anime-wow.wav` | Anime wow reaction |
| `anime-anate.wav` | "Anata…" |
| `anime-etto.wav` | "Etto…" |
| `anime-pasu.wav` | "Pasu!" |
| `oh-yeah.mp3` | Oh yeah |
| `what.mp3` | What? |
| `what-the-hell.mp3` | What the hell |
| `way-way-way.mp3` | Way way way |

## Requirements

- macOS (uses `afplay`)
- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Claude Code

## Setup

```bash
git clone https://github.com/aryancuriel/yamete-claudesai
cd yamete-claudesai
uv sync
```

Copy the included sounds to the app's audio directory (or point it at any folder of your own):

```bash
mkdir -p ~/.config/yamete-kudasai/audio
cp sounds/* ~/.config/yamete-kudasai/audio/
```

## Usage

```bash
uv run python main.py
```

- **Arrow keys / mouse** — navigate the audio file list
- **Enter** — open the hook assignment modal for the selected file
- **Space** — toggle a hook assignment in the modal
- **Confirm** — write assignments to `~/.claude/settings.json`

The app only touches `afplay` entries it owns — any other hooks you have configured (e.g. `osascript` notifications) are left untouched.

### Importing assignments

You can apply a saved assignments file without opening the TUI:

```bash
uv run python main.py apply assignments.json
```

The JSON file must have an `assignments` key mapping hook names to lists of filenames:

```json
{
  "assignments": {
    "Stop": ["arigato.mp3"],
    "Notification": ["anime-nani.mp3"]
  }
}
```

Incoming entries are **merged** into the existing config — nothing already assigned is removed.

## How it works

On **Confirm**, `write_audio_assignments()` in `settings.py` scans `~/.claude/settings.json`, removes any existing entries where every command is an `afplay` call (those are "ours"), and rewrites them with the current assignments. The app config (audio dir + assignments) is persisted separately in `~/.config/yamete-kudasai/config.json`.

## Running tests

```bash
uv run pytest
```
