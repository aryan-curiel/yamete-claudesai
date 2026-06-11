import json
from pathlib import Path

from yamete_claudesai.config import AppConfig, load_config, save_config


def test_load_config_returns_defaults_when_missing(tmp_path):
    cfg = load_config(config_dir=tmp_path)
    assert cfg.audio_dir == tmp_path / "audio"
    assert cfg.assignments == {}


def test_load_config_reads_existing_file(tmp_path):
    data = {"audio_dir": str(tmp_path / "sounds"), "assignments": {"Stop": ["beep.mp3"]}}
    (tmp_path / "config.json").write_text(json.dumps(data))
    cfg = load_config(config_dir=tmp_path)
    assert cfg.audio_dir == Path(data["audio_dir"])
    assert cfg.assignments == {"Stop": ["beep.mp3"]}


def test_save_config_writes_json(tmp_path):
    cfg = AppConfig(audio_dir=tmp_path / "audio", assignments={"Stop": ["ding.wav"]})
    save_config(cfg, config_dir=tmp_path)
    raw = json.loads((tmp_path / "config.json").read_text())
    assert raw["audio_dir"] == str(tmp_path / "audio")
    assert raw["assignments"] == {"Stop": ["ding.wav"]}


def test_roundtrip(tmp_path):
    cfg = AppConfig(audio_dir=tmp_path / "audio", assignments={"PostToolUse": ["ping.aiff"]})
    save_config(cfg, config_dir=tmp_path)
    loaded = load_config(config_dir=tmp_path)
    assert loaded.audio_dir == cfg.audio_dir
    assert loaded.assignments == cfg.assignments
