import os
from typing import Dict
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    env_var: str
    base_url: str


PROVIDERS: Dict[str, ProviderConfig] = {
    "openrouter": ProviderConfig("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
    "openai": ProviderConfig("OPENAI_API_KEY", "https://api.openai.com/v1"),
    "google": ProviderConfig(
        "GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta"
    ),
    "google_vertex": ProviderConfig(
        "GOOGLE_VERTEX_API_KEY", "https://generativelanguage.googleapis.com/v1beta"
    ),
    "anthropic": ProviderConfig("ANTHROPIC_API_KEY", "https://api.anthropic.com/v1"),
    "mistral": ProviderConfig("MISTRAL_API_KEY", "https://api.mistral.ai/v1"),
    "deepseek": ProviderConfig("DEEPSEEK_API_KEY", "https://api.deepseek.com/v1"),
    "cerebras": ProviderConfig("CEREBRAS_API_KEY", "https://api.cerebras.net/v1"),
    "groq": ProviderConfig("GROQ_API_KEY", "https://api.groq.com/v1"),
    "vercel": ProviderConfig("VERCEL_API_KEY", "https://api.vercel.ai/v1"),
    "xai": ProviderConfig("XAI_API_KEY", "https://api.x.ai/v1"),
}


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
    normalized_name = provider_name.lower()
    config = PROVIDERS.get(normalized_name)

    if not config:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(
            f"Unknown provider: '{provider_name}'. Available providers are: {available}"
        )

    api_key = os.getenv(config.env_var)
    if not api_key:
        raise ValueError(
            f"Missing API key for provider '{provider_name}'. "
            f"Set the environment variable: {config.env_var}"
        )

    return api_key, config.base_url
