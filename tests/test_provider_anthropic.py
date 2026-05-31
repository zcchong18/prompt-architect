import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.anthropic import AnthropicProvider
from prompt_architect.providers.factory import ProviderFactory


def test_anthropic_provider_name():
    provider = AnthropicProvider()
    assert provider.provider_name == "anthropic"


def test_anthropic_constructor_defaults():
    provider = AnthropicProvider()
    assert provider.api_key == ""
    assert provider.model == "claude-sonnet-4-20250514"
    assert provider.max_tokens == 1024


def test_anthropic_constructor_with_config():
    provider = AnthropicProvider(
        config={
            "api_key": "sk-ant-test",
            "model": "claude-opus-4-20250514",
            "max_tokens": 2048,
        }
    )
    assert provider.api_key == "sk-ant-test"
    assert provider.model == "claude-opus-4-20250514"
    assert provider.max_tokens == 2048


class TestAnthropicExecute:
    def setup_method(self):
        self.template = PromptTemplate(
            name="test",
            template_string="Hello {name}!",
        )
        self.context = {"name": "World"}

    @patch("urllib.request.urlopen")
    def test_execute_returns_response(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(
            {"content": [{"text": "Hi there!"}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = AnthropicProvider(config={"api_key": "sk-ant-test"})
        result = provider.execute(self.template, self.context)

        assert result == "Hi there!"

    @patch("urllib.request.urlopen")
    def test_execute_sends_correct_request(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"content": [{"text": "ok"}]}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = AnthropicProvider(config={"api_key": "sk-ant-test"})
        provider.execute(self.template, self.context)

        call_args = mock_urlopen.call_args
        assert call_args is not None
        req = call_args[0][0]
        assert req.get_method() == "POST"
        assert req.full_url == "https://api.anthropic.com/v1/messages"
        assert req.headers["X-api-key"] == "sk-ant-test"
        assert req.headers["Anthropic-version"] == "2023-06-01"
        assert req.headers["Content-type"] == "application/json"

        body = json.loads(req.data)
        assert body["model"] == "claude-sonnet-4-20250514"
        assert body["max_tokens"] == 1024
        assert body["messages"] == [{"role": "user", "content": "Hello World!"}]

    @patch("urllib.request.urlopen")
    def test_execute_connection_error_raises_runtime_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        provider = AnthropicProvider(config={"api_key": "sk-ant-test"})
        with pytest.raises(RuntimeError, match="Failed to connect to Anthropic"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_empty_content_raises_runtime_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"content": []}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = AnthropicProvider(config={"api_key": "sk-ant-test"})
        with pytest.raises(RuntimeError, match="empty content"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_empty_text_raises_runtime_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"content": [{"text": ""}]}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = AnthropicProvider(config={"api_key": "sk-ant-test"})
        with pytest.raises(RuntimeError, match="empty text"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_with_custom_config(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"content": [{"text": "ok"}]}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = AnthropicProvider(
            config={
                "api_key": "sk-ant-custom",
                "model": "claude-opus-4-20250514",
                "max_tokens": 4096,
            }
        )
        provider.execute(self.template, self.context)

        req = mock_urlopen.call_args[0][0]
        assert "api.anthropic.com" in req.full_url
        body = json.loads(req.data)
        assert body["model"] == "claude-opus-4-20250514"
        assert body["max_tokens"] == 4096


def test_factory_creates_anthropic_provider():
    factory = ProviderFactory()
    provider = factory.get_provider("anthropic")
    assert isinstance(provider, AnthropicProvider)
    assert provider.provider_name == "anthropic"


def test_factory_anthropic_in_list():
    factory = ProviderFactory()
    assert "anthropic" in factory.list_supported_providers()
