import os
import sys
import logging
import argparse
import source_agent
from typing import Optional


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
DEFAULT_PROVIDER = os.getenv("SOURCE_AGENT_PROVIDER", "moonshotai")
DEFAULT_MODEL = os.getenv("SOURCE_AGENT_MODEL", "kimi-k2")
DEFAULT_TEMPERATURE = float(os.getenv("SOURCE_AGENT_TEMPERATURE", "0.3"))


def validate_environment() -> None:
    """Validate that required environment variables are set."""
    if not OPENROUTER_API_KEY:
        logger.error("Missing OPENROUTER_API_KEY environment variable")
        raise ValueError(
            "Missing OPENROUTER_API_KEY environment variable. "
            "Please set it before running the agent."
        )


def dispatch_agent(
    prompt: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> str:
    """
    Dispatch the agent with the given prompt.

    Args:
        prompt: The prompt to send to the agent.
        provider: The AI provider to use (overrides default).
        model: The model to use (overrides default).
        temperature: The temperature for the model (overrides default).

    Returns:
        The response from the agent.

    Raises:
        Exception: If agent execution fails.
    """
    logger.info("Starting Source Agent")

    # Use provided values or fall back to defaults
    provider = provider or DEFAULT_PROVIDER
    model = model or DEFAULT_MODEL
    temperature = temperature or DEFAULT_TEMPERATURE

    logger.info(
        f"Using provider: {provider}, model: {model}, temperature: {temperature}"
    )

    try:
        agent = source_agent.agents.code.CodeAgent(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            provider=provider,
            model=model,
            prompt=prompt,
            temperature=temperature,
        )

        result = agent.run()
        logger.info("Agent execution completed successfully")
        return result

    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}")
        raise


def validate_prompt(prompt: str) -> str:
    """
    Validate and sanitize the prompt.

    Args:
        prompt: The prompt to validate.

    Returns:
        The validated prompt.

    Raises:
        ValueError: If prompt is invalid.
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    prompt = prompt.strip()
    if not prompt:
        raise ValueError("Prompt cannot be empty or whitespace only")

    if len(prompt) > 10000:  # Reasonable upper limit
        raise ValueError("Prompt is too long (max 10000 characters)")

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
        default=DEFAULT_PROVIDER,
        choices=[DEFAULT_PROVIDER, "other_provider"],
        help=f"AI provider to use (default: {DEFAULT_PROVIDER})",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Temperature for the model (default: {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose logging",
    )

    try:
        args = parser.parse_args()

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Validate environment
        validate_environment()

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

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130  # Standard exit code for SIGINT
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
