from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class AudioStatus(Enum):
    NORMAL = auto()
    ADDED = auto()
    REMOVED = auto()


@dataclass
class AudioEntry:
    filename: str
    status: AudioStatus = AudioStatus.NORMAL


class AppState:
    def __init__(self) -> None:
        self.assignments: dict[str, list[AudioEntry]] = {}

    @classmethod
    def from_assignments(cls, assignments: dict[str, list[str]]) -> "AppState":
        state = cls()
        for hook, filenames in assignments.items():
            state.assignments[hook] = [AudioEntry(f) for f in filenames]
        return state

    def set_hook_assignments(self, hook: str, filenames: set[str]) -> None:
        """Diff current entries against desired filenames, marking ADDED/REMOVED."""
        existing = {e.filename: e for e in self.assignments.get(hook, [])}
        new_entries: list[AudioEntry] = []
        for filename, entry in existing.items():
            entry.status = AudioStatus.NORMAL if filename in filenames else AudioStatus.REMOVED
            new_entries.append(entry)
        for filename in filenames:
            if filename not in existing:
                new_entries.append(AudioEntry(filename, AudioStatus.ADDED))
        self.assignments[hook] = new_entries

    def commit(self) -> None:
        """Remove REMOVED entries; reset ADDED -> NORMAL."""
        for hook in list(self.assignments):
            kept = [e for e in self.assignments[hook] if e.status != AudioStatus.REMOVED]
            for e in kept:
                e.status = AudioStatus.NORMAL
            self.assignments[hook] = kept

    def to_assignments_dict(self) -> dict[str, list[str]]:
        return {
            hook: [e.filename for e in entries if e.status != AudioStatus.REMOVED]
            for hook, entries in self.assignments.items()
            if any(e.status != AudioStatus.REMOVED for e in entries)
        }

    def get_assigned_hooks(self, filename: str) -> set[str]:
        return {
            hook
            for hook, entries in self.assignments.items()
            for e in entries
            if e.filename == filename and e.status != AudioStatus.REMOVED
        }
