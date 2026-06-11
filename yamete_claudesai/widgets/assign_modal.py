from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, SelectionList
from textual.widgets._selection_list import Selection

from yamete_claudesai.hooks import IMPORTANT_HOOKS
from yamete_claudesai.widgets.all_hooks_modal import AllHooksModal


class AssignModal(ModalScreen[set[str] | None]):
    """
    Hook multi-select modal for a single audio file.
    Shows the most-used hooks; "See All" opens the full browser.
    Dismissed with set[str] of selected hook names, or None on cancel.
    """

    DEFAULT_CSS = """
    AssignModal { align: center middle; }
    AssignModal > Vertical {
        width: 64;
        height: auto;
        border: thick $primary;
        padding: 1 2;
        background: $surface;
    }
    AssignModal .modal-title { text-style: bold; }
    AssignModal .subtitle { color: $text-muted; margin-bottom: 1; }
    AssignModal SelectionList { height: auto; max-height: 16; border: round $primary-darken-2; }
    AssignModal .btn-row { layout: horizontal; height: auto; margin-top: 1; }
    AssignModal .btn-row Button { margin-right: 1; }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, filename: str, currently_assigned: set[str]) -> None:
        super().__init__()
        self._filename = filename
        self._currently_assigned = currently_assigned
        important_names = {h.name for h in IMPORTANT_HOOKS}
        self._extra_selected: set[str] = currently_assigned - important_names

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(f"Assign: {self._filename}", classes="modal-title")
            yield Label("↑↓ navigate · Space toggle", classes="subtitle")
            yield SelectionList(
                *[
                    Selection(
                        f"{h.name}  —  {h.description}",
                        h.name,
                        h.name in self._currently_assigned,
                    )
                    for h in IMPORTANT_HOOKS
                ],
                id="hook-list",
            )
            with Horizontal(classes="btn-row"):
                yield Button("Confirm", variant="primary", id="btn-confirm")
                yield Button("See All", variant="default", id="btn-see-all")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def _current_selections(self) -> set[str]:
        sl = self.query_one("#hook-list", SelectionList)
        return set(sl.selected) | self._extra_selected

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-confirm":
                self.dismiss(self._current_selections())
            case "btn-see-all":
                self._open_all_hooks()
            case "btn-cancel":
                self.dismiss(None)

    def _open_all_hooks(self) -> None:
        def handle_result(result: set[str] | None) -> None:
            if result is None:
                return
            important_names = {h.name for h in IMPORTANT_HOOKS}
            self._extra_selected = result - important_names
            sl = self.query_one("#hook-list", SelectionList)
            for hook in IMPORTANT_HOOKS:
                if hook.name in result:
                    sl.select(hook.name)
                else:
                    sl.deselect(hook.name)

        self.app.push_screen(AllHooksModal(self._current_selections()), handle_result)

    def action_cancel(self) -> None:
        self.dismiss(None)
