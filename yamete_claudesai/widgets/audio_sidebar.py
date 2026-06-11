from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button, Input, Label, ListItem, ListView

AUDIO_EXTENSIONS: frozenset[str] = frozenset(
    {".mp3", ".wav", ".aiff", ".m4a", ".ogg", ".flac"}
)


class AudioListItem(ListItem):
    """A list item that carries the audio filename."""

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename

    def compose(self) -> ComposeResult:
        yield Label(self.filename)


class AudioSidebar(Vertical):
    """
    Left sidebar: add button + search input + scrollable file list.
    Emits ListView.Selected (item is AudioListItem) when user presses Enter.
    Emits AudioSidebar.AddAudioRequested when the Add button is pressed.
    """

    DEFAULT_CSS = """
    AudioSidebar {
        width: 30;
        height: 1fr;
        border: round $primary-darken-2;
    }
    AudioSidebar #btn-add-audio { width: 1fr; height: auto; }
    AudioSidebar Input  { width: 1fr; }
    AudioSidebar ListView { width: 1fr; height: 1fr; }
    """

    class AddAudioRequested(Message):
        """Posted when the user clicks the Add Audio button."""

    def __init__(self, audio_dir: Path) -> None:
        super().__init__()
        self._audio_dir = audio_dir
        self._all_files: list[str] = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search-input")
        yield ListView(id="audio-list")
        yield Button("+ Add Audio Files", id="btn-add-audio", variant="primary")

    def on_mount(self) -> None:
        self._reload_files()

    def reload_files(self) -> None:
        self._reload_files()

    def _reload_files(self) -> None:
        if self._audio_dir.exists():
            self._all_files = sorted(
                p.name for p in self._audio_dir.iterdir()
                if p.suffix.lower() in AUDIO_EXTENSIONS
            )
        else:
            self._all_files = []
        search = self.query_one("#search-input", Input).value
        self._apply_filter(search)

    def _apply_filter(self, query: str) -> None:
        lv = self.query_one("#audio-list", ListView)
        lv.clear()
        q = query.lower()
        for name in self._all_files:
            if q in name.lower():
                lv.append(AudioListItem(name))

    def on_input_changed(self, event: Input.Changed) -> None:
        self._apply_filter(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-add-audio":
            event.stop()
            self.post_message(self.AddAudioRequested())
