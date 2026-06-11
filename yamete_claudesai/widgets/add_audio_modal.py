from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Label


class AddAudioModal(ModalScreen[Path | None]):
    """File/folder picker. Dismissed with the selected Path or None on cancel."""

    DEFAULT_CSS = """
    AddAudioModal { align: center middle; }
    AddAudioModal > Vertical {
        width: 72;
        height: 32;
        border: thick $primary;
        padding: 1 2;
        background: $surface;
    }
    AddAudioModal .modal-title { text-style: bold; margin-bottom: 1; }
    AddAudioModal DirectoryTree { height: 1fr; border: round $primary-darken-2; }
    AddAudioModal #selected-label { margin-top: 1; color: $text-muted; height: auto; }
    AddAudioModal .btn-row { height: auto; margin-top: 1; }
    AddAudioModal .btn-row Button { margin-right: 1; }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, start_path: Path) -> None:
        super().__init__()
        self._start_path = start_path
        self._selected: Path | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Select an audio file or a folder", classes="modal-title")
            yield DirectoryTree(str(self._start_path), id="dir-tree")
            yield Label("Nothing selected", id="selected-label")
            with Horizontal(classes="btn-row"):
                yield Button("Select", variant="primary", id="btn-select", disabled=True)
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self._selected = event.path
        self.query_one("#selected-label", Label).update(f"File: {event.path.name}")
        self.query_one("#btn-select", Button).disabled = False

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self._selected = event.path
        self.query_one("#selected-label", Label).update(f"Folder: {event.path}")
        self.query_one("#btn-select", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-select" and self._selected is not None:
            self.dismiss(self._selected)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
