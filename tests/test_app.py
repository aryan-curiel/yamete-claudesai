"""
Integration tests using Textual's Pilot.
All tests use tmp_path to avoid touching real user files.
"""
import json
from pathlib import Path

import pytest

from yamete_claudesai.app import YameteApp
from yamete_claudesai.state import AudioEntry, AudioStatus


def _seed(tmp_path: Path, assignments: dict | None = None) -> tuple[Path, Path, Path]:
    """Create audio dir with two files + config. Returns (audio_dir, config_dir, settings_path)."""
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    (audio_dir / "ding.mp3").write_text("")
    (audio_dir / "boop.wav").write_text("")
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps({
        "audio_dir": str(audio_dir),
        "assignments": assignments or {},
    }))
    return audio_dir, tmp_path, tmp_path / "settings.json"


@pytest.mark.asyncio
async def test_sidebar_shows_audio_files(tmp_path):
    _seed(tmp_path)
    app = YameteApp(config_dir=tmp_path, settings_path=tmp_path / "settings.json")
    async with app.run_test(headless=True) as pilot:
        await pilot.pause()
        from yamete_claudesai.widgets.audio_sidebar import AudioListItem
        names = [i.filename for i in app.query(AudioListItem)]
        assert "ding.mp3" in names
        assert "boop.wav" in names


@pytest.mark.asyncio
async def test_modal_cancel_does_not_change_state(tmp_path):
    _seed(tmp_path)
    app = YameteApp(config_dir=tmp_path, settings_path=tmp_path / "settings.json")
    async with app.run_test(headless=True) as pilot:
        await pilot.pause()
        await pilot.press("tab")
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert app._state.assignments == {}


@pytest.mark.asyncio
async def test_confirm_writes_settings_json(tmp_path):
    audio_dir, config_dir, settings_path = _seed(tmp_path, {"Stop": ["ding.mp3"]})
    app = YameteApp(config_dir=config_dir, settings_path=settings_path)
    async with app.run_test(headless=True) as pilot:
        await pilot.pause()
        await pilot.click("#btn-confirm-all")
        await pilot.pause()
    raw = json.loads(settings_path.read_text())
    commands = [
        hh["command"]
        for h in raw["hooks"].get("Stop", [])
        for hh in h.get("hooks", [])
        if isinstance(hh, dict)
    ]
    assert any("ding.mp3" in cmd for cmd in commands)


@pytest.mark.asyncio
async def test_added_entry_renders_with_added_class(tmp_path):
    _seed(tmp_path)
    app = YameteApp(config_dir=tmp_path, settings_path=tmp_path / "settings.json")
    app._state.assignments["Stop"] = [AudioEntry("ding.mp3", AudioStatus.ADDED)]
    async with app.run_test(headless=True) as pilot:
        await pilot.pause()
        app._refresh_right_panel()
        await pilot.pause()
        from yamete_claudesai.widgets.hook_box import AudioLabel
        added = [lbl for lbl in app.query(AudioLabel) if "added" in lbl.classes]
        assert len(added) >= 1
