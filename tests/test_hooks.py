from yamete_claudesai.hooks import HOOKS, HookDef


def test_hooks_has_five_entries():
    assert len(HOOKS) == 5


def test_hook_names_are_known_claude_hooks():
    names = {h.name for h in HOOKS}
    assert names == {"Stop", "Notification", "PreToolUse", "PostToolUse", "SubagentStop"}


def test_hookdef_has_name_and_description():
    for h in HOOKS:
        assert isinstance(h, HookDef)
        assert h.name and h.description
