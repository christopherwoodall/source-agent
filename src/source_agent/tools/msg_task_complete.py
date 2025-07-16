# ruff: noqa: E501
from datetime import datetime
from .tool_registry import registry


@registry.register(
    name="msg_task_complete",
    description="REQUIRED: Call this tool when the user's original request has been fully satisfied and you have provided a complete answer. This signals task completion and exits the agent loop.",
    parameters={
        "type": "object",
        "properties": {
            "task_summary": {
                "type": "string",
                "description": "Brief summary of what was accomplished",
            },
            "completion_message": {
                "type": "string",
                "description": "Message to show the user indicating the task is complete",
            },
        },
        "required": ["task_summary", "completion_message"],
    },
)
def msg_task_complete(task_summary: str, completion_message: str) -> dict:
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "success": True,
            "content": {
                "status": "completed",
                "task_summary": task_summary,
                "completion_message": completion_message,
                "timestamp": timestamp,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "content": [f"Failed to mark task complete: {str(e)}"],
        }
