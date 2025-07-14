import os
import argparse
import source_agent


# TODO - Make this dynamic.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", False)
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY environment variable")


def dispatch_agent(prompt):
    """
    Dispatch the agent with the given prompt.
    Args:
        prompt (str): The prompt to send to the agent.
    Returns:
        str: The response from the agent.
    """
    print("Welcome to the Source Agent!")

    # temperature = 0.7

    provider = "moonshotai"
    model = "kimi-k2"
    # This is free right now.
    # model = "kimi-k2:free"

    # provider = "openai"
    # model = "gpt-3.5-turbo"

    agent = source_agent.agents.code.CodeAgent(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
        provider=provider,
        model=model,
        prompt=prompt,
    )


def main():
    parser = argparse.ArgumentParser(description="Simple coding agent.")
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        default="Analyze this code base.",
        help="Prompt for the coding agent (default: 'Analyze this code base.')",
    )
    args = parser.parse_args()

    prompt = args.prompt

    if not prompt:
        raise ValueError("Prompt cannot be empty")

    return dispatch_agent(prompt)


if __name__ == "__main__":
    main()
