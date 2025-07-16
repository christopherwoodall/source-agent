# ruff: noqa: E501

from datetime import datetime
from .tool_registry import registry


@registry.register(
    name="msg_final_answer",
    description="Final summary of the task. Call this tool when the user's original request has been fully satisfied and you have provided a complete answer. This signals task completion and exits the agent loop.",
    parameters={
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": "The final answer to the user's question or request.",
            },
        },
        "required": ["answer"],
    },
)
def msg_final_answer(answer: str):
    """
    Final summary of the task.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "success": True,
        "content": {
            "status": "answered",
            "answer": answer,
            "timestamp": timestamp,
        },
    }
