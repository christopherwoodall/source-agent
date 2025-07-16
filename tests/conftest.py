import pytest

@pytest.fixture(autouse=True)
def isolate_env(monkeypatch):
    """
    Automatically isolate environment for every test.
    Clears all known API keys from env.
    """
    keys = [
        "XAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_VERTEX_API_KEY", "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", "MISTRAL_API_KEY", "DEEPSEEK_API_KEY",
        "CEREBRAS_API_KEY", "GROQ_API_KEY", "VERCEL_API_KEY", "OPENROUTER_API_KEY"
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)
