import sys
import argparse

# https://docs.python.org/3/library/readline.html
import source_agent


def run_prompt_mode(agent, prompt) -> str:
    """
    Dispatch the agent with the given prompt.

    Args:
        agent: The agent instance to run.
        prompt: The prompt to provide to the agent.

    Returns:
        The response from the agent.
    """
    user_prompt = (
        "You are a helpful code assistant. Think step-by-step and use tools when needed.\n"
        "Stop when you have completed your thoughts.\n"
        f"The user's prompt is:\n\n{prompt}"
    )

    return agent.run(user_prompt=user_prompt)


def run_interactive_mode(agent):
    print(
        """
🧠 Entering interactive mode.
💡 Type your prompt and press ↵.

    Type ':exit' to quit,
         ':reset' to start fresh
         ':help' for commands.
        """
    )

    system_prompt = agent.system_prompt
    history = []

    while True:
        try:
            user_input = input("🗣️  You > ").strip()

            if not user_input:
                continue

            if user_input.lower() in (":help", "?"):
                print(
                    """
🔧 Available commands:
  :exit      Quit the session
  :history   Show conversation history
  :reset     Clear conversation history
  :help      Show this help message
                """
                )
                continue

            if user_input.lower() in ("q", ":exit"):
                print("👋 Exiting interactive session.")
                break

            if user_input.lower() == ":history":
                print("📜 Conversation History:")
                for i, msg in enumerate(history, 1):
                    print(f"{i}. {msg}")
                continue

            if user_input.lower() == ":reset":
                print("🔄 Conversation history reset.")
                agent.messages = [{"role": "system", "content": system_prompt}]
                history.clear()
                continue

            # Update message history
            agent.messages.append({"role": "user", "content": user_input})

            history.append(f"User: {user_input}")

            print("🤖 Thinking...\n")
            response = agent.run()

            if response:
                print(f"\n🤖 Agent > {response.strip()}\n")

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Session interrupted. Exiting.")
            break


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
        help="Run in interactive step-through mode",
    )

    args = parser.parse_args()

    # if args.verbose:
    #     # Logging setup?
    #     pass

    api_key, base_url = source_agent.providers.get(args.provider)
    agent = source_agent.agents.code.CodeAgent(
        api_key=api_key,
        base_url=base_url,
        model=args.model,
        temperature=args.temperature,
    )

    if args.interactive:
        # Run in interactive mode
        run_interactive_mode(agent)

    else:
        # Let the agent run autonomously
        run_prompt_mode(agent=agent, prompt=args.prompt)

    return 0


if __name__ == "__main__":
    sys.exit(main())
