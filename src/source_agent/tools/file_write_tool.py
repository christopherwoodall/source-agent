import pathlib
from .tool_registry import registry


@registry.register(
    name="file_write_tool",
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
def file_write_tool(path: str, content: str) -> dict:
    """
    Write content to a file.

    Args:
        path (str): The path to the file to write.
        content (str): The content to write to the file.

    Returns:
        dict: A dictionary containing the file path, bytes written, success status, and any error message.
    """
    # Get absolute path
    file_path = pathlib.Path(path).resolve()

    # Security: Check for path traversal
    cwd = pathlib.Path.cwd().resolve()
    if not file_path.is_relative_to(cwd):
        return {
            "path": str(file_path),
            "bytes_written": None,
            "success": False,
            "error": f"Path traversal detected - {path}",
        }

    # Create parent directories if needed
    parent_dir = file_path.parent
    if parent_dir and not parent_dir.exists():
        parent_dir.mkdir(parents=True, exist_ok=True)

    # Write file atomically using temporary file
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Atomic rename
        temp_path.rename(file_path)

        return {
            "path": str(file_path),
            "bytes_written": len(content.encode("utf-8")),
            "success": True,
            "message": f"Successfully wrote to {path}",
        }

    except Exception as e:
        # Clean up temp file if it exists
        if temp_path.exists():
            try:
                temp_path.unlink()
            except:  # noqa: E722
                pass
        return {
            "path": str(file_path),
            "bytes_written": None,
            "success": False,
            "error": str(e),
        }
