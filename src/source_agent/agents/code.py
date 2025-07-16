import re
import json
import time
import openai
import random
import source_agent
from pathlib import Path


class CodeAgent:
    def __init__(
        self,
        api_key=None,
        base_url=None,
        model=None,
        temperature=0.3,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        self.temperature = temperature
        # self.top_p = 0.98
        # self.frequency_penalty = 0.0005
        # self.presence_penalty = 0.0005

        self.messages = []
        self.system_prompt = Path("AGENTS.md").read_text(encoding="utf-8")

        self.messages.append({"role": "system", "content": self.system_prompt})

        # Load tools from the registry
        self.tools = source_agent.tools.tool_registry.registry.get_tools()
        self.tool_mapping = source_agent.tools.tool_registry.registry.get_mapping()

        # Initialize session
        self.session = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def run(self, user_prompt: str = None, max_steps: int = 10):
        """
        If user_prompt is provided, seed it;
        otherwise assume messages already has the last user turn.
        Then run the full react loop to completion.
        """
        if user_prompt is not None:
            self.messages.append({"role": "user", "content": user_prompt})

        for step in range(1, max_steps + 1):
            print(f"🔄 Agent iteration {step}/{max_steps}")
            response = self.call_llm(self.messages)

            choice = response.choices[0]
            message = choice.message
            self.messages.append(message)

            if message.content:
                print("🤖 Agent:", self._parse_message(message.content))

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "msg_complete_tool":
                        print("💯 Task marked complete!\n")
                        return

                    print(f"🔧 Calling: {tool_call.function.name}")

                    result = self.handle_tool_call(tool_call)
                    self.messages.append(result)

            print("-" * 40 + "\n")

        return {"error": "Max steps reached without task completion."}

    def _parse_message(self, message):
        pattern = r"(\{[^}]*'type'\s*:\s*'text'[^}]*\})"
        match = re.search(pattern, message, re.DOTALL)
        try:
            if match:
                message = match.group(0).replace("'", '"')
                message = json.loads(message)["text"]
        except:  # noqa: E722
            pass
        return message

    def handle_tool_call(self, tool_call):
        try:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name in self.tool_mapping:
                func = self.tool_mapping[tool_name]
                result = func(**tool_args)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(result),
            }

        except Exception as e:
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps({"error": f"Tool execution failed: {str(e)}"}),
            }

    def call_llm(
        self,
        messages,
        max_retries: int = 5,
        backoff_base: float = 1.0,
        backoff_factor: float = 2.0,
        max_backoff: float = 60.0,
    ):
        """
        Call the OpenAI chat API, retrying on transient errors
        with exponential backoff and jitter.

        Args:
            messages: the message list to send
            max_retries: how many total attempts (including first)
            backoff_base: initial delay in seconds
            backoff_factor: multiplier for exponential backoff
            max_backoff: cap on backoff delay
        """
        # Notes:
        #  - https://medium.com/@Doug-Creates/nightmares-and-client-chat-completions-create-29ad0acbe16a
        for attempt in range(1, max_retries + 1):
            try:
                return self.session.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=self.temperature,
                    # top_p=self.top_p,
                    # frequency_penalty=self.frequency_penalty,
                    # presence_penalty=self.presence_penalty,
                )
            except (
                openai.Timeout,
                openai.APIError,
                openai.OpenAIError,
                openai.APIStatusError,
                openai.RateLimitError,
                openai.APITimeoutError,
                openai.APIConnectionError,
            ) as e:
                # If we've used up our retries, re‐raise
                if attempt == max_retries:
                    print(f"❌ LLM call failed after {attempt} attempts: {e}")
                    raise
                # Otherwise, back off and retry
                delay = min(
                    backoff_base * (backoff_factor ** (attempt - 1)) + random.random(),
                    max_backoff,
                )
                print(
                    f"⚠️ Attempt {attempt} failed with {type(e).__name__}: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
            except Exception as e:
                # Unexpected exception - do not retry
                print(f"❌ Unexpected error in LLM call: {e}")
                raise
