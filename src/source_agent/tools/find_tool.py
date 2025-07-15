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
    name="find",
    description="Find files by name pattern (glob) in directory tree, respecting .gitignore.",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Glob pattern to match file names (e.g. *.py)",
            },
            "path": {
                "type": "string",
                "description": "Root directory to search from.",
                "default": ".",
            },
        },
        "required": ["name"],
    },
)
def find(name: str, path: str = ".") -> List[str]:
    root = pathlib.Path(path).resolve()
    cwd = pathlib.Path.cwd().resolve()

    if not root.is_relative_to(cwd):
        return [f"Error: Path traversal detected - {path}"]
    if not root.is_dir():
        return [f"Error: Not a directory - {path}"]

    ignores = load_gitignore_patterns(root)
    found = []

    for p in root.rglob(name):
        if p.is_file() and not is_ignored(p, ignores, root):
            found.append(str(p.relative_to(cwd)))

    return sorted(found)
