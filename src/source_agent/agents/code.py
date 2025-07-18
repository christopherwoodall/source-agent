import re
import sys
import json
import time
import openai
import random
import source_agent
from enum import Enum
from typing import Any, Dict, Iterator
from pathlib import Path
from dataclasses import field, dataclass


class AgentEventType(Enum):
    ITERATION_START = "iteration_start"
    AGENT_MESSAGE = "agent_message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TASK_COMPLETE = "task_complete"
    MAX_STEPS_REACHED = "max_steps_reached"
    ERROR = "error"


@dataclass(frozen=True)
class AgentEvent:
    """
    Represents an event occurring during the agent's operation.

    Attributes:
        type: The type of event (e.g., iteration_start, agent_message).
        data: A dictionary containing event-specific data.
    """

    type: AgentEventType
    data: Dict[str, Any] = field(default_factory=dict)


class CodeAgent:
    DEFAULT_SYSTEM_PROMPT_PATH = "AGENTS.md"
    MAX_STEPS = 12
    MAX_RETRIES = 3
    BACKOFF_BASE = 1.0
    BACKOFF_FACTOR = 2.0
    MAX_BACKOFF = 60.0

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
        temperature: float = 0.3,
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

    def run(
        self, user_prompt: str = None, max_steps: int = None
    ) -> Iterator[AgentEvent]:
        """
        Run a full ReAct-style loop with tool usage, yielding events at each step.

        Args:
            user_prompt: Optional user input to start the conversation.
            max_steps: Maximum steps before stopping.

        Yields:
            AgentEvent: An event describing the current state or action of the agent.
        """
        if user_prompt:
            self.messages.append({"role": "user", "content": user_prompt})

        steps = max_steps or self.MAX_STEPS

        for step in range(1, steps + 1):
            yield AgentEvent(
                type=AgentEventType.ITERATION_START,
                data={"step": step, "max_steps": steps},
            )

            try:
                response = self.call_llm(self.messages)
            except Exception as e:
                yield AgentEvent(
                    type=AgentEventType.ERROR,
                    data={
                        "message": f"LLM call failed: {str(e)}",
                        "exception_type": type(e).__name__,
                    },
                )
                return

            message = response.choices[0].message
            self.messages.append(message)

            parsed_content = self.parse_response_message(message.content)
            if parsed_content:
                yield AgentEvent(
                    type=AgentEventType.AGENT_MESSAGE, data={"content": parsed_content}
                )

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    yield AgentEvent(
                        type=AgentEventType.TOOL_CALL,
                        data={
                            "name": tool_name,
                            "arguments": tool_call.function.arguments,
                        },
                    )

                    if tool_name == "msg_complete_tool":
                        yield AgentEvent(
                            type=AgentEventType.TASK_COMPLETE,
                            data={"message": "Task marked complete!"},
                        )
                        return

                    result_message = self.handle_tool_call(tool_call)
                    self.messages.append(result_message)
                    # Attempt to parse tool result content as JSON if it's a string, otherwise use as-is
                    tool_result_content = result_message["content"]
                    try:
                        parsed_tool_result = json.loads(tool_result_content)
                    except (json.JSONDecodeError, TypeError):
                        # Fallback to string representation for complex types
                        parsed_tool_result = tool_result_content

                    yield AgentEvent(
                        type=AgentEventType.TOOL_RESULT,
                        data={"name": tool_name, "result": parsed_tool_result},
                    )

        yield AgentEvent(
            type=AgentEventType.MAX_STEPS_REACHED,
            data={"message": f"Max steps ({steps}) reached without task completion."},
        )

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
            # Ensure result is always JSON serializable for the 'content' field of the tool message
            # This is important for the LLM to process it correctly
            if not isinstance(result, (str, dict, list, int, float, bool, type(None))):
                result = str(result)

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
            openai.OpenAIError: If the API call fails after retries due to an OpenAI-specific error.
            Exception: For any other unexpected errors.
        """
        retries = max_retries or self.MAX_RETRIES
        base = backoff_base or self.BACKOFF_BASE
        factor = backoff_factor or self.BACKOFF_FACTOR
        cap = max_backoff or self.MAX_BACKOFF

        # Define specific OpenAI errors that are generally retryable.
        RETRYABLE_OPENAI_ERRORS = (
            openai.RateLimitError,  # 429 status code
            openai.APITimeoutError,  # Timeout during the API call
            openai.APIConnectionError,  # Network connection issues
            openai.APIStatusError,  # Covers 5xx errors which are often retryable, and also other 4xx errors
        )

        for attempt in range(1, retries + 1):
            try:
                return self.session.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=self.temperature,
                )
            except RETRYABLE_OPENAI_ERRORS as e:
                # This block handles known retryable OpenAI API errors.
                if attempt == retries:
                    print(
                        f"❌ LLM call failed after {attempt} attempts: {e}",
                        file=sys.stderr,
                    )
                    raise  # Re-raise if all retries exhausted

                delay = min(base * (factor ** (attempt - 1)) + random.random(), cap)
                print(
                    f"⚠️  Attempt {attempt} failed: {type(e).__name__}: {e}. "
                    f"Retrying in {delay:.1f}s...",
                    file=sys.stderr,
                )
                time.sleep(delay)

            except openai.OpenAIError as e:
                # This block handles non-retryable OpenAI API errors (e.g., AuthenticationError,
                # PermissionDeniedError, InvalidRequestError, etc.).
                # These typically indicate a problem that retrying won't solve.
                print(
                    f"❌ Non-retryable OpenAI error during LLM call: {e}",
                    file=sys.stderr,
                )
                raise  # Re-raise immediately

            except Exception as e:
                # This block catches any other unexpected Python exceptions.
                print(f"❌ Unexpected error during LLM call: {e}", file=sys.stderr)
                raise
