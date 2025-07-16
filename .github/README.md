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
**Source Agent** operates as a stateless entity, guided by clear directives and external context. Its behavior is primarily defined by **`AGENTS.md`**, which serves as the core system prompt. 

![](docs/example.gif)

---

## Prerequisites
- Python 3.10 or higher
- An API key from one of the supported AI providers (see [Supported Providers](#supported-providers))
- Git (for .gitignore support)

---

## Installation
### Quick Start
```bash
# Clone the repository
git clone https://github.com/christopherwoodall/source-agent
cd source-agent

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[developer]"

# Verify the installation
source-agent --help
```

### Basic Usage
```bash
# Analyze the current codebase
source-agent --prompt "Analyze this codebase and identify potential improvements"

# Analyze with specific focus
source-agent --prompt "Review the authentication system for security issues"
```

### Advanced Usage
```bash
# Use OpenAI with GPT-4
source-agent \
  --provider openai \
  --model gpt-4o \
  --temperature 0.1 \
  --prompt "Create unit tests for the utils.py file"

# Use Claude for code review
source-agent \
  --provider anthropic \
  --model claude-3-5-sonnet \
  --prompt "Review the error handling in this codebase"
```

---

## Supported Providers

Source Agent supports multiple AI providers. Set the corresponding environment variable:

| Provider | Environment Variable |
|----------|---------------------|
| OpenRouter | `OPENROUTER_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Google | `GEMINI_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Cerebras | `CEREBRAS_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Vercel | `VERCEL_API_KEY` |
| xAI | `XAI_API_KEY` |

---

## Available Tools
Source Agent provides these built-in tools for code analysis:

- **file_list_tool** - List files/directories in a given path (respects .gitignore)
- **file_read_tool** - Read contents of any file
- **file_write_tool** - Write content to a file (creates/overwrites)
- **file_delete_tool** - Safely delete a file
- **file_search_tool** - Search files by name pattern and optionally search within files using text/regex
- **directory_create_tool** - Create directories (with optional parent creation)
- **directory_delete_tool** - Safely delete directories (recursive option available)
- **calculate_expression** - Evaluate mathematical expressions (supports sqrt, pi, etc.)
- **web_search_tool** - Search the web using DuckDuckGo (returns snippets and optional page content)
- **task_mark_complete** - REQUIRED tool to signal task completion and exit the agent loop

These tools are automatically available to the AI agent during analysis.

---

## Core Architecture
- **Entry Point**: `src/source_agent/entrypoint.py` - CLI interface with argument parsing
- **Agent Engine**: `src/source_agent/agents/code.py` - OpenAI-compatible client with tool integration
- **System Prompt**: `AGENTS.md` - Defines agent behavior, roles, and constraints

### Project Structure

```
source-agent/
├── src/source_agent/
│   ├── entrypoint.py      # CLI interface
│   ├── agents/
│   │   └── code.py        # Main agent logic
│   └── tools/             # File system tools
└── AGENTS.md              # System prompt & behavior rules
```
