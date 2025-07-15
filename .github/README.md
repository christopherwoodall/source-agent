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
A simple coding agent.

## How it Works
**Source Agent** operates as a stateless entity, guided by clear directives and external context. Its behavior is primarily defined by **`AGENTS.md`**, which serves as the core system prompt. **`CHANGELOG.md`** provides essential historical context and sense-making rationale. 

![](docs/example.gif)

---

## Usage
**Installation**
```bash
git clone https://github.com/christopherwoodall/source-agent
cd source-agent
pip install --editable ".[developer]"
```

**Basic usage**
```bash
export OPENROUTER_API_KEY=your_key
source-agent --prompt "Analyze this code base"
```

**Advanced usage**
```bash
source-agent --provider "openai" --model "gpt-4o"  --temperature 0.3
```

## Core Architecture
- **Entry Point**: `src/source_agent/entrypoint.py` - CLI interface with argument parsing
- **Agent Engine**: `src/source_agent/agents/code.py` - OpenAI-compatible client with tool integration
- **System Prompt**: `AGENTS.md` - Defines agent behavior, roles, and constraints
