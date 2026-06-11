from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Button, Footer, Header, ListView

from yamete_claudesai.config import AppConfig, load_config, save_config
from yamete_claudesai.hooks import HOOKS
from yamete_claudesai.settings import write_audio_assignments
from yamete_claudesai.state import AppState, AudioStatus
from yamete_claudesai.widgets.assign_modal import AssignModal
from yamete_claudesai.widgets.audio_sidebar import AudioListItem, AudioSidebar
from yamete_claudesai.widgets.hook_box import HookBox


class YameteApp(App):
    TITLE = "yamete-kudasai"

    CSS = """
    Screen { layout: vertical; }
    #main-area { layout: horizontal; height: 1fr; }
    #right-panel { width: 1fr; height: 1fr; overflow-y: auto; padding: 0 1; }
    #confirm-bar { height: auto; padding: 0 1; align: right middle; }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(
        self,
        config_dir: Path | None = None,
        settings_path: Path | None = None,
    ) -> None:
        super().__init__()
        self._config_dir = config_dir
        self._settings_path = settings_path
        cfg = load_config(config_dir=config_dir)
        self._audio_dir = cfg.audio_dir
        self._state = AppState.from_assignments(cfg.assignments)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-area"):
            yield AudioSidebar(self._audio_dir)
            with ScrollableContainer(id="right-panel"):
                for hook in HOOKS:
                    if self._state.assignments.get(hook.name):
                        yield HookBox(hook.name, hook.description, self._state)
        with Horizontal(id="confirm-bar"):
            yield Button("Confirm", variant="success", id="btn-confirm-all")
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if not isinstance(event.item, AudioListItem):
            return
        filename = event.item.filename
        currently_assigned = self._state.get_assigned_hooks(filename)

        def handle_result(result: set[str] | None) -> None:
            if result is None:
                return
            for hook in HOOKS:
                active_files = {
                    e.filename
                    for e in self._state.assignments.get(hook.name, [])
                    if e.status != AudioStatus.REMOVED
                }
                if hook.name in result:
                    active_files.add(filename)
                else:
                    active_files.discard(filename)
                self._state.set_hook_assignments(hook.name, active_files)
            self._refresh_right_panel()

        self.push_screen(AssignModal(filename, currently_assigned), handle_result)

    def _refresh_right_panel(self) -> None:
        panel = self.query_one("#right-panel", ScrollableContainer)
        for box in list(panel.query(HookBox)):
            box.remove()
        for hook in HOOKS:
            if self._state.assignments.get(hook.name):
                panel.mount(HookBox(hook.name, hook.description, self._state))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm-all":
            self._commit()

    def _commit(self) -> None:
        assignments_dict = self._state.to_assignments_dict()
        write_audio_assignments(
            assignments=assignments_dict,
            audio_dir=self._audio_dir,
            path=self._settings_path,
        )
        save_config(
            AppConfig(audio_dir=self._audio_dir, assignments=assignments_dict),
            config_dir=self._config_dir,
        )
        self._state.commit()
        self._refresh_right_panel()
        self.notify("Written to ~/.claude/settings.json", title="Saved ✓")


def run() -> None:
    YameteApp().run()
