import os


def get(provider_name: str = "openrouter") -> tuple[str, str]:
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
