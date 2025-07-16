import pathlib
from .tool_registry import registry


@registry.register(
    name="file_delete_tool",
    description="Delete a file safely inside the current working directory.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file to delete.",
            }
        },
        "required": ["path"],
    },
)
def file_delete_tool(path: str) -> dict:
    """
    Delete a file with error handling and security checks.

    Args:
        path (str): The path to the file to delete.

    Returns:
        dict: A dictionary containing the file path and success status or error.
    """
    # Resolve absolute path
    file_path = pathlib.Path(path).resolve()

    # Security: prevent deleting outside the current working directory
    cwd = pathlib.Path.cwd().resolve()
    if not file_path.is_relative_to(cwd):
        return {
            "path": path,
            "success": False,
            "error": f"Path traversal detected - {path}",
        }

    # Check file existence and that it's a file
    if not file_path.exists():
        return {
            "path": path,
            "success": False,
            "error": f"File not found - {path}",
        }
    if not file_path.is_file():
        return {
            "path": path,
            "success": False,
            "error": f"Path is not a file - {path}",
        }

    try:
        file_path.unlink()
        return {
            "path": path,
            "success": True,
        }
    except Exception as e:
        return {
            "path": path,
            "success": False,
            "error": f"Failed to delete file - {path}: {str(e)}",
        }
