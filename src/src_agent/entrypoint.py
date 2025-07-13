import os
import argparse

import openai

from pathlib import Path


# TODO - Check args for provider
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
    session = openai.OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )
    
    # model = "openai/gpt-3.5-turbo"
    # model = "moonshotai/kimi-k2"
    # This is free right now.
    model = "moonshotai/kimi-k2:free"
    temperature = 0.7

    messages = []
    system_prompt = Path("AGENTS.md").read_text(encoding="utf-8")

    # message = Path("TASKS.md").read_text(encoding="utf-8")
    message = prompt

    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})


    completion = session.chat.completions.create(
        model=model, messages=messages, temperature=temperature
    )

    response = completion.choices[0].message.content

    messages.append(
        {"role": "assistant", "content": response}
    )

    print(response)
    print("\n---\n")
    print("Messages:"
          f"\n{messages}\n---\n")

    return response


def main():
    parser = argparse.ArgumentParser(
        description="Simple coding agent."
    )
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


# Resources
#  - [Using OpenRouter with Python](https://openrouter.ai/docs/quickstart)
