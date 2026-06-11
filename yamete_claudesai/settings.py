from __future__ import annotations

import json
from pathlib import Path

_DEFAULT_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"


def read_settings(path: Path | None = None) -> dict:
    p = path or _DEFAULT_SETTINGS_PATH
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _is_all_afplay_entry(entry: dict) -> bool:
    hooks = entry.get("hooks")
    return (
        isinstance(hooks, list)
        and bool(hooks)
        and all(
            isinstance(h, dict) and h.get("command", "").startswith("afplay ")
            for h in hooks
        )
    )


def write_audio_assignments(
    assignments: dict[str, list[str]],
    audio_dir: Path,
    path: Path | None = None,
) -> None:
    """
    Write afplay entries for each hook in assignments into settings.json.
    Removes all existing all-afplay entries, preserves all other entries.
    One afplay entry per file (sequential playback).
    """
    p = path or _DEFAULT_SETTINGS_PATH
    settings = read_settings(path=p)
    hooks_section: dict[str, list] = settings.setdefault("hooks", {})

    # Strip our old afplay entries from every existing hook
    for hook_name in list(hooks_section.keys()):
        hooks_section[hook_name] = [
            e for e in hooks_section[hook_name] if not _is_all_afplay_entry(e)
        ]

    # Add new afplay entries
    for hook_name, filenames in assignments.items():
        hook_list = hooks_section.setdefault(hook_name, [])
        for filename in filenames:
            hook_list.append({
                "matcher": "",
                "hooks": [{"type": "command", "command": f"afplay {audio_dir / filename}"}],
            })

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(settings, indent=2))
