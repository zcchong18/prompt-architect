import os
from unittest.mock import patch

import pytest

from prompt_architect.providers.config import Settings
from prompt_architect.providers.factory import ProviderFactory


class TestSettingsDefaults:
    def test_default_provider_is_mock(self):
        settings = Settings()
        assert settings.default_provider == "mock"

    def test_openai_defaults(self):
        settings = Settings()
        assert settings.openai_api_key == ""
        assert settings.openai_model == "gpt-4o"

    def test_anthropic_defaults(self):
        settings = Settings()
        assert settings.anthropic_api_key == ""
        assert settings.anthropic_model == "claude-sonnet-4-20250514"

    def test_ollama_defaults(self):
        settings = Settings()
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "llama3"

    def test_embedding_defaults(self):
        settings = Settings()
        assert settings.openai_embedding_model == "text-embedding-3-small"
        assert settings.openai_embedding_dim == 1536

    def test_judge_defaults(self):
        settings = Settings()
        assert settings.judge_provider == "mock"
        assert settings.judge_model == "gpt-4o"

    def test_gemini_defaults(self):
        settings = Settings()
        assert settings.gemini_api_key == ""
        assert settings.gemini_model == "gemini-2.0-flash"

    def test_llamacpp_defaults(self):
        settings = Settings()
        assert settings.llamacpp_base_url == "http://localhost:8080"
        assert settings.llamacpp_model == "default"

    def test_for_provider_mock_returns_empty(self):
        settings = Settings()
        assert settings.for_provider("mock") == {}

    def test_for_provider_openai(self):
        settings = Settings()
        config = settings.for_provider("openai")
        assert "api_key" in config
        assert "model" in config
        assert config["model"] == "gpt-4o"

    def test_for_provider_unknown_returns_empty(self):
        settings = Settings()
        assert settings.for_provider("nonexistent") == {}


class TestSettingsFromEnv:
    @patch.dict(
        os.environ,
        {
            "PROMPT_ARCHITECT_DEFAULT_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test-key",
            "OPENAI_MODEL": "gpt-4o-mini",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "ANTHROPIC_MODEL": "claude-opus-4-20250514",
            "OLLAMA_BASE_URL": "http://custom:8080",
            "OLLAMA_MODEL": "mistral",
        },
        clear=True,
    )
    def test_reads_all_env_vars(self):
        settings = Settings()
        assert settings.default_provider == "openai"
        assert settings.openai_api_key == "sk-test-key"
        assert settings.openai_model == "gpt-4o-mini"
        assert settings.anthropic_api_key == "sk-ant-test"
        assert settings.anthropic_model == "claude-opus-4-20250514"
        assert settings.ollama_base_url == "http://custom:8080"
        assert settings.ollama_model == "mistral"

    @patch.dict(os.environ, {}, clear=True)
    def test_falls_back_to_defaults_when_unset(self):
        settings = Settings()
        assert settings.default_provider == "mock"
        assert settings.openai_api_key == ""
        assert settings.ollama_base_url == "http://localhost:11434"


class TestFactoryConfigPassthrough:
    def test_factory_passes_settings_config_to_provider(self):
        settings = Settings()
        factory = ProviderFactory(settings=settings)
        provider = factory.get_provider("mock")
        assert provider._config == {}

    def test_factory_merges_override_config(self):
        settings = Settings()
        factory = ProviderFactory(settings=settings)
        provider = factory.get_provider("mock", config={"custom": "value"})
        assert provider._config == {"custom": "value"}

    def test_factory_default_settings_no_env(self):
        factory = ProviderFactory()
        provider = factory.get_provider("mock")
        assert provider._config == {}
