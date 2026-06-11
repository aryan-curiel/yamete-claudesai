# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_state.py -v

# Run a single test by name
uv run pytest tests/test_state.py::test_commit_removes_removed_and_resets_added -v

# Launch the TUI
uv run python main.py

# Apply an assignments JSON file without opening the TUI
uv run python main.py apply path/to/assignments.json

# Install dependencies (including dev)
uv sync --group dev

# Hot-reload TUI during development (requires textual-dev)
uv run textual run --dev main.py
```

## Architecture

This is a Textual TUI app that maps audio files to Claude Code lifecycle hooks and writes `afplay` commands into `~/.claude/settings.json`.

### Data flow

1. On startup, `YameteApp` calls `load_config()` to read `~/.config/yamete-kudasai/config.json`, which stores the audio directory path and current hook→filename assignments.
2. Assignments are loaded into `AppState`, which tracks each `AudioEntry` with a status (`NORMAL`, `ADDED`, `REMOVED`) for diff display.
3. When the user presses Enter/Space on a file in `AudioSidebar`, the app calls `push_screen(AssignModal(...), callback)`. The modal dismisses with a `set[str]` of selected hook names (or `None` on cancel).
4. The callback calls `state.set_hook_assignments(hook, filenames)` for each hook, which diffs against existing entries and marks statuses.
5. On Confirm, `_commit()` calls `write_audio_assignments()` to update `~/.claude/settings.json`, then `save_config()` to persist the new assignments, then `state.commit()` to reset diff state.

### Key modules

- **`state.py`** — `AppState` is the single source of truth. `set_hook_assignments(hook, filenames_set)` diffs against existing entries rather than replacing them, preserving NORMAL/ADDED/REMOVED statuses. `merge_assignments()` unions incoming filenames with existing ones (used by import and the `apply` CLI).
- **`settings.py`** — `write_audio_assignments()` identifies "our" entries in `settings.json` by checking if all hooks in an entry are `afplay` commands (`_is_all_afplay_entry`). It strips those and rewrites them, leaving all other entries (e.g. `osascript` notifications) untouched.
- **`hooks.py`** — Defines `ALL_HOOKS` (every known Claude Code hook) and `IMPORTANT_HOOKS` (the subset flagged `important=True`). `HOOKS` is an alias for `ALL_HOOKS`. `AssignModal` displays `IMPORTANT_HOOKS` by default; `AllHooksModal` shows the full list.
- **`widgets/assign_modal.py`** — `AssignModal(ModalScreen[set[str] | None])` uses Textual's typed `dismiss(result)` + `push_screen(modal, callback)` pattern, not message events.
- **`widgets/audio_sidebar.py`** — `AudioListItem` is a `ListItem` subclass that carries `.filename`; the app identifies sidebar selections by `isinstance(event.item, AudioListItem)`.
- **`widgets/add_audio_modal.py`** — `AddAudioModal` is a file/folder picker reused for both "Add Audio" (copying files) and "Import" (picking a JSON assignments file).
- **`widgets/hook_box.py`** — Renders a single hook's current assignments in the right panel with ADDED/REMOVED diff coloring.
- **`main.py`** — Entry point. Delegates to `run()` (TUI) or `_apply(path)` (headless import) based on `sys.argv`.

### TUI keybindings

| Key | Action |
|-----|--------|
| Enter / Space | Assign selected audio file to hooks |
| `a` | Add audio file(s) or folder |
| `d` | Delete selected audio file |
| `p` | Preview (play) selected audio file via `afplay` |
| `e` | Export current assignments to `~/.config/yamete-kudasai/selections.json` |
| `i` | Import assignments from a JSON file (merged, non-destructive) |
| `q` | Quit |

### Config locations

- Audio files: `~/.config/yamete-kudasai/audio/` (supported: `.mp3 .wav .aiff .m4a .ogg .flac`)
- App config: `~/.config/yamete-kudasai/config.json`
- Claude Code hooks: `~/.claude/settings.json`
- Default export path: `~/.config/yamete-kudasai/selections.json`

### Testability

`YameteApp.__init__` accepts `config_dir` and `settings_path` keyword arguments to redirect all file I/O to temp paths — tests use these instead of touching real user config. `pytest-asyncio` is configured with `asyncio_mode = "auto"` (set in `pyproject.toml`), so async test functions need no decorator.
