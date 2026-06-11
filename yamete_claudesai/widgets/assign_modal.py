from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Label

from yamete_claudesai.hooks import HOOKS


class AssignModal(ModalScreen[set[str] | None]):
    """
    Hook multi-select modal for a single audio file.
    Dismissed with set[str] of selected hook names, or None on cancel.
    """

    DEFAULT_CSS = """
    AssignModal { align: center middle; }
    AssignModal > Vertical {
        width: 56;
        height: auto;
        border: thick $primary;
        padding: 1 2;
        background: $surface;
    }
    AssignModal .modal-title { text-style: bold; margin-bottom: 1; }
    AssignModal .btn-row { layout: horizontal; height: auto; margin-top: 1; }
    AssignModal .btn-row Button { margin-right: 1; }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, filename: str, currently_assigned: set[str]) -> None:
        super().__init__()
        self._filename = filename
        self._currently_assigned = currently_assigned

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(f"Assign: {self._filename}", classes="modal-title")
            for hook in HOOKS:
                yield Checkbox(
                    f"{hook.name} — {hook.description}",
                    value=hook.name in self._currently_assigned,
                    id=f"cb-{hook.name}",
                )
            with Vertical(classes="btn-row"):
                yield Button("Confirm", variant="primary", id="btn-confirm")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm":
            selected = {
                hook.name
                for hook in HOOKS
                if self.query_one(f"#cb-{hook.name}", Checkbox).value
            }
            self.dismiss(selected)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
