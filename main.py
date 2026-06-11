import json
import shutil
import sys
from pathlib import Path

from yamete_claudesai.app import run
from yamete_claudesai.config import AppConfig, load_config, save_config
from yamete_claudesai.settings import write_audio_assignments
from yamete_claudesai.state import AppState

_AUDIO_EXTENSIONS = {".mp3", ".wav", ".aiff", ".m4a", ".ogg", ".flac"}


def _bootstrap() -> None:
    config_dir = Path.home() / ".config" / "yamete-kudasai"
    if config_dir.exists():
        return
    audio_dir = config_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    sounds_src = Path(__file__).parent / "sounds"
    if sounds_src.is_dir():
        for f in sounds_src.iterdir():
            if f.suffix.lower() in _AUDIO_EXTENSIONS:
                shutil.copy2(f, audio_dir / f.name)


def _apply(json_path: Path) -> None:
    if not json_path.exists():
        print(f"error: file not found: {json_path}", file=sys.stderr)
        sys.exit(1)
    try:
        raw = json.loads(json_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        print(f"error: could not read {json_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    incoming: dict[str, list[str]] = raw.get("assignments", {})
    if not isinstance(incoming, dict):
        print("error: unexpected format — missing 'assignments' dict", file=sys.stderr)
        sys.exit(1)

    cfg = load_config()
    state = AppState.from_assignments(cfg.assignments)
    state.merge_assignments(incoming)
    merged = state.to_assignments_dict()

    write_audio_assignments(assignments=merged, audio_dir=cfg.audio_dir)
    save_config(AppConfig(audio_dir=cfg.audio_dir, assignments=merged))

    total = sum(len(v) for v in incoming.values())
    print(f"Applied {total} assignment(s) from '{json_path.name}' → ~/.claude/settings.json")


def main() -> None:
    _bootstrap()
    if len(sys.argv) >= 3 and sys.argv[1] == "apply":
        _apply(Path(sys.argv[2]))
    else:
        run()


if __name__ == "__main__":
    main()
