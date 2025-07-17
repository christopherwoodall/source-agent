import pytest
from source_agent.providers import get, PROVIDERS


def test_valid_provider(monkeypatch):
    """
    Test that a valid provider returns the correct API key and base URL.
    """
    monkeypatch.setenv("OPENROUTER_API_KEY", "testkey123")
    api_key, base_url = get("openrouter")
    assert api_key == "testkey123"
    assert base_url == "https://openrouter.ai/api/v1"


def test_invalid_provider_name():
    """
    Test that an unknown provider raises a ValueError with suggestions.
    """
    with pytest.raises(ValueError) as excinfo:
        get("notaprovider")

    assert "Unknown provider" in str(excinfo.value)
    for name in PROVIDERS:
        assert name in str(excinfo.value)


def test_missing_api_key(monkeypatch):
    """
    Test that a missing environment variable raises a ValueError.
    """
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError) as excinfo:
        get("openrouter")

    assert "Missing API key for provider" in str(excinfo.value)
    assert "OPENROUTER_API_KEY" in str(excinfo.value)


@pytest.mark.parametrize("provider", PROVIDERS.keys())
def test_all_providers_have_valid_config(provider):
    """
    Sanity test: all configured providers must have non-empty env_var and base_url.
    """
    config = PROVIDERS[provider]
    assert isinstance(config.env_var, str) and config.env_var
    assert isinstance(config.base_url, str) and config.base_url.startswith("http")
