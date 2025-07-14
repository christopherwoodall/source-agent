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

        self.run()

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def send(self):
        return self.session.chat.completions.create(
            model=self.model_string,
            temperature=self.temperature,
            tools=source_agent.tools.plugins.registry.get_tools(),
            tool_choice="auto",
            messages=self.messages,
        )

    def run(self):
        # steps = [
        #     (
        #         "Analyze the user's prompt and determine what files need to be read.\n"
        #         f"The user's prompt is:\n\n{self.prompt}"
        #     ),
        #     (
        #         "Analyze the file contents and determine the intent of the user.\n"
        #         "Develop a plan to address the user's request."
        #     ),
        # ]
        # for step in steps:
        #     self.run_step(step)
        prompt = (
            "You are a helpful code assistant. Think step-by-step and use tools when needed.\n"
            "Stop when you have completed your analysis and clearly state you're done using the token <done>.\n"
            f"The user's prompt is:\n\n{self.prompt}"
        )
        self.think_loop(prompt)

    def think_loop(self, initial_prompt, max_steps=20):
        self.add_message("user", initial_prompt)

        # while True:
        for _ in range(max_steps):
            print("Thinking...")
            # self.add_message("assistant", "Thinking...")
            response = self.send()
            choice = response.choices[0]
            message = choice.message

            self.messages.append(message)
            print("Agent:", message.content)

            # If the agent is using a tool, run it and loop again
            if message.tool_calls:
                self.run_tools_from_response(message.tool_calls)
                continue

            # Stop when the model decides it's done thinking
            if self.should_stop(message.content):
                break

    def should_stop(self, content: str):
        return any(
            stop_token in content.lower()
            for stop_token in ["<done>", "all tasks complete", "finished", "complete"]
        )

    def run_step(self, message):
        self.add_message("user", message)
        response = self.send()
        self.handle_response(response)

    def handle_response(self, response):
        choice = response.choices[0]
        msg = choice.message
        self.messages.append(msg)
        print("Agent:", msg.content)

        if msg.tool_calls:
            self.run_tools_from_response(msg.tool_calls)

    def run_tools_from_response(self, tool_calls):
        mapping = source_agent.tools.plugins.registry.get_mapping()

        for call in tool_calls:
            tool_name = call.function.name
            tool_args = json.loads(call.function.arguments)
            result = mapping[tool_name](**tool_args)

            self.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": tool_name,
                    "content": json.dumps(result),
                }
            )

            print(f"Tool '{tool_name}' called with args: {tool_args}")
