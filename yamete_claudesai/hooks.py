from dataclasses import dataclass


@dataclass(frozen=True)
class HookDef:
    name: str
    description: str
    important: bool = False


ALL_HOOKS: list[HookDef] = [
    # Session-level
    HookDef("SessionStart", "Fires when a session starts or resumes", important=True),
    HookDef("Setup", "Fires with --init-only or --init/--maintenance in print mode"),
    HookDef("SessionEnd", "Fires when a session terminates"),
    # Per-turn
    HookDef("UserPromptSubmit", "Fires when the user submits a prompt", important=True),
    HookDef("UserPromptExpansion", "Fires when a user command expands into a prompt"),
    HookDef("Stop", "Fires when Claude finishes responding", important=True),
    HookDef("StopFailure", "Fires when the turn ends due to an API error"),
    # Agentic loop
    HookDef("PreToolUse", "Fires before a tool call executes", important=True),
    HookDef("PermissionRequest", "Fires when a permission dialog appears"),
    HookDef("PermissionDenied", "Fires when a tool call is denied"),
    HookDef("PostToolUse", "Fires after a tool call succeeds", important=True),
    HookDef("PostToolUseFailure", "Fires after a tool call fails"),
    HookDef("PostToolBatch", "Fires after a full batch of parallel tool calls"),
    HookDef("PreCompact", "Fires before context compaction"),
    HookDef("PostCompact", "Fires after context compaction completes"),
    # Subagent & team
    HookDef("SubagentStart", "Fires when a subagent is spawned"),
    HookDef("SubagentStop", "Fires when a subagent finishes", important=True),
    HookDef("TeammateIdle", "Fires when an agent team teammate is about to go idle"),
    HookDef("TaskCreated", "Fires when a task is being created"),
    HookDef("TaskCompleted", "Fires when a task is being marked as completed"),
    # File & config
    HookDef("InstructionsLoaded", "Fires when a CLAUDE.md or rules file is loaded"),
    HookDef("ConfigChange", "Fires when a configuration file changes"),
    HookDef("FileChanged", "Fires when a watched file changes on disk"),
    HookDef("CwdChanged", "Fires when the working directory changes"),
    # Worktree
    HookDef("WorktreeCreate", "Fires when a worktree is being created"),
    HookDef("WorktreeRemove", "Fires when a worktree is being removed"),
    # MCP & notifications
    HookDef("Elicitation", "Fires when an MCP server requests user input"),
    HookDef("ElicitationResult", "Fires after a user responds to an MCP elicitation"),
    HookDef("Notification", "Fires when Claude Code sends a notification", important=True),
    HookDef("MessageDisplay", "Fires while assistant message text is displayed"),
]

IMPORTANT_HOOKS: list[HookDef] = [h for h in ALL_HOOKS if h.important]

# Backward-compatible alias — app.py uses HOOKS to iterate all known hooks
HOOKS = ALL_HOOKS
