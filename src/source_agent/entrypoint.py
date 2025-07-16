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
    PROVIDER_KEYS = {
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

    PROVIDER_BASE_URLS = {
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

    provider_key = PROVIDER_KEYS.get(provider_name.lower())
    if not provider_key:
        raise ValueError(f"Unknown provider: {provider_name}")

    api_key = os.getenv(provider_key)
    if not api_key:
        raise ValueError(f"Missing API key for provider: {provider_name}")

    base_url = PROVIDER_BASE_URLS.get(provider_name.lower())
    if not base_url:
        raise ValueError(f"Missing base URL for provider: {provider_name}")

    return api_key, base_url


def dispatch_agent(
    prompt: str,
    provider: str = "openrouter",
    model: str = "moonshotai/kimi-k2",
    temperature: float = 0.3,
) -> str:
    """
    Dispatch the agent with the given prompt.

    Args:
        prompt: The prompt to send to the agent.
        provider: The AI provider to use.
        model: The model to use.
        temperature: The temperature for the model.

    Returns:
        The response from the agent.

    Raises:
        Exception: If agent execution fails.
    """
    print("Starting Source Agent")
    print(f"Using provider: {provider}, model: {model}, temperature: {temperature}")

    api_key, provider_url = get_provider(provider)

    agent = source_agent.agents.code.CodeAgent(
        api_key=api_key,
        base_url=provider_url,
        model=model,
        prompt=prompt,
        temperature=temperature,
    )

    result = agent.run()
    print("Agent execution completed successfully")
    return result


def validate_prompt(prompt: str, max_length: int = 10000) -> str:
    """
    Validate and sanitize the prompt.

    Args:
        prompt: The prompt to validate.

    Returns:
        The validated prompt.

    Raises:
        ValueError: If prompt is invalid.
    """
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("Prompt cannot be empty or whitespace only")

    # Reasonable upper limit
    if len(prompt) > max_length:
        raise ValueError(f"Prompt is too long (max {max_length} characters)")

    return prompt


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

    args = parser.parse_args()

    # if args.verbose:
    #     logging.getLogger().setLevel(logging.DEBUG)

    # Validate prompt
    prompt = validate_prompt(args.prompt)

    # Run agent
    result = dispatch_agent(
        prompt=prompt,
        provider=args.provider,
        model=args.model,
        temperature=args.temperature,
    )

    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
