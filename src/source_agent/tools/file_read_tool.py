import pathlib
from .tool_registry import registry


@registry.register(
    name="file_read_tool",
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
def file_read_tool(path: str) -> dict:
    """
    Read file contents with error handling and security checks.

    Args:
        path (str): The path to the file to read.

    Returns:
        dict: A dictionary containing the file path, content, and success status.
    """
    # Get absolute path
    file_path = pathlib.Path(path).resolve()

    # Security: Check for path traversal
    cwd = pathlib.Path.cwd().resolve()
    if not file_path.is_relative_to(cwd):
        return {
            "path": path,
            "content": None,
            "success": False,
            "error": f"Path traversal detected - {path}",
        }

    # Security: Check if file exists and is a regular file
    if not file_path.exists():
        return {
            "path": path,
            "content": None,
            "success": False,
            "error": f"File not found - {path}",
        }
    if not file_path.is_file():
        return {
            "path": path,
            "content": None,
            "success": False,
            "error": f"Path is not a file - {path}",
        }

    # Security: Check file size (prevent reading huge files)
    max_size = 10 * 1024 * 1024  # 10MB limit
    if file_path.stat().st_size > max_size:
        return {
            "path": path,
            "content": None,
            "success": False,
            "error": f"File too large (>10MB) - {path}",
        }

    # Security: Check for common dangerous file extensions
    dangerous_extensions = {".exe", ".dll", ".so", ".dylib", ".bin"}
    if file_path.suffix.lower() in dangerous_extensions:
        return {
            "path": path,
            "content": None,
            "success": False,
            "error": f"Cannot read binary/executable files - {path}",
        }

    content = file_path.read_text()

    return {"path": path, "content": content, "success": True}
