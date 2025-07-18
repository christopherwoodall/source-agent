import sys
import json
import argparse
import source_agent


def handle_agent_events(
    agent_events: source_agent.agents.code.AgentEvent, verbose: bool
):
    """
    Handles and prints events yielded by the agent.

    Args:
        agent_events: An iterator yielding AgentEvent objects.
        verbose: If True, prints more detailed information (e.g., tool arguments).
    """
    for event in agent_events:
        if event.type == source_agent.agents.code.AgentEventType.ITERATION_START:
            print("\n" + "-" * 40 + "\n")
            print(f"🔄 Iteration {event.data['step']}/{event.data['max_steps']}")
        elif event.type == source_agent.agents.code.AgentEventType.AGENT_MESSAGE:
            print(f"🤖 Agent: {event.data['content']}")
        elif event.type == source_agent.agents.code.AgentEventType.TOOL_CALL:
            tool_name = event.data["name"]
            tool_args = event.data["arguments"]
            print(f"🔧 Calling: {tool_name}")
            if verbose:
                try:
                    print(f"   Args: {json.dumps(json.loads(tool_args), indent=2)}")
                except json.JSONDecodeError:
                    print(f"   Raw Args: {tool_args}")
        elif event.type == source_agent.agents.code.AgentEventType.TOOL_RESULT:
            tool_name = event.data["name"]
            tool_result = event.data["result"]
            print(f"✅ Tool Result ({tool_name}): {json.dumps(tool_result, indent=2)}")
        elif event.type == source_agent.agents.code.AgentEventType.TASK_COMPLETE:
            # Exit generator iteration as task is complete
            print(f"💯 {event.data['message']}\n")
            return
        elif event.type == source_agent.agents.code.AgentEventType.MAX_STEPS_REACHED:
            print(f"🛑 {event.data['message']}")
        elif event.type == source_agent.agents.code.AgentEventType.ERROR:
            print(f"❌ Error: {event.data['message']}", file=sys.stderr)


def run_prompt_mode(agent, prompt: str, verbose: bool):
    """
    Dispatch the agent with the given prompt in autonomous mode.

    Args:
        agent: The agent instance to run.
        prompt: The prompt to provide to the agent.
        verbose: If True, enables verbose output for agent events.
    """
    user_prompt = (
        "You are a helpful code assistant. Think step-by-step and use tools when needed.\n"
        "Stop when you have completed your thoughts.\n"
        f"The user's prompt is:\n\n{prompt}"
    )

    print("🚀 Running in autonomous mode...")
    agent_events_generator = agent.run(user_prompt=user_prompt)
    handle_agent_events(agent_events_generator, verbose)


def run_interactive_mode(agent, verbose: bool):
    """
    Runs the agent in interactive mode, allowing user input and displaying agent progress.

    Args:
        agent: The agent instance to run.
        verbose: If True, enables verbose output for agent events.
    """
    history = []

    print(
        """
🧠 Entering interactive mode.
💡 Type your prompt and press ↵.

    Type ':exit' to quit,
    Type ':reset' to start fresh,
    Type ':help' for commands.
        """
    )

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
  :history   Show conversation history (local to CLI)
  :reset     Clear conversation history (agent's memory)
  :help      Show this help message
                    """
                )
                continue

            if user_input.lower() in ("q", ":exit"):
                print("👋 Exiting interactive session.")
                break

            if user_input.lower() == ":history":
                print("📜 Conversation History (Local CLI Log):")
                if not history:
                    print("   (No history yet)")
                for i, msg in enumerate(history, 1):
                    print(f"{i}. {msg}")
                continue

            if user_input.lower() == ":reset":
                print("🔄 Conversation history reset (for agent and CLI log).")
                agent.reset_conversation()
                history.clear()
                continue

            # Add user input to CLI history
            history.append(f"User: {user_input}")

            print("🤖 Thinking...\n")

            # Run the agent and iterate over its events
            agent_events_generator = agent.run(user_prompt=user_input)
            for event in agent_events_generator:
                # Print the event using the handler
                handle_agent_events([event], verbose)

                # In interactive mode, we might want to allow deeper interaction.
                # For now, just continue processing.
                # If a "task_complete" event is received, break the loop
                if (
                    event.type == source_agent.agents.code.AgentEventType.TASK_COMPLETE
                    or event.type == source_agent.agents.code.AgentEventType.MAX_STEPS_REACHED
                    or event.type == source_agent.agents.code.AgentEventType.ERROR
                ):
                    break

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Session interrupted. Exiting.")
            break
        except Exception as e:
            print(
                f"An unexpected error occurred in interactive mode: {e}",
                file=sys.stderr,
            )


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
        "-i",
        "--interactive",
        action="store_true",
        default=False,
        help="Run in interactive step-through mode",
    )

    args = parser.parse_args()

    api_key, base_url = source_agent.providers.get(args.provider)
    agent = source_agent.agents.code.CodeAgent(
        api_key=api_key,
        base_url=base_url,
        model=args.model,
        temperature=args.temperature,
    )

    try:
        if args.interactive:
            run_interactive_mode(agent, args.verbose)
        else:
            run_prompt_mode(agent=agent, prompt=args.prompt, verbose=args.verbose)
    except Exception as e:
        print(f"An unhandled error occurred: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
