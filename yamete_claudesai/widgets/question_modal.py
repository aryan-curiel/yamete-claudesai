from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class QuestionModal(ModalScreen[bool]):
    """Simple yes/no dialog. Dismissed with True for Yes, False for No/escape."""

    DEFAULT_CSS = """
    QuestionModal { align: center middle; }
    QuestionModal > Vertical {
        width: 56;
        height: auto;
        border: thick $primary;
        padding: 1 2;
        background: $surface;
    }
    QuestionModal .modal-question { margin-bottom: 1; }
    QuestionModal .btn-row { height: auto; margin-top: 1; }
    QuestionModal .btn-row Button { margin-right: 1; }
    """

    BINDINGS = [("escape", "no", "No")]

    def __init__(self, question: str) -> None:
        super().__init__()
        self._question = question

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._question, classes="modal-question")
            with Horizontal(classes="btn-row"):
                yield Button("Yes", variant="success", id="btn-yes")
                yield Button("No", variant="default", id="btn-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-yes")

    def action_no(self) -> None:
        self.dismiss(False)
