import pathlib
import pathspec
from .tool_registry import registry


def load_gitignore(root: pathlib.Path):
    gitignore = root / ".gitignore"
    if gitignore.exists():
        lines = gitignore.read_text(encoding="utf-8").splitlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", lines)
    return None


@registry.register(
    name="file_list_tool",
    description="List files and directories in a given path, respecting .gitignore if present.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "default": ".",
                "description": "Directory to list.",
            },
            "recursive": {
                "type": "boolean",
                "default": False,
                "description": "List recursively.",
            },
        },
        "required": [],
    },
)
def file_list_tool(path=".", recursive=False):
    cwd = pathlib.Path.cwd().resolve()
    try:
        target = (cwd / path).resolve(strict=True)
    except FileNotFoundError:
        return {"success": False, "error": f"Path not found: {path}"}

    if not target.is_dir():
        return {"success": False, "error": f"Not a directory: {path}"}
    if not str(target).startswith(str(cwd)):
        return {"success": False, "error": "Path traversal not allowed."}

    spec = load_gitignore(cwd)
    rel = lambda p: p.relative_to(cwd).as_posix()  # noqa: E731

    items = []
    paths = target.rglob("*") if recursive else target.iterdir()

    for p in paths:
        if spec and spec.match_file(rel(p)):
            continue
        name = rel(p)
        if p.is_dir() and not recursive:
            name += "/"
        items.append(name)

    return {"success": True, "files": sorted(items)}
