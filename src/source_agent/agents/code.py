import re
import json
import time
import openai
import random
import source_agent
from pathlib import Path


class CodeAgent:
    DEFAULT_SYSTEM_PROMPT_PATH = "AGENTS.md"
    MAX_STEPS = 12
    MAX_RETRIES = 3
    BACKOFF_BASE = 1.0
    BACKOFF_FACTOR = 2.0
    MAX_BACKOFF = 60.0

    def __init__(
        self,
        api_key=None,
        base_url=None,
        model=None,
        temperature=0.3,
        system_prompt: str = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature

        self.system_prompt = system_prompt or Path(
            self.DEFAULT_SYSTEM_PROMPT_PATH
        ).read_text(encoding="utf-8")
        self.messages = []
        self.reset_conversation()

        self.tools = source_agent.tools.tool_registry.registry.get_tools()
        self.tool_mapping = source_agent.tools.tool_registry.registry.get_mapping()

        self.session = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def reset_conversation(self):
        """Clear conversation and initialize with system prompt."""
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def run(self, user_prompt: str = None, max_steps: int = None):
        """
        Run a full ReAct-style loop with tool usage.

        Args:
            user_prompt: Optional user input to start the conversation.
            max_steps: Maximum steps before stopping.
        """
        if user_prompt:
            self.messages.append({"role": "user", "content": user_prompt})

        steps = max_steps or self.MAX_STEPS

        for step in range(1, steps + 1):
            print(f"🔄 Iteration {step}/{steps}")
            response = self.call_llm(self.messages)

            message = response.choices[0].message
            self.messages.append(message)

            parsed_content = self.parse_response_message(message.content)
            if parsed_content:
                print("🤖 Agent:", parsed_content)

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    print(f"🔧 Calling: {tool_name}")

                    if tool_name == "msg_complete_tool":
                        print("💯 Task marked complete!\n")
                        return

                    result = self.handle_tool_call(tool_call)
                    self.messages.append(result)

            print("-" * 40 + "\n")

        return {"error": "Max steps reached without task completion."}

    def parse_response_message(self, message: str) -> str:
        """
        Extracts clean user-facing content from a model response.
        Assumes OpenAI-style JSON snippets with 'type': 'text'.
        """
        pattern = r"(\{[^}]*'type'\s*:\s*'text'[^}]*\})"
        match = re.search(pattern, message, re.DOTALL)

        if match:
            try:
                message = match.group(0).replace("'", '"')
                return json.loads(message).get("text", "").strip()
            except json.JSONDecodeError:
                pass

        return message.strip()

    def handle_tool_call(self, tool_call):
        """Execute the named tool with arguments, return result as message."""
        try:
            tool_name = tool_call.function.name
            args_raw = tool_call.function.arguments

            try:
                tool_args = json.loads(args_raw)
            except json.JSONDecodeError:
                return self._tool_error(tool_call, "Invalid JSON arguments.")

            func = self.tool_mapping.get(tool_name)
            if not func:
                return self._tool_error(tool_call, f"Unknown tool: {tool_name}")

            result = func(**tool_args)
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(result),
            }

        except Exception as e:
            return self._tool_error(tool_call, f"Tool execution failed: {str(e)}")

    def _tool_error(self, tool_call, error_msg: str):
        """Helper for returning tool execution errors."""
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": json.dumps({"error": error_msg}),
        }

    def call_llm(
        self,
        messages,
        max_retries: int = None,
        backoff_base: float = None,
        backoff_factor: float = None,
        max_backoff: float = None,
    ):
        """
        Call the OpenAI-compatible chat API with retries.

        Args:
            messages: List of messages for the chat API.
            max_retries: Maximum number of retries on failure.
            backoff_base: Base delay for exponential backoff.
            backoff_factor: Factor to increase delay on each retry.
            max_backoff: Maximum delay before giving up.

        Returns:
            The response from the chat API.

        Raises:
            openai.Timeout: If the API call times out.
            openai.APIError: If the API call fails due to an API error.
            openai.OpenAIError: If the API call fails after retries.
            openai.APIStatusError: If the API call fails due to an API status error.
            openai.RateLimitError: If the API call exceeds the rate limit.
            openai.APITimeoutError: If the API call times out.
            openai.APIConnectionError: If the API call fails due to a connection error.
        """
        retries = max_retries or self.MAX_RETRIES
        base = backoff_base or self.BACKOFF_BASE
        factor = backoff_factor or self.BACKOFF_FACTOR
        cap = max_backoff or self.MAX_BACKOFF

        for attempt in range(1, retries + 1):
            try:
                return self.session.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=self.temperature,
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
                if attempt == retries:
                    print(f"❌ LLM call failed after {attempt} attempts: {e}")
                    raise

                delay = min(base * (factor ** (attempt - 1)) + random.random(), cap)
                print(
                    f"⚠️  Attempt {attempt} failed: {type(e).__name__}: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)

            except Exception as e:
                print(f"❌ Unexpected error during LLM call: {e}")
                raise
