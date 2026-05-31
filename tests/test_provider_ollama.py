import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.factory import ProviderFactory
from prompt_architect.providers.ollama import OllamaProvider


def test_ollama_provider_name():
    provider = OllamaProvider()
    assert provider.provider_name == "ollama"


def test_ollama_constructor_defaults():
    provider = OllamaProvider()
    assert provider.base_url == "http://localhost:11434"
    assert provider.model == "llama3"


def test_ollama_constructor_with_config():
    provider = OllamaProvider(
        config={"base_url": "http://custom:8080", "model": "mistral"}
    )
    assert provider.base_url == "http://custom:8080"
    assert provider.model == "mistral"


class TestOllamaExecute:
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
        mock_resp.read.return_value = json.dumps({"response": "Hi there!"}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OllamaProvider()
        result = provider.execute(self.template, self.context)

        assert result == "Hi there!"

    @patch("urllib.request.urlopen")
    def test_execute_sends_correct_request(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OllamaProvider()
        provider.execute(self.template, self.context)

        call_args = mock_urlopen.call_args
        assert call_args is not None
        req = call_args[0][0]
        assert req.get_method() == "POST"
        assert req.full_url == "http://localhost:11434/api/generate"
        assert req.headers["Content-type"] == "application/json"

        body = json.loads(req.data)
        assert body["model"] == "llama3"
        assert body["prompt"] == "Hello World!"
        assert body["stream"] is False

    @patch("urllib.request.urlopen")
    def test_execute_connection_error_raises_runtime_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        provider = OllamaProvider()
        with pytest.raises(RuntimeError, match="Failed to connect to Ollama"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_empty_response_raises_runtime_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"response": ""}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OllamaProvider()
        with pytest.raises(RuntimeError, match="empty response"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_with_custom_config(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"response": "ok"}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OllamaProvider(
            config={"base_url": "http://localhost:8080", "model": "codellama"}
        )
        provider.execute(self.template, self.context)

        req = mock_urlopen.call_args[0][0]
        assert "localhost:8080" in req.full_url
        body = json.loads(req.data)
        assert body["model"] == "codellama"


def test_factory_creates_ollama_provider():
    factory = ProviderFactory()
    provider = factory.get_provider("ollama")
    assert isinstance(provider, OllamaProvider)
    assert provider.provider_name == "ollama"
    assert provider.base_url == "http://localhost:11434"


def test_factory_ollama_in_list():
    factory = ProviderFactory()
    assert "ollama" in factory.list_supported_providers()
