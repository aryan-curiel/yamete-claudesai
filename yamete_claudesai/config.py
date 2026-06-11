from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

_DEFAULT_CONFIG_DIR = Path.home() / ".config" / "yamete-kudasai"


@dataclass
class AppConfig:
    audio_dir: Path
    assignments: dict[str, list[str]] = field(default_factory=dict)


def load_config(config_dir: Path | None = None) -> AppConfig:
    """Load config from config_dir/config.json, returning defaults if missing."""
    if config_dir is None:
        config_dir = _DEFAULT_CONFIG_DIR
    config_path = config_dir / "config.json"
    if not config_path.exists():
        return AppConfig(audio_dir=config_dir / "audio")
    raw = json.loads(config_path.read_text())
    return AppConfig(
        audio_dir=Path(raw["audio_dir"]),
        assignments=raw.get("assignments", {}),
    )


def save_config(cfg: AppConfig, config_dir: Path | None = None) -> None:
    """Write config to config_dir/config.json, creating the directory if needed."""
    if config_dir is None:
        config_dir = _DEFAULT_CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "config.json").write_text(json.dumps({
        "audio_dir": str(cfg.audio_dir),
        "assignments": cfg.assignments,
    }, indent=2))
