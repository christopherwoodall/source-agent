import pathlib
from .plugins import registry


@registry.register(
    name="cat",
    description="Read the contents of a file.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file to read.",
            }
        },
        "required": ["path"],
    },
)
def cat(path):
    return [pathlib.Path(path).read_text()]
