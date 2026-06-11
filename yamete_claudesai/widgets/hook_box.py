from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Static

from yamete_claudesai.state import AppState, AudioStatus


class AudioLabel(Static):
    """A single audio filename line, color-coded by AudioStatus."""

    DEFAULT_CSS = """
    AudioLabel { height: auto; }
    AudioLabel.added  { color: $success; }
    AudioLabel.removed { color: $error; }
    """

    def __init__(self, filename: str, status: AudioStatus) -> None:
        css_class = {
            AudioStatus.ADDED: "added",
            AudioStatus.REMOVED: "removed",
            AudioStatus.NORMAL: "",
        }[status]
        prefix = {"added": "+ ", "removed": "- ", "": "  "}[css_class]
        super().__init__(prefix + filename, classes=css_class)


class HookBox(Vertical):
    """Shows one hook: bold name, muted description, color-coded audio entries."""

    DEFAULT_CSS = """
    HookBox {
        height: auto;
        border: round $primary-darken-2;
        padding: 0 1;
        margin-bottom: 1;
    }
    HookBox .hook-name { text-style: bold; }
    HookBox .hook-desc { color: $text-muted; }
    """

    def __init__(self, hook_name: str, description: str, state: AppState) -> None:
        super().__init__()
        self._hook_name = hook_name
        self._description = description
        self._state = state

    def compose(self) -> ComposeResult:
        yield Label(self._hook_name, classes="hook-name")
        yield Label(self._description, classes="hook-desc")
        for entry in self._state.assignments.get(self._hook_name, []):
            yield AudioLabel(entry.filename, entry.status)

    def refresh_entries(self) -> None:
        for lbl in list(self.query(AudioLabel)):
            lbl.remove()
        for entry in self._state.assignments.get(self._hook_name, []):
            self.mount(AudioLabel(entry.filename, entry.status))
