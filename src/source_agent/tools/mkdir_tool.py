import pathlib
from typing import List
from .plugins import registry


@registry.register(
    name="mkdir",
    description="Create a directory at the given path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The directory path to create.",
            },
            "parents": {
                "type": "boolean",
                "description": "Whether to create parent directories.",
                "default": True,
            },
            "exist_ok": {
                "type": "boolean",
                "description": "Whether it's okay if the directory already exists.",
                "default": True,
            },
        },
        "required": ["path"],
    },
)
def mkdir(path: str, parents: bool = True, exist_ok: bool = True) -> List[str]:
    """
    Create a directory with safety and options.

    Args:
        path (str): The directory path to create.
        parents (bool): Whether to create parent directories.
        exist_ok (bool): Whether it's okay if the directory already exists.

    Returns:
        List[str]: A message indicating success or an error.
    """
    cwd = pathlib.Path.cwd().resolve()
    dir_path = pathlib.Path(path).resolve()

    # Security: Prevent creating outside the working directory
    if not dir_path.is_relative_to(cwd):
        return [f"Error: Path traversal detected - {path}"]

    dir_path.mkdir(parents=parents, exist_ok=exist_ok)
    return [f"Created directory: {dir_path.relative_to(cwd)}"]
