<p align="center">

[![CI][ci-badge]][ci-url]
[![Release][release-badge]][release-url]
[![PyPI Status Badge][pypi-badge]][pypi-url]

</p>

[ci-badge]: https://github.com/christopherwoodall/code-agent/actions/workflows/lint.yaml/badge.svg?branch=main
[ci-url]: https://github.com/christopherwoodall/code-agent/actions/workflows/lint.yml
[pypi-badge]: https://badge.fury.io/py/code-agent.svg
[pypi-url]: https://pypi.org/project/code-agent/
[release-badge]: https://github.com/christopherwoodall/code-agent/actions/workflows/release.yml/badge.svg
[release-url]: https://github.com/christopherwoodall/code-agent/actions/workflows/release.yml


# Code Agent
Simple coding agent.

## How it Works
**Code Agent** operates as a stateless entity, guided by clear directives and external context. Its behavior is primarily defined by **`AGENTS.md`**, which serves as the core system prompt. For current tasks and instructions, it references **`TASKS.md`**, while **`CHANGELOG.md`** provides essential historical context and decision-making rationale. This setup ensures consistent and informed responses without internal memory.

---

## Getting Started

```bash
git clone [https://github.com/christopherwoodall/code-agent](https://github.com/christopherwoodall/code-agent)
cd code-agent
pip install -e ".[developer]"

code-agent
```


## References
- [Using OnepRouter with Python](https://openrouter.ai/docs/quickstart)
- https://agentic-patterns.com/
