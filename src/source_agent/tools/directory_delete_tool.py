import pathlib
from .tool_registry import registry


@registry.register(
    name="directory_delete_tool",
    description="Delete a directory safely inside the current working directory.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the directory to delete.",
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to delete directories recursively.",
                "default": False,
            },
        },
        "required": ["path"],
    },
)
def directory_delete_tool(path: str, recursive: bool = False) -> dict:
    """
    Delete a directory with safety checks.

    Args:
        path (str): The path to the directory to delete.
        recursive (bool): Whether to delete non-empty directories recursively.

    Returns:
        dict: A dictionary with path and success or error info.
    """
    dir_path = pathlib.Path(path).resolve()
    cwd = pathlib.Path.cwd().resolve()

    # Prevent deleting directories outside the current working directory
    if not dir_path.is_relative_to(cwd):
        return {
            "path": path,
            "success": False,
            "error": f"Path traversal detected - {path}",
        }

    if not dir_path.exists():
        return {
            "path": path,
            "success": False,
            "error": f"Directory not found - {path}",
        }

    if not dir_path.is_dir():
        return {
            "path": path,
            "success": False,
            "error": f"Path is not a directory - {path}",
        }

    try:
        if recursive:
            # Remove directory and all contents
            import shutil

            shutil.rmtree(dir_path)
        else:
            # Remove only empty directory
            dir_path.rmdir()

        return {
            "path": path,
            "success": True,
        }
    except Exception as e:
        return {
            "path": path,
            "success": False,
            "error": f"Failed to delete directory - {path}: {str(e)}",
        }
