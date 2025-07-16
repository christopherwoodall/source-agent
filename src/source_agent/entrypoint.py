import os
import sys
import argparse
import source_agent


# # Configure logging
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)


def get_provider(provider_name: str = "openrouter") -> tuple[str, str]:
    """
    Get the API key and base URL for the specified provider.

    Args:
        provider_name: The name of the AI provider.

    Returns:
        A tuple containing the API key and base URL for the provider.

    Raises:
        ValueError: If the provider is unknown or the API key is missing.
    """
    provider_keys = {
        "xai": "XAI_API_KEY",
        "google": "GEMINI_API_KEY",
        "google_vertex": "GOOGLE_VERTEX_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "cerebras": "CEREBRAS_API_KEY",
        "groq": "GROQ_API_KEY",
        "vercel": "VERCEL_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }

    provider_base_urls = {
        "xai": "https://api.x.ai/v1",
        "google": "https://generativelanguage.googleapis.com/v1beta",
        "google_vertex": "https://generativelanguage.googleapis.com/v1beta",
        "openai": "https://api.openai.com/v1",
        "anthropic": "https://api.anthropic.com/v1",
        "mistral": "https://api.mistral.ai/v1",
        "deepseek": "https://api.deepseek.com/v1",
        "cerebras": "https://api.cerebras.net/v1",
        "groq": "https://api.groq.com/v1",
        "vercel": "https://api.vercel.ai/v1",
        "openrouter": "https://openrouter.ai/api/v1",
    }

    provider_key = provider_keys.get(provider_name.lower())
    if not provider_key:
        raise ValueError(f"Unknown provider: {provider_name}")

    api_key = os.getenv(provider_key)
    if not api_key:
        raise ValueError(f"Missing API key for provider: {provider_name}")

    base_url = provider_base_urls.get(provider_name.lower())
    if not base_url:
        raise ValueError(f"Missing base URL for provider: {provider_name}")

    return api_key, base_url


def dispatch_agent(agent, prompt) -> str:
    """
    Dispatch the agent with the given prompt.

    Args:
        agent: The agent instance to run.
        prompt: The prompt to provide to the agent.

    Returns:
        The response from the agent.
    """
    print("Starting Source Agent")

    user_prompt = (
        "You are a helpful code assistant. Think step-by-step and use tools when needed.\n"
        "Stop when you have completed your analysis.\n"
        f"The user's prompt is:\n\n{prompt}"
    )

    result = agent.run(user_prompt=user_prompt)
    print("Agent execution completed successfully")

    return result


def interactive_session(agent):
    print("Entering interactive mode. Type your prompt and ↵; type 'q' to quit.")
    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() == "q":
            print("Exiting interactive session.")
            return

        # reset the conversation to just the system prompt + the new user prompt
        agent.messages = [{"role": "system", "content": agent.system_prompt}]
        agent.messages.append({"role": "user", "content": user_input})

        # run full react loop
        agent.run()
        print("\n🔚 Run completed.\n")


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = argparse.ArgumentParser(description="Simple coding agent.")
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        default="Analyze this code base.",
        help="Prompt for the coding agent (default: 'Analyze this code base.')",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openrouter",
        choices=[
            "openrouter",
            "openai",
            "google",
            "anthropic",
            "mistral",
            "deepseek",
            "cerebras",
            "groq",
            "vercel",
            "xai",
        ],
        help="AI provider to use (default: openrouter)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="moonshotai/kimi-k2",
        help="Model to use (default: moonshotai/kimi-k2)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Temperature for the model (default: 0.3)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose logging",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        default=False,
        help="Run in interactive step‑through mode",
    )
    parser.add_argument(
        "-h",
        "--heavy",
        action="store_true",
        default=False,
        help="Enable heavy mode",
    )

    args = parser.parse_args()

    # if args.verbose:
    #     logging.getLogger().setLevel(logging.DEBUG)

    api_key, base_url = get_provider(args.provider)
    agent = source_agent.agents.code.CodeAgent(
        api_key=api_key,
        base_url=base_url,
        model=args.model,
        temperature=args.temperature,
    )

    if args.interactive:
        # Run in interactive mode
        return interactive_session(agent)

    else:
        # Let the agent run autonomously
        return dispatch_agent(agent=agent, prompt=args.prompt)


if __name__ == "__main__":
    sys.exit(main())
