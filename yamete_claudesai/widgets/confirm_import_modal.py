from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmImportModal(ModalScreen[bool]):
    """Shows the list of audio files to be copied; dismissed True to proceed, False to cancel."""

    DEFAULT_CSS = """
    ConfirmImportModal { align: center middle; }
    ConfirmImportModal > Vertical {
        width: 60;
        height: auto;
        max-height: 34;
        border: thick $primary;
        padding: 1 2;
        background: $surface;
    }
    ConfirmImportModal .modal-title { text-style: bold; margin-bottom: 1; }
    ConfirmImportModal #file-list {
        height: auto;
        max-height: 20;
        border: round $primary-darken-2;
        padding: 0 1;
    }
    ConfirmImportModal .btn-row { height: auto; margin-top: 1; }
    ConfirmImportModal .btn-row Button { margin-right: 1; }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, files: list[Path]) -> None:
        super().__init__()
        self._files = files

    def compose(self) -> ComposeResult:
        count = len(self._files)
        with Vertical():
            yield Label(
                f"Copy {count} file{'s' if count != 1 else ''} to audio folder?",
                classes="modal-title",
            )
            with ScrollableContainer(id="file-list"):
                for f in self._files:
                    yield Label(f.name)
            with Horizontal(classes="btn-row"):
                yield Button("Copy", variant="success", id="btn-copy")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-copy")

    def action_cancel(self) -> None:
        self.dismiss(False)
