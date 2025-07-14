import fnmatch
import pathlib
from typing import Set
from .plugins import registry


def load_gitignore_patterns(root_path: pathlib.Path = None) -> Set[str]:
    """Load .gitignore patterns from the given root path."""
    if root_path is None:
        root_path = pathlib.Path(".")

    patterns = set()
    gitignore_path = root_path / ".gitignore"

    if gitignore_path.exists():
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        # Remove trailing slashes for directory patterns
                        # if line.endswith("/"):
                        #     line = line.rstrip("/")
                        patterns.add(line)
        except (IOError, OSError):
            # If we can't read .gitignore, return empty set
            pass

    return patterns


def should_ignore(
    path: pathlib.Path, ignore_patterns: Set[str], root_path: pathlib.Path
) -> bool:
    """Check if a path should be ignored based on .gitignore patterns."""
    try:
        # Get relative path from root
        rel_path = path.relative_to(root_path)
    except ValueError:
        # If path is not relative to root, don't ignore
        return False

    # Convert to string with forward slashes for consistent matching
    path_str = str(rel_path).replace("\\", "/")

    # Check against each pattern
    for pattern in ignore_patterns:
        # Handle directory patterns
        if pattern.endswith("/"):
            dir_pattern = pattern.rstrip("/")
            # Check if any parent directory matches
            parts = path_str.split("/")
            for i in range(len(parts)):
                if fnmatch.fnmatch("/".join(parts[: i + 1]), dir_pattern):
                    return True
        else:
            # Check file pattern
            if fnmatch.fnmatch(path_str, pattern):
                return True
            # Check if file is in ignored directory
            parts = path_str.split("/")
            for i in range(len(parts)):
                if fnmatch.fnmatch("/".join(parts[: i + 1]), pattern):
                    return True

    return False


@registry.register(
    name="grep",
    description="Search for a file matching a pattern, respecting .gitignore.",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Python glob pattern to match files.",
                "default": "**/*.py",
            }
        },
        "required": ["pattern"],
    },
)
def grep(pattern):
    root_path = pathlib.Path(".")
    ignore_patterns = load_gitignore_patterns(root_path)

    # Get all files matching the pattern
    all_files = list(root_path.rglob(pattern.lstrip("/")))

    # Filter out ignored files and directories
    filtered_files = []
    for file_path in all_files:
        # Skip if it's a directory
        if file_path.is_dir():
            continue

        # Skip if the file or any parent should be ignored
        if not should_ignore(file_path, ignore_patterns, root_path):
            filtered_files.append(file_path)

    if not filtered_files:
        # return f"No files found matching pattern: {pattern}"
        return []

    return [str(file.relative_to(root_path)) for file in sorted(filtered_files)]
