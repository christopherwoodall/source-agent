import pathlib
import importlib


# Auto-load all .py files in this directory (excluding __init__.py)
for path in pathlib.Path(__file__).parent.glob("*.py"):
    if path.name != "__init__.py":
        importlib.import_module(f"{__package__}.{path.stem}")
