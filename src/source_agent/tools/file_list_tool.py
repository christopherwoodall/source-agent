import pathlib
import pathspec
from typing import Optional
from .tool_registry import registry


def load_gitignore_spec(root: pathlib.Path) -> Optional[pathspec.PathSpec]:
    """
    Load a PathSpec object from a .gitignore file in the given root directory.

    Args:
        root (pathlib.Path): The root directory to look for .gitignore.

    Returns:
        PathSpec or None: A compiled PathSpec or None if .gitignore doesn't exist.
    """
    gitignore = root / ".gitignore"
    if gitignore.exists():
        lines = gitignore.read_text(encoding="utf-8").splitlines()
        # Compile patterns using gitwildmatch (same as .gitignore)
        return pathspec.PathSpec.from_lines("gitwildmatch", lines)
    return None


def is_ignored(
    path: pathlib.Path, spec: Optional[pathspec.PathSpec], root: pathlib.Path
) -> bool:
    """
    Check if the given path matches the PathSpec patterns.

    Args:
        path (pathlib.Path): The path to check.
        spec (PathSpec or None): A PathSpec object or None.
        root (pathlib.Path): The root directory for relative matching.

    Returns:
        bool: True if the path is ignored, False otherwise.
    """
    if not spec:
        return False
    # Convert to POSIX-style relative path for matching
    rel = path.relative_to(root).as_posix()
    return spec.match_file(rel)


def is_subpath(path: pathlib.Path, base: pathlib.Path) -> bool:
    """
    Check whether 'path' is a subpath of 'base'.

    Args:
        path (pathlib.Path): The path to check.
        base (pathlib.Path): The base directory.

    Returns:
        bool: True if path is within base, False otherwise.
    """
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


@registry.register(
    name="file_list_tool",
    description="List files and directories in a given path, respecting .gitignore if present.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The directory path to list.",
                "default": ".",
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to list recursively.",
                "default": False,
            },
        },
        "required": [],
    },
)
def file_list_tool(path: str = ".", recursive: bool = False) -> dict:
    """
    List files and directories, filtered by .gitignore if available.

    Args:
        path (str): The directory path to list.
        recursive (bool): Whether to list recursively.

    Returns:
        dict: A list of files and directories, or an error message if the path is invalid.
    """
    cwd = pathlib.Path.cwd().resolve()

    try:
        # Resolve the user-provided path securely
        dir_path = pathlib.Path(path).resolve(strict=True)
    except FileNotFoundError:
        return {
            "error": f"Directory not found - {path}",
            "success": False,
        }

    if not dir_path.is_dir():
        return {
            "error": f"Path is not a directory - {path}",
            "success": False,
        }

    # Prevent access to paths outside the working directory
    if not is_subpath(dir_path, cwd):
        return {
            "error": f"Path traversal detected - {path}",
            "success": False,
        }

    # Load .gitignore patterns (if any) into a PathSpec
    spec = load_gitignore_spec(dir_path)

    items = []
    # Choose recursive or shallow listing
    iterator = dir_path.rglob("*") if recursive else dir_path.iterdir()

    for item in iterator:
        # Skip ignored files/directories
        if is_ignored(item, spec, dir_path):
            continue

        # Format the output relative to the current working directory
        formatted = str(item.relative_to(cwd))
        # Indicate non-recursive subdirectories with trailing slash
        if item.is_dir() and not recursive:
            formatted += "/"

        items.append(formatted)

    return {
        "files": sorted(items),
        "success": True,
    }
