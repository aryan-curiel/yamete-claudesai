from yamete_claudesai.hooks import ALL_HOOKS, HOOKS, IMPORTANT_HOOKS, HookDef


def test_all_hooks_contains_all_known_events():
    names = {h.name for h in ALL_HOOKS}
    required = {
        "Stop", "Notification", "PreToolUse", "PostToolUse", "SubagentStop",
        "SessionStart", "UserPromptSubmit", "SessionEnd", "Setup",
    }
    assert required <= names


def test_hooks_alias_equals_all_hooks():
    assert HOOKS is ALL_HOOKS


def test_important_hooks_are_subset_of_all_hooks():
    all_names = {h.name for h in ALL_HOOKS}
    for h in IMPORTANT_HOOKS:
        assert h.name in all_names
        assert h.important is True


def test_important_hooks_include_core_events():
    names = {h.name for h in IMPORTANT_HOOKS}
    assert {"Stop", "Notification", "PreToolUse", "PostToolUse", "SubagentStop"} <= names


def test_hookdef_has_name_and_description():
    for h in ALL_HOOKS:
        assert isinstance(h, HookDef)
        assert h.name and h.description
