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
    """
    Read file contents with error handling and security checks.

    Args:
        path (str): The path to the file to read.
    Returns:
        list: The contents of the file as a list, or an error message.
    """
    file_path = pathlib.Path(path).resolve()

    # Security: Check for path traversal
    cwd = pathlib.Path.cwd().resolve()
    if not file_path.is_relative_to(cwd):
        return [f"Error: Path traversal detected - {path}"]

    # Security: Check if file exists and is a regular file
    if not file_path.exists():
        return [f"Error: File not found - {path}"]
    if not file_path.is_file():
        return [f"Error: Path is not a file - {path}"]

    # Security: Check file size (prevent reading huge files)
    max_size = 10 * 1024 * 1024  # 10MB limit
    if file_path.stat().st_size > max_size:
        return [f"Error: File too large (>10MB) - {path}"]

    # Security: Check for common dangerous file extensions
    dangerous_extensions = {".exe", ".dll", ".so", ".dylib", ".bin"}
    if file_path.suffix.lower() in dangerous_extensions:
        return [f"Error: Cannot read binary/executable files - {path}"]

    content = file_path.read_text(encoding="utf-8")
    return [content]
