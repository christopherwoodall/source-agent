import re
import pathlib
import pathspec
from typing import Dict, List, Union, Callable, Optional
from .tool_registry import registry


def load_gitignore_spec(root: pathlib.Path) -> Optional[pathspec.PathSpec]:
    """
    Load a PathSpec object from a .gitignore file in the given root directory.
    """
    gitignore = root / ".gitignore"
    if gitignore.exists():
        lines = gitignore.read_text(encoding="utf-8").splitlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", lines)
    return None


def is_ignored(
    path: pathlib.Path, spec: Optional[pathspec.PathSpec], root: pathlib.Path
) -> bool:
    """
    Check if the given path is ignored based on the pathspec rules.
    """
    if not spec:
        return False
    rel = path.relative_to(root).as_posix()
    return spec.match_file(rel)


def is_subpath(path: pathlib.Path, base: pathlib.Path) -> bool:
    """
    Return True if `path` is within `base` (prevents path traversal).
    """
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def build_plain_text_matcher(pattern: str, ignore_case: bool) -> Callable[[str], bool]:
    """
    Returns a function that checks if a pattern appears in a line.
    """
    if ignore_case:
        lowered = pattern.lower()
        return lambda line: lowered in line.lower()
    return lambda line: pattern in line


@registry.register(
    name="file_search_tool",
    description="Search for files by name and optionally search for text or regex within them.",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Glob pattern to match file names (e.g. *.py)",
            },
            "pattern": {
                "type": "string",
                "description": "Text or regex pattern to search within files (optional)",
            },
            "path": {
                "type": "string",
                "default": ".",
                "description": "Root directory to search from.",
            },
            "regex": {
                "type": "boolean",
                "default": False,
                "description": "Treat pattern as regular expression.",
            },
            "ignore_case": {
                "type": "boolean",
                "default": False,
                "description": "Case-insensitive content search.",
            },
            "ext": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter files by extensions (e.g. ['.py', '.txt'])",
            },
        },
        "required": ["name"],
    },
)
def file_search_tool(
    name: str,
    pattern: Optional[str] = None,
    path: str = ".",
    regex: bool = False,
    ignore_case: bool = False,
    ext: Optional[List[str]] = None,
) -> Dict[str, Union[bool, List[str]]]:
    """
    Search for files in a directory matching a name pattern and optionally search for text or regex inside them.
    Respects .gitignore rules.

    Returns:
        Dict[str, Union[bool, List[str]]]: The search results or error message.
    """
    try:
        cwd = pathlib.Path.cwd().resolve()
        root = pathlib.Path(path).resolve(strict=True)

        if not is_subpath(root, cwd):
            return {
                "success": False,
                "content": [f"Error: Path traversal detected - {path}"],
            }

        if not root.is_dir():
            return {"success": False, "content": [f"Error: Not a directory - {path}"]}

        ignore_spec = load_gitignore_spec(root)
        results = []

        # Create the matcher based on provided pattern
        matcher: Optional[Callable[[str], bool]] = None
        if pattern:
            if regex:
                flags = re.IGNORECASE if ignore_case else 0
                matcher = re.compile(pattern, flags).search
            else:
                matcher = build_plain_text_matcher(pattern, ignore_case)

        # File system traversal and filtering
        for file in root.rglob(name):
            if not file.is_file():
                continue
            if ext and file.suffix not in ext:
                continue
            if is_ignored(file, ignore_spec, root):
                continue

            # If content match is needed
            if matcher:
                try:
                    for i, line in enumerate(
                        file.read_text(encoding="utf-8", errors="ignore").splitlines(),
                        1,
                    ):
                        if matcher(line):
                            rel = file.relative_to(cwd)
                            results.append(f"{rel}:{i}:{line.strip()}")
                except Exception:
                    continue  # Skip files that can't be read
            else:
                results.append(str(file.relative_to(cwd)))

        return {"success": True, "content": results or ["No matches found."]}

    except Exception as e:
        return {"success": False, "content": [f"Unexpected error: {str(e)}"]}
