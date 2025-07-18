import subprocess
import pathlib
from .tool_registry import registry


@registry.register(
    name="execute_shell_command",
    description=(
        "Executes a shell command. Use this tool with extreme caution. "
        "It can run any command on the system where the agent is operating. "
        "Outputs stdout, stderr, and exit code."
    ),
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute.",
            }
        },
        "required": ["command"],
    },
)
def execute_shell_command(command: str) -> dict:
    """
    Executes a shell command and returns its stdout, stderr, and exit code.

    WARNING: This tool allows arbitrary code execution. Ensure the environment
    where this agent runs is properly sandboxed to prevent security risks.

    Args:
        command (str): The shell command to execute.

    Returns:
        dict: A dictionary containing stdout, stderr, exit_code, success status, and any error message.
    """
    try:
        # Using shell=True for simplicity, allowing the agent to use pipes, redirects, etc.
        # This is where the security risk lies.
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
            cwd=pathlib.Path.cwd(),
        )

        return {
            "success": True,
            "command": command,
            "stdout": process.stdout.strip(),
            "stderr": process.stderr.strip(),
            "exit_code": process.returncode,
            "message": f"Command executed with exit code {process.returncode}",
        }
    except Exception as e:
        return {
            "success": False,
            "command": command,
            "stdout": "",
            "stderr": str(e),
            "exit_code": 1, # Indicate failure
            "error": f"Failed to execute command: {str(e)}",
        }