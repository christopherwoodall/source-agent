import sys
import subprocess
import pathlib
from typing import List, Optional
from .tool_registry import registry


@registry.register(
    name="run_pytest_tests",
    description="Runs pytest tests in a specified directory or for specific files.",
    parameters={
        "type": "object",
        "properties": {
            "target_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "A list of paths (files or directories) to run pytest on. Defaults to current directory if empty.",
                "default": [],
            },
            "pytest_args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Additional arguments to pass directly to pytest (e.g., ['-k', 'test_my_feature']).",
                "default": [],
            },
        },
    },
)
def run_pytest_tests(target_paths: Optional[List[str]] = None, pytest_args: Optional[List[str]] = None) -> dict:
    """
    Runs pytest tests in a specified directory or for specific files.

    Args:
        target_paths (List[str], optional): Paths to run pytest on.
        pytest_args (List[str], optional): Additional arguments for pytest.

    Returns:
        dict: A dictionary containing success status, output, and any error message.
    """
    cmd = [sys.executable, "-m", "pytest"]

    if target_paths:
        for path_str in target_paths:
            path = pathlib.Path(path_str).resolve()
            cwd = pathlib.Path.cwd().resolve()
            if not path.is_relative_to(cwd):
                return {
                    "success": False,
                    "error": f"Path traversal detected for target_path - {path_str}",
                    "stdout": "",
                    "stderr": "",
                    "exit_code": 1,
                }
            cmd.append(str(path))
    else:
        # If no target_paths, pytest runs in the current directory by default
        pass

    if pytest_args:
        cmd.extend(pytest_args)

    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,  # Pytest returns non-zero on test failures, which is not an execution error
            cwd=pathlib.Path.cwd(),
        )

        # Pytest exit codes: 0 (all passed), 1 (tests failed), 2 (internal error), 3 (usage error), 4 (no tests collected), 5 (no tests ran)
        # We consider 0 as success, others as failure in the context of the tool's success status
        is_success = process.returncode == 0

        return {
            "success": is_success,
            "command": " ".join(cmd),
            "stdout": process.stdout.strip(),
            "stderr": process.stderr.strip(),
            "exit_code": process.returncode,
            "message": "Pytest execution completed." if is_success else "Pytest tests failed or encountered issues.",
        }
    except Exception as e:
        return {
            "success": False,
            "command": " ".join(cmd),
            "error": f"An unexpected error occurred during pytest execution: {str(e)}",
            "stdout": "",
            "stderr": "",
            "exit_code": 1,
        }