from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Button, Footer, Header, ListView

from yamete_claudesai.config import AppConfig, load_config, save_config
from yamete_claudesai.hooks import HOOKS
from yamete_claudesai.settings import write_audio_assignments
from yamete_claudesai.state import AppState, AudioStatus
from yamete_claudesai.widgets.add_audio_modal import AddAudioModal
from yamete_claudesai.widgets.assign_modal import AssignModal
from yamete_claudesai.widgets.audio_sidebar import AUDIO_EXTENSIONS, AudioListItem, AudioSidebar
from yamete_claudesai.widgets.confirm_import_modal import ConfirmImportModal
from yamete_claudesai.widgets.hook_box import HookBox
from yamete_claudesai.widgets.question_modal import QuestionModal


class YameteApp(App):
    TITLE = "yamete-kudasai"

    CSS = """
    Screen { layout: vertical; }
    #main-area { layout: horizontal; height: 1fr; }
    #right-col { width: 1fr; height: 1fr; layout: vertical; }
    #right-panel { height: 1fr; overflow-y: auto; padding: 0 1; }
    #confirm-bar { height: auto; padding: 0 1; align: right middle; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_audio", "Add Audio"),
        ("p", "play_audio", "Play"),
        ("space", "assign_audio", "Assign"),
        ("d", "delete_audio", "Delete"),
        ("e", "export_selections", "Export"),
        ("i", "import_selections", "Import"),
    ]

    def __init__(
        self,
        config_dir: Path | None = None,
        settings_path: Path | None = None,
    ) -> None:
        super().__init__()
        self._config_dir = config_dir or Path.home() / ".config" / "yamete-kudasai"
        self._settings_path = settings_path
        cfg = load_config(config_dir=config_dir)
        self._audio_dir = cfg.audio_dir
        self._state = AppState.from_assignments(cfg.assignments)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-area"):
            yield AudioSidebar(self._audio_dir)
            with Vertical(id="right-col"):
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
        self._open_assign_modal(event.item.filename)

    def action_assign_audio(self) -> None:
        lv = self.query_one("#audio-list", ListView)
        item = lv.highlighted_child
        if isinstance(item, AudioListItem):
            self._open_assign_modal(item.filename)

    def _open_assign_modal(self, filename: str) -> None:
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

    # ── Add Audio ────────────────────────────────────────────────────────────

    def action_add_audio(self) -> None:
        self._open_add_audio_picker()

    def action_delete_audio(self) -> None:
        lv = self.query_one("#audio-list", ListView)
        item = lv.highlighted_child
        if not isinstance(item, AudioListItem):
            return
        filename = item.filename

        def handle_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            path = self._audio_dir / filename
            path.unlink(missing_ok=True)
            for hook in HOOKS:
                active_files = {
                    e.filename
                    for e in self._state.assignments.get(hook.name, [])
                    if e.status != AudioStatus.REMOVED and e.filename != filename
                }
                self._state.set_hook_assignments(hook.name, active_files)
            self._refresh_right_panel()
            self.query_one(AudioSidebar).reload_files()
            self.notify(f"Deleted {filename!r}", title="Deleted")

        self.push_screen(QuestionModal(f"Delete '{filename}'?"), handle_confirm)

    def action_play_audio(self) -> None:
        lv = self.query_one("#audio-list", ListView)
        item = lv.highlighted_child
        if not isinstance(item, AudioListItem):
            return
        path = self._audio_dir / item.filename
        subprocess.Popen(["afplay", str(path)])

    def on_audio_sidebar_add_audio_requested(
        self, _event: AudioSidebar.AddAudioRequested
    ) -> None:
        self._open_add_audio_picker()

    def _open_add_audio_picker(self) -> None:
        def handle_picker(selected: Path | None) -> None:
            if selected is None:
                return
            if selected.is_file():
                self._handle_single_file(selected)
            else:
                self._handle_folder(selected)

        self.push_screen(AddAudioModal(Path.home()), handle_picker)

    def _handle_single_file(self, path: Path) -> None:
        if path.suffix.lower() not in AUDIO_EXTENSIONS:
            self.notify(
                f"{path.name!r} is not a supported audio format",
                severity="error",
                title="Unsupported file",
            )
            return

        def handle_confirm(confirmed: bool) -> None:
            if confirmed:
                self._do_copy_files([path])

        self.push_screen(ConfirmImportModal([path]), handle_confirm)

    def _handle_folder(self, folder: Path) -> None:
        def handle_folder_question(confirmed: bool) -> None:
            if not confirmed:
                return
            audio_files = sorted(
                p for p in folder.rglob("*")
                if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
            )
            if not audio_files:
                self.notify(
                    "No supported audio files found in that folder",
                    severity="warning",
                    title="Nothing found",
                )
                return

            def handle_import_confirm(confirmed: bool) -> None:
                if confirmed:
                    self._do_copy_files(audio_files)

            self.push_screen(ConfirmImportModal(audio_files), handle_import_confirm)

        self.push_screen(
            QuestionModal(f"Add all audio files from '{folder.name}'?"),
            handle_folder_question,
        )

    # ── Export / Import ──────────────────────────────────────────────────────

    def action_export_selections(self) -> None:
        export_path = self._config_dir / "selections.json"
        self._config_dir.mkdir(parents=True, exist_ok=True)
        data = {"assignments": self._state.to_assignments_dict()}
        existing: dict = {}
        if export_path.exists():
            try:
                existing = json.loads(export_path.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        for hook, filenames in data["assignments"].items():
            existing_list: list[str] = existing.setdefault("assignments", {}).get(hook, [])
            merged = list(dict.fromkeys(existing_list + filenames))
            existing.setdefault("assignments", {})[hook] = merged
        export_path.write_text(json.dumps(existing, indent=2))
        self.notify(str(export_path), title="Exported ✓")

    def action_import_selections(self) -> None:
        def handle_picked(path: Path | None) -> None:
            if path is None or not path.is_file():
                return
            if path.suffix.lower() != ".json":
                self.notify(
                    f"{path.name!r} is not a JSON file",
                    severity="error",
                    title="Invalid file",
                )
                return
            try:
                raw = json.loads(path.read_text())
            except (json.JSONDecodeError, OSError) as exc:
                self.notify(str(exc), severity="error", title="Could not read file")
                return
            incoming: dict[str, list[str]] = raw.get("assignments", {})
            if not isinstance(incoming, dict):
                self.notify("Unexpected format", severity="error", title="Import failed")
                return
            self._state.merge_assignments(incoming)
            self._refresh_right_panel()
            total = sum(len(v) for v in incoming.values())
            self.notify(
                f"Merged {total} assignment(s) from {path.name!r}",
                title="Imported ✓",
            )

        self.push_screen(AddAudioModal(Path.home()), handle_picked)

    def _do_copy_files(self, files: list[Path]) -> None:
        self._audio_dir.mkdir(parents=True, exist_ok=True)
        skipped: list[str] = []
        copied = 0
        for src in files:
            dest = self._audio_dir / src.name
            if dest.exists():
                skipped.append(src.name)
            else:
                shutil.copy2(src, dest)
                copied += 1

        for name in skipped:
            self.notify(
                f"{name!r} already exists — skipped",
                severity="warning",
                title="Skipped",
            )

        if copied:
            self.query_one(AudioSidebar).reload_files()
            self.notify(f"Added {copied} file(s)", title="Imported ✓")
        elif not skipped:
            self.notify("No files were copied", severity="warning")


def run() -> None:
    YameteApp().run()
