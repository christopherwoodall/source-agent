import pathlib
from .plugins import registry


@registry.register(
    name="grep",
    description="Search for a file matching a pattern.",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Python glob pattern to match files.",
                "default": "**/*.py",
            }
        },
        "required": ["pattern"],
    },
)
def grep(pattern):
    files = list(pathlib.Path(".").glob(pattern))
    if not files:
        return f"No files found matching pattern: {pattern}"
    return [str(file) for file in files]
