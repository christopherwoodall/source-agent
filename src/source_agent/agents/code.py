import json
import openai
import source_agent
from pathlib import Path
from pyexpat.errors import messages


# TODO - MOVE TOOLS
def grep(pattern):
    """
    Recursive search for a pattern in a filename.
    Args:
        pattern (str): The pattern to search for.
    Returns:
        list: A list of files that match the pattern.
    """
    files = list(Path(".").glob(pattern))
    if not files:
        return f"No files found matching pattern: {pattern}"
    return [str(file) for file in files]


def cat(path):
    """
    Read the contents of a file.
    Args:
        path (str): The path to the file to read.
    Returns:
        str: The contents of the file.
    """
    return [Path(path).read_text()]


def write(path, content):
    """
    Write content to a file.
    Args:
        path (str): The path to the file to write.
        content (str): The content to write to the file.
    """
    Path(path).write_text(content)
    return f"Content written to {path}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search for a file matching a pattern.",
            "parameters": {
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
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cat",
            "description": "Read the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to read.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write",
            "description": "Write content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
]


# TODO - MOVE TOOLS
TOOL_MAPPING = {"grep": grep, "cat": cat, "write": write}


class CodeAgent:
    def __init__(
        self, api_key=None, base_url=None, provider=None, model=None, prompt=None
    ):
        self.api_key = api_key
        self.base_url = base_url

        self.model_string = "/".join([provider, model])
        self.temperature = 0.3

        self.messages = []
        self.prompt = prompt
        self.system_prompt = Path("AGENTS.md").read_text(encoding="utf-8")

        self.session = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

        self.messages.append({"role": "system", "content": self.system_prompt})
        # self.messages.append({"role": "user", "content": self.prompt})

        self.process()

    def handle_response(self, response):
        """
        Handle the response from the agent.
        Args:
            response (openai.ChatCompletion): The response from the agent.
        Returns:
            str: The content of the response message.
        """
        response = response.choices[0]
        agent_message = response.message.content

        self.messages.append(response.message)

        ##########
        # import pprint
        # print(response_1)
        # pprint.pprint(response_1.to_dict())
        print("Response:", response)
        print("Agent Message:", agent_message)
        ##########

        ### TOOL USAGE EXAMPLE
        tool_calls = response.message.tool_calls

        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call.function.name

                tool_args = json.loads(tool_call.function.arguments)

                # Look up the correct tool locally, and call it with the provided arguments
                # Other tools can be added without changing the agentic loop
                tool_response = TOOL_MAPPING[tool_name](**tool_args)

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        # "content": json.dumps(tool_response),
                        "content": str(tool_response),
                    }
                )

                print(f"Tool call: {tool_name} with args: {tool_args}")
                # print(f"Tool response: {tool_response}")

    def process(self):
        step_1 = (
            "Analyze the user's prompt and determine what files need "
            "to be read. Use the tools to your advantage.\n"
            "The user's prompt is:\n\n"
            f"{self.prompt}"
        )

        completion = self.chat(message=step_1)
        response = self.handle_response(completion)
        print(response)

        # TESTING
        step_2 = (
            "Analyze the file contents and determine the intent of the user.\n"
            "Develop a plan to address the user's request.\n"
        )
        completion = self.chat(message=step_2)
        response = self.handle_response(completion)
        print(response)

        # step_3 = (
        #     "Generate code to address the user's request.\n"
        #     "Write the new code in a file with the name 'new_code.py'.\n"
        # )
        # completion = self.chat(message=step_3)
        # response = self.handle_response(completion)
        # print(response)

    def chat(self, message=None):
        if message:
            self.messages.append({"role": "user", "content": message})

        request = {
            "model": self.model_string,
            "temperature": self.temperature,
            "tools": source_agent.tools.tools,
            "tool_choice": "auto",
            "messages": self.messages,
        }

        response = self.session.chat.completions.create(**request)

        return response

    def greet(self):
        return f"Hello, I am {self.model_string}."


# Resources
# - https://openrouter.ai/docs/features/tool-calling
# - https://openrouter.ai/docs/api-reference/overview
