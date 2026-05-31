import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.factory import ProviderFactory
from prompt_architect.providers.openai import OpenAIProvider


def test_openai_provider_name():
    provider = OpenAIProvider()
    assert provider.provider_name == "openai"


def test_openai_constructor_defaults():
    provider = OpenAIProvider()
    assert provider.api_key == ""
    assert provider.model == "gpt-4o"
    assert provider.base_url == "https://api.openai.com/v1"


def test_openai_constructor_with_config():
    provider = OpenAIProvider(
        config={
            "api_key": "sk-test",
            "model": "gpt-4o-mini",
            "base_url": "https://custom.example.com/v1",
        }
    )
    assert provider.api_key == "sk-test"
    assert provider.model == "gpt-4o-mini"
    assert provider.base_url == "https://custom.example.com/v1"


class TestOpenAIExecute:
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
            {"choices": [{"message": {"content": "Hi there!"}}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OpenAIProvider(config={"api_key": "sk-test"})
        result = provider.execute(self.template, self.context)

        assert result == "Hi there!"

    @patch("urllib.request.urlopen")
    def test_execute_sends_correct_request(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "ok"}}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OpenAIProvider(config={"api_key": "sk-test"})
        provider.execute(self.template, self.context)

        call_args = mock_urlopen.call_args
        assert call_args is not None
        req = call_args[0][0]
        assert req.get_method() == "POST"
        assert req.full_url == "https://api.openai.com/v1/chat/completions"
        assert req.headers["Authorization"] == "Bearer sk-test"
        assert req.headers["Content-type"] == "application/json"

        body = json.loads(req.data)
        assert body["model"] == "gpt-4o"
        assert body["messages"] == [{"role": "user", "content": "Hello World!"}]

    @patch("urllib.request.urlopen")
    def test_execute_connection_error_raises_runtime_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        provider = OpenAIProvider(config={"api_key": "sk-test"})
        with pytest.raises(RuntimeError, match="Failed to connect to OpenAI"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_empty_choices_raises_runtime_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"choices": []}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OpenAIProvider(config={"api_key": "sk-test"})
        with pytest.raises(RuntimeError, match="empty choices"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_empty_content_raises_runtime_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(
            {"choices": [{"message": {"content": ""}}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OpenAIProvider(config={"api_key": "sk-test"})
        with pytest.raises(RuntimeError, match="empty content"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_with_custom_config(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "ok"}}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OpenAIProvider(
            config={
                "api_key": "sk-custom",
                "model": "gpt-4-turbo",
                "base_url": "https://custom.example.com/v1",
            }
        )
        provider.execute(self.template, self.context)

        req = mock_urlopen.call_args[0][0]
        assert "custom.example.com" in req.full_url
        body = json.loads(req.data)
        assert body["model"] == "gpt-4-turbo"


def test_factory_creates_openai_provider():
    factory = ProviderFactory()
    provider = factory.get_provider("openai")
    assert isinstance(provider, OpenAIProvider)
    assert provider.provider_name == "openai"


def test_factory_openai_in_list():
    factory = ProviderFactory()
    assert "openai" in factory.list_supported_providers()
