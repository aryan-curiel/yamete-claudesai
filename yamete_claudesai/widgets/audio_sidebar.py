from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Label, ListItem, ListView


class AudioListItem(ListItem):
    """A list item that carries the audio filename."""

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename

    def compose(self) -> ComposeResult:
        yield Label(self.filename)


class AudioSidebar(Vertical):
    """
    Left sidebar: search input + scrollable file list.
    Emits ListView.Selected (item is AudioListItem) when user presses Enter.
    """

    DEFAULT_CSS = """
    AudioSidebar {
        width: 30;
        height: 1fr;
        border: round $primary-darken-2;
    }
    AudioSidebar Input  { width: 1fr; }
    AudioSidebar ListView { width: 1fr; height: 1fr; }
    """

    _EXTENSIONS = {".mp3", ".wav", ".aiff", ".m4a", ".ogg", ".flac"}

    def __init__(self, audio_dir: Path) -> None:
        super().__init__()
        self._audio_dir = audio_dir
        self._all_files: list[str] = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search-input")
        yield ListView(id="audio-list")

    def on_mount(self) -> None:
        self._reload_files()

    def _reload_files(self) -> None:
        if self._audio_dir.exists():
            self._all_files = sorted(
                p.name for p in self._audio_dir.iterdir()
                if p.suffix.lower() in self._EXTENSIONS
            )
        else:
            self._all_files = []
        self._apply_filter("")

    def _apply_filter(self, query: str) -> None:
        lv = self.query_one("#audio-list", ListView)
        lv.clear()
        q = query.lower()
        for name in self._all_files:
            if q in name.lower():
                lv.append(AudioListItem(name))

    def on_input_changed(self, event: Input.Changed) -> None:
        self._apply_filter(event.value)
