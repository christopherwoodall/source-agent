# ruff: noqa: E501
from datetime import datetime
from .tool_registry import registry


@registry.register(
    name="msg_task_complete",
    description="REQUIRED: Call this tool when the user's original request has been fully satisfied and you have provided a complete answer. This signals task completion and exits the agent loop.",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
def msg_task_complete() -> dict:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "success": True,
        "content": {
            "status": "completed",
            "timestamp": timestamp,
        },
    }
