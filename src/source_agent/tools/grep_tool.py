import re
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
    name="grep",
    description="Search for a string or regex in files, respecting .gitignore.",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Text or regex to search for"},
            "path": {"type": "string", "default": ".", "description": "Search root"},
            "regex": {"type": "boolean", "default": False, "description": "Use regex"},
            "ignore_case": {
                "type": "boolean",
                "default": False,
                "description": "Ignore case",
            },
            "ext": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Only search files with these extensions",
            },
        },
        "required": ["pattern"],
    },
)
def grep(
    pattern: str,
    path: str = ".",
    regex: bool = False,
    ignore_case: bool = False,
    ext: List[str] = None,
) -> List[str]:
    root = pathlib.Path(path).resolve()
    if not root.is_dir():
        return [f"Error: Not a directory - {path}"]

    flags = re.IGNORECASE if ignore_case else 0
    match = (
        re.compile(pattern, flags).search
        if regex
        else (
            lambda line: (
                pattern.lower() in line.lower() if ignore_case else pattern in line
            )
        )
    )

    ignores = load_gitignore_patterns(root)
    results = []

    for file in root.rglob("*"):
        if not file.is_file():
            continue
        if ext and file.suffix not in ext:
            continue
        if is_ignored(file, ignores, root):
            continue

        try:
            for i, line in enumerate(
                file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
            ):
                if match(line):
                    rel = file.relative_to(root)
                    results.append(f"{rel}:{i}:{line.strip()}")
        except Exception:
            continue  # Skip unreadable files

    return results or ["No matches found."]
