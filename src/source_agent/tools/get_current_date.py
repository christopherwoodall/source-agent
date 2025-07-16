import datetime
from .tool_registry import registry


@registry.register(
    name="get_current_date",
    description="Returns the current date and time in ISO 8601 format.",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
def get_current_date() -> dict:
    """
    Get the current date and time in ISO 8601 format.

    Returns:
        dict: A dictionary containing the current date and time.
    """
    now = datetime.datetime.now().isoformat()
    return {
        "current_datetime": now,
        "success": True,
    }
