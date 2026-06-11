import json
from pathlib import Path

from yamete_claudesai.settings import read_settings, write_audio_assignments


def test_read_settings_returns_empty_when_missing(tmp_path):
    assert read_settings(path=tmp_path / "settings.json") == {}


def test_read_settings_parses_existing(tmp_path):
    p = tmp_path / "settings.json"
    data = {"hooks": {"Stop": []}}
    p.write_text(json.dumps(data))
    assert read_settings(path=p) == data


def test_write_adds_afplay_commands(tmp_path):
    p = tmp_path / "settings.json"
    write_audio_assignments({"Stop": ["ding.mp3"]}, audio_dir=Path("/audio"), path=p)
    commands = _all_commands(p, "Stop")
    assert "afplay /audio/ding.mp3" in commands


def test_write_preserves_non_afplay_entries(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"hooks": {"Stop": [
        {"matcher": "", "hooks": [{"type": "command", "command": "osascript -e 'beep'"}]}
    ]}}))
    write_audio_assignments({"Stop": ["ding.mp3"]}, audio_dir=Path("/audio"), path=p)
    raw = json.loads(p.read_text())
    stop = raw["hooks"]["Stop"]
    non_afplay = [h for h in stop if not _is_all_afplay(h)]
    assert len(non_afplay) == 1
    assert non_afplay[0]["hooks"][0]["command"] == "osascript -e 'beep'"


def test_write_removes_old_afplay_before_adding(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"hooks": {"Stop": [
        {"matcher": "", "hooks": [{"type": "command", "command": "afplay /old/sound.mp3"}]}
    ]}}))
    write_audio_assignments({"Stop": ["new.mp3"]}, audio_dir=Path("/audio"), path=p)
    commands = _all_commands(p, "Stop")
    assert "afplay /old/sound.mp3" not in commands
    assert "afplay /audio/new.mp3" in commands


def test_write_multiple_files_same_hook(tmp_path):
    p = tmp_path / "settings.json"
    write_audio_assignments({"Stop": ["a.mp3", "b.mp3"]}, audio_dir=Path("/audio"), path=p)
    commands = _all_commands(p, "Stop")
    assert len(commands) == 1
    cmd = commands[0]
    assert "bash -c" in cmd
    assert "date +%s" in cmd
    assert "/audio/a.mp3" in cmd
    assert "/audio/b.mp3" in cmd


def test_write_empty_assignments_clears_afplay(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"hooks": {"Stop": [
        {"matcher": "", "hooks": [{"type": "command", "command": "afplay /audio/old.mp3"}]}
    ]}}))
    write_audio_assignments({}, audio_dir=Path("/audio"), path=p)
    commands = _all_commands(p, "Stop")
    assert "afplay /audio/old.mp3" not in commands


# ---------- helpers ----------

def _all_commands(p: Path, hook: str) -> list[str]:
    raw = json.loads(p.read_text())
    return [
        hh["command"]
        for h in raw.get("hooks", {}).get(hook, [])
        for hh in h.get("hooks", [])
        if isinstance(hh, dict) and "command" in hh
    ]


def _is_all_afplay(entry: dict) -> bool:
    hooks = entry.get("hooks", [])
    return bool(hooks) and all(
        isinstance(h, dict) and h.get("command", "").startswith("afplay ")
        for h in hooks
    )
