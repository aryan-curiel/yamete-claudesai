from yamete_claudesai.state import AppState, AudioEntry, AudioStatus


def test_app_state_starts_empty():
    assert AppState().assignments == {}


def test_load_from_assignments_marks_normal():
    state = AppState.from_assignments({"Stop": ["beep.mp3", "boop.wav"]})
    assert all(e.status == AudioStatus.NORMAL for e in state.assignments["Stop"])
    assert state.assignments["Stop"][0].filename == "beep.mp3"


def test_set_hook_assignments_marks_added_and_removed():
    state = AppState.from_assignments({"Stop": ["old.mp3"]})
    state.set_hook_assignments("Stop", {"new.mp3"})
    stop = {e.filename: e for e in state.assignments["Stop"]}
    assert stop["old.mp3"].status == AudioStatus.REMOVED
    assert stop["new.mp3"].status == AudioStatus.ADDED


def test_set_hook_assignments_keeps_unchanged():
    state = AppState.from_assignments({"Stop": ["keep.mp3", "remove.mp3"]})
    state.set_hook_assignments("Stop", {"keep.mp3"})
    stop = {e.filename: e for e in state.assignments["Stop"]}
    assert stop["keep.mp3"].status == AudioStatus.NORMAL
    assert stop["remove.mp3"].status == AudioStatus.REMOVED


def test_set_hook_assignments_on_new_hook():
    state = AppState()
    state.set_hook_assignments("Notification", {"ding.mp3"})
    entries = state.assignments["Notification"]
    assert len(entries) == 1
    assert entries[0].status == AudioStatus.ADDED


def test_commit_removes_removed_and_resets_added():
    state = AppState.from_assignments({"Stop": ["keep.mp3", "gone.mp3"]})
    state.set_hook_assignments("Stop", {"keep.mp3", "new.mp3"})
    state.commit()
    stop = {e.filename: e for e in state.assignments["Stop"]}
    assert "gone.mp3" not in stop
    assert stop["keep.mp3"].status == AudioStatus.NORMAL
    assert stop["new.mp3"].status == AudioStatus.NORMAL


def test_to_assignments_dict_excludes_removed():
    state = AppState.from_assignments({"Stop": ["keep.mp3", "gone.mp3"]})
    state.set_hook_assignments("Stop", {"keep.mp3"})
    assert state.to_assignments_dict() == {"Stop": ["keep.mp3"]}


def test_get_assigned_hooks_for_file():
    state = AppState.from_assignments({"Stop": ["beep.mp3"], "Notification": ["beep.mp3"]})
    assert state.get_assigned_hooks("beep.mp3") == {"Stop", "Notification"}


def test_get_assigned_hooks_excludes_removed():
    state = AppState.from_assignments({"Stop": ["beep.mp3"]})
    state.set_hook_assignments("Stop", set())
    assert "Stop" not in state.get_assigned_hooks("beep.mp3")
