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
        prompt=None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        self.temperature = temperature
        # self.top_p = 0.98
        # self.frequency_penalty = 0.0005
        # self.presence_penalty = 0.0005

        self.messages = []
        self.prompt = prompt
        self.system_prompt = Path("AGENTS.md").read_text(encoding="utf-8")
        self.user_prompt = (
            "You are a helpful code assistant. Think step-by-step and use tools when needed.\n"
            "Stop when you have completed your analysis.\n"
            f"The user's prompt is:\n\n{self.prompt}"
        )

        # Initialize system and user messages
        self.messages.append({"role": "system", "content": self.system_prompt})
        self.messages.append({"role": "user", "content": self.user_prompt})

        # Load tools from the registry
        self.tools = source_agent.tools.tool_registry.registry.get_tools()
        self.tool_mapping = source_agent.tools.tool_registry.registry.get_mapping()

        # Initialize session
        self.session = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def run(self, max_steps=50):
        for step in range(max_steps):
            print(f"🔄 Agent iteration {step}/{max_steps}")

            response = self.call_llm(self.messages)

            choice = response.choices[0]
            message = choice.message
            self.messages.append(message)

            print("🤖 Agent:", message.content)

            # If the agent is using a tool, run it and loop again
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    print(f"🔧 Calling: {tool_call.function.name}")
                    print(f"📝 Args: {tool_call.function.arguments}")

                    result = self.handle_tool_call(tool_call)
                    self.messages.append(result)

                    print(f"✅ Result: {result}")

                    # Check if this was the task completion tool
                    if tool_call.function.name == "task_mark_complete":
                        print("💯 Task marked complete!")
                        return result
            else:
                print("💭 Agent responded without tool calls - continuing loop")

            print(f"\n{'-'*40}\n")

        print(
            "🚨 Max steps reached without task completion"
            " - consider refining the prompt or tools."
        )

        return {"error": "Max steps reached without task completion."}

    def handle_tool_call(self, tool_call):
        try:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name in self.tool_mapping:
                func = self.tool_mapping[tool_name]
                result = func(**tool_args)
            else:
                # print(f"❌ Function {tool_name} not found")
                result = {"error": f"Unknown tool: {tool_name}"}

            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(result),
            }

        except Exception as e:
            # print(f"❌ Error executing tool {tool_name}: {str(e)}")
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
