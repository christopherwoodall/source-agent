# ruff: noqa: E501
from datetime import datetime
from .tool_registry import registry


@registry.register(
    name="msg_complete_tool",
    description="REQUIRED: Call this tool when you have fulfilled the user's request and are satisfied with your response or when there is nothing to add. This signals task completion and exits the agent loop.",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
def msg_complete_tool() -> dict:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "success": True,
        "content": {
            "status": "completed",
            "timestamp": timestamp,
        },
    }
