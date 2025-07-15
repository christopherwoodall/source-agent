import pathlib
from .plugins import registry


@registry.register(
    name="write",
    description="Write content to a file.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file to write.",
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file.",
            },
        },
        "required": ["path", "content"],
    },
)
def write(path, content):
    pathlib.Path(path).write_text(content)
    return f"Content written to {path}"
