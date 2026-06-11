from __future__ import annotations

import json
from pathlib import Path

_DEFAULT_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"


def backup_settings(path: Path | None = None) -> Path | None:
    p = path or _DEFAULT_SETTINGS_PATH
    if not p.exists():
        return None
    backup = p.with_suffix(".json.bak")
    backup.write_text(p.read_text())
    return backup


def read_settings(path: Path | None = None) -> dict:
    p = path or _DEFAULT_SETTINGS_PATH
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _is_our_command(cmd: str) -> bool:
    return cmd.startswith("afplay ") or (
        cmd.startswith("bash -c") and "afplay" in cmd and "date" in cmd
    )


def _is_all_afplay_entry(entry: dict) -> bool:
    hooks = entry.get("hooks")
    return (
        isinstance(hooks, list)
        and bool(hooks)
        and all(isinstance(h, dict) and _is_our_command(h.get("command", "")) for h in hooks)
    )


def write_audio_assignments(
    assignments: dict[str, list[str]],
    audio_dir: Path,
    path: Path | None = None,
) -> None:
    """
    Write afplay entries for each hook in assignments into settings.json.
    Removes all existing all-afplay entries, preserves all other entries.
    Single file: plain afplay command. Multiple files: bash picks one via date +%s mod N.
    """
    p = path or _DEFAULT_SETTINGS_PATH
    backup_settings(path=p)
    settings = read_settings(path=p)
    hooks_section: dict[str, list] = settings.setdefault("hooks", {})

    # Strip our old entries from every existing hook
    for hook_name in list(hooks_section.keys()):
        hooks_section[hook_name] = [
            e for e in hooks_section[hook_name] if not _is_all_afplay_entry(e)
        ]

    # Add new entries — one per hook
    for hook_name, filenames in assignments.items():
        hook_list = hooks_section.setdefault(hook_name, [])
        if len(filenames) == 1:
            cmd = f"afplay {audio_dir / filenames[0]}"
        else:
            paths_arr = " ".join(f'"{audio_dir / f}"' for f in filenames)
            inner = f'f=({paths_arr}); afplay "${{f[$(($(date +%s) % ${{#f[@]}}))]}}"'
            cmd = f"bash -c '{inner}'"
        hook_list.append({
            "matcher": "",
            "hooks": [{"type": "command", "command": cmd}],
        })

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(settings, indent=2))
