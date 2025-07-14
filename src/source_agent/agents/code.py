import json
import openai
import source_agent
from pathlib import Path


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
                tool_response = source_agent.tools.plugins.registry.get_mapping()[
                    tool_name
                ](**tool_args)

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_response),
                    }
                )

                print(f"Tool call: {tool_name} with args: {tool_args}")
                # print(f"Tool response: {tool_response}")

    def process(self):
        step_1 = (
            "Analyze the user's prompt and determine what files need "
            "to be read. Use the tools to your advantage.\n"
            # "You can think recursively.\n"
            # "Terminate thoughts with a `<stop_thoughts>` tag.\n"
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
            "tools": source_agent.tools.plugins.registry.get_tools(),
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
