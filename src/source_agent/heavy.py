import argparse
import os
import json
import yaml
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from source_agent.agents.code import CodeAgent


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


class TaskOrchestrator:
    def __init__(
        self,
        config_path: str = "config.yaml",
        provider: str = "openrouter",
        model: str = "moonshotai/kimi-k2",
        temperature: float = 0.3,
        silent: bool = False,
    ):
        # load orchestrator config
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["orchestrator"]

        self.num_agents = self.config["parallel_agents"]
        self.task_timeout = self.config["task_timeout"]
        self.aggregation_strategy = self.config.get("aggregation_strategy", "consensus")
        self.silent = silent

        # prepare agent factory args
        api_key, base_url = get_provider(provider)
        self.agent_kwargs = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
            "temperature": temperature,
        }

        # thread-safe progress & results
        self.progress_lock = threading.Lock()
        self.agent_progress: Dict[int, str] = {}
        self.agent_results: Dict[int, str] = {}

    def _make_agent(self) -> CodeAgent:
        """Instantiate a fresh CodeAgent for a subtask."""
        agent = CodeAgent(**self.agent_kwargs)
        if self.silent:
            # suppress internal prints by redirecting stdout temporarily
            import sys, io
            agent._print = print
            agent._stdout_backup = sys.stdout
            sys.stdout = io.StringIO()
        return agent

    def decompose_task(self, user_input: str, num_agents: int) -> List[str]:
        """Use AI to generate N sub‑prompts for parallel agents."""
        question_agent = self._make_agent()

        template = self.config["question_generation_prompt"]
        prompt = template.format(user_input=user_input, num_agents=num_agents)

        # remove the task‐complete tool if present
        question_agent.tools = [
            t for t in question_agent.tools
            if getattr(t, "function", {}).get("name") != "task_mark_complete"
        ]
        question_agent.tool_mapping = {
            name: fn for name, fn in question_agent.tool_mapping.items()
            if name != "task_mark_complete"
        }

        try:
            raw = question_agent.run(prompt)
            questions = json.loads(raw.strip())
            if len(questions) != num_agents:
                raise ValueError(f"expected {num_agents} questions, got {len(questions)}")
            return questions
        except Exception:
            # fallback simple templates
            variations = [
                f"Research comprehensive information about: {user_input}",
                f"Analyze and provide insights about: {user_input}",
                f"Find alternative perspectives on: {user_input}",
                f"Verify and cross-check facts about: {user_input}",
            ]
            return variations[:num_agents]

    def update_agent_progress(self, agent_id: int, status: str, result: str = None):
        with self.progress_lock:
            self.agent_progress[agent_id] = status
            if result is not None:
                self.agent_results[agent_id] = result

    def run_agent_parallel(self, agent_id: int, subtask: str) -> Dict[str, Any]:
        """Execute one CodeAgent on the given subtask."""
        try:
            self.update_agent_progress(agent_id, "PROCESSING")
            agent = self._make_agent()

            start = time.time()
            response = agent.run(subtask)
            duration = time.time() - start

            self.update_agent_progress(agent_id, "COMPLETED", response)
            return {
                "agent_id": agent_id,
                "status": "success",
                "response": response,
                "execution_time": duration,
            }
        except Exception as e:
            return {
                "agent_id": agent_id,
                "status": "error",
                "response": f"Error: {e}",
                "execution_time": 0.0,
            }

    def aggregate_results(self, results: List[Dict[str, Any]]) -> str:
        """Combine all agent outputs into one final answer."""
        successes = [r for r in results if r["status"] == "success"]
        if not successes:
            return "All agents failed—please try again."

        responses = [r["response"] for r in successes]
        if self.aggregation_strategy == "consensus":
            return self._aggregate_consensus(responses)
        # future strategies can go here
        return self._aggregate_consensus(responses)

    def _aggregate_consensus(self, responses: List[str]) -> str:
        """Use a final AI call to synthesize all successful agent responses."""
        if len(responses) == 1:
            return responses[0]

        synth_agent = self._make_agent()
        # strip out all tools to force plain completion
        synth_agent.tools = []
        synth_agent.tool_mapping = {}

        header = []
        for i, resp in enumerate(responses, start=1):
            header.append(f"=== AGENT {i} RESPONSE ===\n{resp}\n")
        all_text = "\n".join(header)

        template = self.config["synthesis_prompt"]
        prompt = template.format(
            num_responses=len(responses),
            agent_responses=all_text,
        )

        try:
            return synth_agent.run(prompt)
        except Exception as e:
            # fallback to concatenation
            fallback = []
            for i, resp in enumerate(responses, start=1):
                fallback.append(f"=== AGENT {i} ===")
                fallback.append(resp)
                fallback.append("")
            return "\n".join(fallback)

    def get_progress_status(self) -> Dict[int, str]:
        with self.progress_lock:
            return dict(self.agent_progress)

    def orchestrate(self, user_input: str) -> str:
        """Top-level entry: decompose, run in parallel, aggregate."""
        # reset
        self.agent_progress.clear()
        self.agent_results.clear()

        # 1) task decomposition
        subtasks = self.decompose_task(user_input, self.num_agents)
        for idx in range(self.num_agents):
            self.agent_progress[idx] = "QUEUED"

        # 2) parallel execution
        results: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=self.num_agents) as exe:
            futures = {
                exe.submit(self.run_agent_parallel, idx, subtasks[idx]): idx
                for idx in range(self.num_agents)
            }
            for fut in as_completed(futures, timeout=self.task_timeout):
                try:
                    results.append(fut.result())
                except Exception as e:
                    idx = futures[fut]
                    results.append({
                        "agent_id": idx,
                        "status": "timeout",
                        "response": f"Agent {idx} timed out: {e}",
                        "execution_time": self.task_timeout,
                    })

        # sort + aggregate
        results.sort(key=lambda r: r["agent_id"])
        return self.aggregate_results(results)


def main() -> int:
    parser = argparse.ArgumentParser(description="Parallel task orchestrator")
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="The user query to orchestrate across agents"
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="config.yaml",
        help="Path to YAML config file (default: config.yaml)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openrouter",
        help="AI provider to use (must match entrypoint providers)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="moonshotai/kimi-k2",
        help="Model name to use for all agents"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Sampling temperature for all agents"
    )
    parser.add_argument(
        "--parallel_agents",
        type=int,
        help="Override number of parallel agents from config"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        help="Override per-task timeout (seconds) from config"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress intermediate agent logs"
    )
    args = parser.parse_args()

    orchestrator = TaskOrchestrator(
        config_path=args.config,
        provider=args.provider,
        model=args.model,
        temperature=args.temperature,
        silent=args.silent
    )

    # optional overrides
    if args.parallel_agents:
        orchestrator.num_agents = args.parallel_agents
    if args.timeout:
        orchestrator.task_timeout = args.timeout

    print("🔍 Decomposing and running tasks in parallel...")
    final = orchestrator.orchestrate(args.prompt)
    print("\n🎯 Final aggregated result:\n")
    print(final)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
