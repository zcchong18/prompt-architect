import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.factory import ProviderFactory
from prompt_architect.providers.llamacpp import LlamaCppProvider


def test_llamacpp_provider_name():
    provider = LlamaCppProvider()
    assert provider.provider_name == "llamacpp"


def test_llamacpp_constructor_defaults():
    provider = LlamaCppProvider()
    assert provider.base_url == "http://localhost:8080"
    assert provider.model == "default"


def test_llamacpp_constructor_with_config():
    provider = LlamaCppProvider(
        config={"base_url": "http://custom:8080", "model": "llama-3.2-3b"}
    )
    assert provider.base_url == "http://custom:8080"
    assert provider.model == "llama-3.2-3b"


class TestLlamaCppExecute:
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

        provider = LlamaCppProvider()
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

        provider = LlamaCppProvider()
        provider.execute(self.template, self.context)

        call_args = mock_urlopen.call_args
        assert call_args is not None
        req = call_args[0][0]
        assert req.get_method() == "POST"
        assert req.full_url == "http://localhost:8080/v1/chat/completions"
        assert req.headers["Content-type"] == "application/json"

        body = json.loads(req.data)
        assert body["model"] == "default"
        assert body["messages"] == [{"role": "user", "content": "Hello World!"}]

    @patch("urllib.request.urlopen")
    def test_execute_connection_error_raises_runtime_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        provider = LlamaCppProvider()
        with pytest.raises(RuntimeError, match="Failed to connect to llama.cpp"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_empty_choices_raises_runtime_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"choices": []}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = LlamaCppProvider()
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

        provider = LlamaCppProvider()
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

        provider = LlamaCppProvider(
            config={"base_url": "http://localhost:8081", "model": "mistral"}
        )
        provider.execute(self.template, self.context)

        req = mock_urlopen.call_args[0][0]
        assert "localhost:8081" in req.full_url
        body = json.loads(req.data)
        assert body["model"] == "mistral"


def test_factory_creates_llamacpp_provider():
    factory = ProviderFactory()
    provider = factory.get_provider("llamacpp")
    assert isinstance(provider, LlamaCppProvider)
    assert provider.provider_name == "llamacpp"


def test_factory_llamacpp_in_list():
    factory = ProviderFactory()
    assert "llamacpp" in factory.list_supported_providers()
