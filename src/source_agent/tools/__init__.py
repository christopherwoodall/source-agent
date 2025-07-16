import pathlib
import importlib


# Auto-load all .py files in this directory (excluding __init__.py and tool_registry.py)
for path in pathlib.Path(__file__).parent.glob("*.py"):
    if path.stem not in ["__init__", "tool_registry"]:
        importlib.import_module(f"{__package__}.{path.stem}")
