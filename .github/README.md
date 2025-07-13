<p align="center">

[![CI][ci-badge]][ci-url]
[![Release][release-badge]][release-url]
[![PyPI Status Badge][pypi-badge]][pypi-url]

</p>

[ci-badge]: https://github.com/christopherwoodall/source-agent/actions/workflows/lint.yaml/badge.svg?branch=main
[ci-url]: https://github.com/christopherwoodall/source-agent/actions/workflows/lint.yml
[pypi-badge]: https://badge.fury.io/py/source-agent.svg
[pypi-url]: https://pypi.org/project/source-agent/
[release-badge]: https://github.com/christopherwoodall/source-agent/actions/workflows/release.yml/badge.svg
[release-url]: https://github.com/christopherwoodall/source-agent/actions/workflows/release.yml

# Source Agent
Simple coding agent.

## How it Works
**Source Agent** operates as a stateless entity, guided by clear directives and external context. Its behavior is primarily defined by **`AGENTS.md`**, which serves as the core system prompt. For current tasks and instructions, it references **`TASKS.md`**, while **`CHANGELOG.md`** provides essential historical context and decision-making rationale. This setup ensures consistent and informed responses without internal memory.

---

## Getting Started

```bash
git clone [https://github.com/christopherwoodall/source-agent](https://github.com/christopherwoodall/source-agent)
cd source-agent
pip install -e ".[developer]"

source-agent --prompt "Analyze the file at src/src_agent/entrypoint.py and suggest any edits."
```

This project uses [OpenRouter](https://openrouter.ai/) to run the agent. You will need to set both the `OPENROUTER_API_KEY` and `OPENROUTER_BASE_URL` environment variables.

```bash
export OPENROUTER_API_KEY=your_api_key_here
export OPENROUTER_BASE_URL=https://api.openrouter.ai/v1
```

---


# Resources
  - [Using OpenRouter with Python](https://openrouter.ai/docs/quickstart)
  - [Agentic Patterns](https://agentic-patterns.com/)
