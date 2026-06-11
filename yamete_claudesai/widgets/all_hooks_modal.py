from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, SelectionList
from textual.widgets._selection_list import Selection

from yamete_claudesai.hooks import ALL_HOOKS


class AllHooksModal(ModalScreen[set[str] | None]):
    """
    Full hook browser with search. Dismissed with the full set of selected
    hook names, or None on cancel.
    """

    DEFAULT_CSS = """
    AllHooksModal { align: center middle; }
    AllHooksModal > Vertical {
        width: 72;
        height: 38;
        border: thick $primary;
        padding: 1 2;
        background: $surface;
    }
    AllHooksModal .modal-title { text-style: bold; }
    AllHooksModal .subtitle { color: $text-muted; margin-bottom: 1; }
    AllHooksModal #search { margin-bottom: 1; }
    AllHooksModal SelectionList { height: 1fr; border: round $primary-darken-2; }
    AllHooksModal .btn-row { height: auto; margin-top: 1; }
    AllHooksModal .btn-row Button { margin-right: 1; }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, currently_selected: set[str]) -> None:
        super().__init__()
        self._selected: set[str] = set(currently_selected)
        self._visible_names: set[str] = {h.name for h in ALL_HOOKS}

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("All Hooks", classes="modal-title")
            yield Label("↑↓ navigate · Space toggle · Type to search", classes="subtitle")
            yield Input(placeholder="Search by name or description…", id="search")
            yield SelectionList(*self._make_options(""), id="hook-list")
            with Horizontal(classes="btn-row"):
                yield Button("Confirm", variant="primary", id="btn-confirm")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def _make_options(self, query: str) -> list[Selection]:
        q = query.lower()
        return [
            Selection(
                f"{h.name}  —  {h.description}",
                h.name,
                h.name in self._selected,
            )
            for h in ALL_HOOKS
            if not q or q in h.name.lower() or q in h.description.lower()
        ]

    def _sync_from_list(self) -> None:
        """Persist visible selections into _selected before rebuilding the list."""
        sl = self.query_one("#hook-list", SelectionList)
        visible_selected = set(sl.selected)
        for name in self._visible_names:
            if name in visible_selected:
                self._selected.add(name)
            else:
                self._selected.discard(name)

    @on(Input.Changed, "#search")
    def filter_hooks(self, event: Input.Changed) -> None:
        self._sync_from_list()
        new_options = self._make_options(event.value)
        self._visible_names = {
            h.name for h in ALL_HOOKS
            if not event.value.lower()
            or event.value.lower() in h.name.lower()
            or event.value.lower() in h.description.lower()
        }
        sl = self.query_one("#hook-list", SelectionList)
        sl.clear_options()
        for opt in new_options:
            sl.add_option(opt)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm":
            self._sync_from_list()
            self.dismiss(self._selected)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
