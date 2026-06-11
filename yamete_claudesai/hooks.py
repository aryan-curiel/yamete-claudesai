from dataclasses import dataclass


@dataclass(frozen=True)
class HookDef:
    name: str
    description: str


HOOKS: list[HookDef] = [
    HookDef("Stop", "Runs when Claude Code finishes a task"),
    HookDef("Notification", "Runs when Claude Code needs your attention"),
    HookDef("PreToolUse", "Runs before any tool is executed"),
    HookDef("PostToolUse", "Runs after any tool finishes"),
    HookDef("SubagentStop", "Runs when a subagent task completes"),
]
