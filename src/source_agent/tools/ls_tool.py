import fnmatch
import pathlib
from typing import Set, List
from .plugins import registry


def load_gitignore_patterns(root: pathlib.Path) -> Set[str]:
    """
    Load .gitignore patterns from the given root directory.

    Args:
        root (pathlib.Path): The root directory to load .gitignore from.

    Returns:
        Set[str]: A set of ignore patterns.
    """
    patterns = set()
    gitignore = root / ".gitignore"
    if gitignore.exists():
        for line in gitignore.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.add(line)
    return patterns


def is_ignored(path: pathlib.Path, patterns: Set[str], root: pathlib.Path) -> bool:
    """
    Check if the given path matches any of the ignore patterns.

    Args:
        path (pathlib.Path): The path to check.
        patterns (Set[str]): The set of ignore patterns.
        root (pathlib.Path): The root directory to check against.

    Returns:
        bool: True if the path is ignored, False otherwise.
    """
    rel = path.relative_to(root).as_posix()
    parts = path.relative_to(root).parts
    for pattern in patterns:
        if pattern.endswith("/") and pattern.rstrip("/") in parts:
            return True
        if fnmatch.fnmatch(rel, pattern):
            return True
    return False


@registry.register(
    name="ls",
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
def ls(path: str = ".", recursive: bool = False) -> List[str]:
    """
    List files and directories, filtered by .gitignore if available.

    Args:
        path (str): The directory path to list.
        recursive (bool): Whether to list recursively.

    Returns:
        List[str]: Sorted list of files and directories, respecting .gitignore.
    """
    cwd = pathlib.Path.cwd().resolve()
    dir_path = pathlib.Path(path).resolve()

    # Security: Prevent accessing above working directory
    if not dir_path.is_relative_to(cwd):
        return [f"Error: Path traversal detected - {path}"]
    if not dir_path.exists():
        return [f"Error: Directory not found - {path}"]
    if not dir_path.is_dir():
        return [f"Error: Path is not a directory - {path}"]

    ignore_patterns = load_gitignore_patterns(dir_path)

    items = []
    iterator = dir_path.rglob("*") if recursive else dir_path.iterdir()

    for item in iterator:
        if is_ignored(item, ignore_patterns, dir_path):
            continue
        # Relative to cwd for consistent output
        formatted = str(item.relative_to(cwd))
        if item.is_dir() and not recursive:
            formatted += "/"
        items.append(formatted)

    return sorted(items)
