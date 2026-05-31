import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.factory import ProviderFactory
from prompt_architect.providers.gemini import GeminiProvider


def test_gemini_provider_name():
    provider = GeminiProvider()
    assert provider.provider_name == "gemini"


def test_gemini_constructor_defaults():
    provider = GeminiProvider()
    assert provider.api_key == ""
    assert provider.model == "gemini-2.0-flash"


def test_gemini_constructor_with_config():
    provider = GeminiProvider(
        config={"api_key": "AIza-test", "model": "gemini-2.5-pro"}
    )
    assert provider.api_key == "AIza-test"
    assert provider.model == "gemini-2.5-pro"


class TestGeminiExecute:
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
            {"candidates": [{"content": {"parts": [{"text": "Hi there!"}]}}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = GeminiProvider(config={"api_key": "AIza-test"})
        result = provider.execute(self.template, self.context)

        assert result == "Hi there!"

    @patch("urllib.request.urlopen")
    def test_execute_sends_correct_request(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = GeminiProvider(config={"api_key": "AIza-test"})
        provider.execute(self.template, self.context)

        call_args = mock_urlopen.call_args
        assert call_args is not None
        req = call_args[0][0]
        assert req.get_method() == "POST"
        assert "generativelanguage.googleapis.com" in req.full_url
        assert "key=AIza-test" in req.full_url
        assert req.headers["Content-type"] == "application/json"

        body = json.loads(req.data)
        assert body["contents"] == [{"parts": [{"text": "Hello World!"}]}]

    @patch("urllib.request.urlopen")
    def test_execute_connection_error_raises_runtime_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        provider = GeminiProvider(config={"api_key": "AIza-test"})
        with pytest.raises(RuntimeError, match="Failed to connect to Gemini"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_no_candidates_raises_runtime_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"candidates": []}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = GeminiProvider(config={"api_key": "AIza-test"})
        with pytest.raises(RuntimeError, match="no candidates"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_empty_parts_raises_runtime_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(
            {"candidates": [{"content": {"parts": []}}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = GeminiProvider(config={"api_key": "AIza-test"})
        with pytest.raises(RuntimeError, match="empty parts"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_empty_text_raises_runtime_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": ""}]}}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = GeminiProvider(config={"api_key": "AIza-test"})
        with pytest.raises(RuntimeError, match="empty text"):
            provider.execute(self.template, self.context)

    @patch("urllib.request.urlopen")
    def test_execute_with_custom_model(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = GeminiProvider(
            config={"api_key": "AIza-custom", "model": "gemini-2.5-pro"}
        )
        provider.execute(self.template, self.context)

        req = mock_urlopen.call_args[0][0]
        assert "gemini-2.5-pro" in req.full_url


def test_factory_creates_gemini_provider():
    factory = ProviderFactory()
    provider = factory.get_provider("gemini")
    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name == "gemini"


def test_factory_gemini_in_list():
    factory = ProviderFactory()
    assert "gemini" in factory.list_supported_providers()
