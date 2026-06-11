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

# Install dependencies (including dev)
uv sync --group dev
```

## Architecture

This is a Textual TUI app that maps audio files to Claude Code lifecycle hooks and writes `afplay` commands into `~/.claude/settings.json`.

### Data flow

1. On startup, `YameteApp` calls `load_config()` to read `~/.config/yamete-kudasai/config.json`, which stores the audio directory path and current hook→filename assignments.
2. Assignments are loaded into `AppState`, which tracks each `AudioEntry` with a status (`NORMAL`, `ADDED`, `REMOVED`) for diff display.
3. When the user presses Enter on a file in `AudioSidebar`, the app calls `push_screen(AssignModal(...), callback)`. The modal dismisses with a `set[str]` of selected hook names (or `None` on cancel).
4. The callback calls `state.set_hook_assignments(hook, filenames)` for each hook, which diffs against existing entries and marks statuses.
5. On Confirm, `_commit()` calls `write_audio_assignments()` to update `~/.claude/settings.json`, then `save_config()` to persist the new assignments, then `state.commit()` to reset diff state.

### Key modules

- **`state.py`** — `AppState` is the single source of truth. `set_hook_assignments(hook, filenames_set)` is the primary mutation method; it diffs against existing entries rather than replacing them, so NORMAL/ADDED/REMOVED statuses are preserved correctly.
- **`settings.py`** — `write_audio_assignments()` identifies "our" entries in `settings.json` by checking if all hooks in an entry are `afplay` commands (`_is_all_afplay_entry`). It strips those and rewrites them, leaving all other entries (e.g. existing `osascript` notifications) untouched.
- **`widgets/assign_modal.py`** — `AssignModal(ModalScreen[set[str] | None])` uses Textual's typed `dismiss(result)` + `push_screen(modal, callback)` pattern, not message events.
- **`widgets/audio_sidebar.py`** — `AudioListItem` is a `ListItem` subclass that carries `.filename`; the app identifies sidebar selections by `isinstance(event.item, AudioListItem)`.

### Config location

- Audio files: `~/.config/yamete-kudasai/audio/` (supported: `.mp3 .wav .aiff .m4a .ogg .flac`)
- App config: `~/.config/yamete-kudasai/config.json`
- Claude Code hooks: `~/.claude/settings.json`
