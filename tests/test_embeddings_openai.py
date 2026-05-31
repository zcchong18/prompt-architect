import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from prompt_architect.embeddings.openai import OpenAIEmbeddingProvider


def test_openai_embedding_provider_name():
    provider = OpenAIEmbeddingProvider(api_key="sk-test")
    assert provider.provider_name == "openai"


def test_openai_embedding_defaults():
    provider = OpenAIEmbeddingProvider()
    assert provider.api_key == ""
    assert provider.model == "text-embedding-3-small"
    assert provider.vector_dim == 1536


def test_openai_embedding_custom_config():
    provider = OpenAIEmbeddingProvider(
        api_key="sk-test", model="text-embedding-3-large", vector_dim=3072
    )
    assert provider.api_key == "sk-test"
    assert provider.model == "text-embedding-3-large"
    assert provider.vector_dim == 3072


@patch("urllib.request.urlopen")
def test_embed_text_returns_embedding(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    fake_embedding = [0.1, 0.2, 0.3]
    mock_resp.read.return_value = json.dumps(
        {
            "data": [{"embedding": fake_embedding, "index": 0}],
            "model": "text-embedding-3-small",
            "usage": {},
        }
    ).encode()
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    provider = OpenAIEmbeddingProvider(api_key="sk-test")
    result = provider.embed_text("Hello World")

    assert result == [0.1, 0.2, 0.3]


@patch("urllib.request.urlopen")
def test_embed_text_sends_correct_request(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(
        {"data": [{"embedding": [0.1], "index": 0}]}
    ).encode()
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    provider = OpenAIEmbeddingProvider(api_key="sk-test")
    provider.embed_text("Hello World")

    req = mock_urlopen.call_args[0][0]
    assert req.get_method() == "POST"
    assert req.full_url == "https://api.openai.com/v1/embeddings"
    assert req.headers["Authorization"] == "Bearer sk-test"

    body = json.loads(req.data)
    assert body["input"] == "Hello World"
    assert body["model"] == "text-embedding-3-small"


@patch("urllib.request.urlopen")
def test_embed_text_connection_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

    provider = OpenAIEmbeddingProvider(api_key="sk-test")
    with pytest.raises(RuntimeError, match="Failed to connect to OpenAI Embedding"):
        provider.embed_text("Hello")


@patch("urllib.request.urlopen")
def test_embed_text_no_data(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({"data": []}).encode()
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    provider = OpenAIEmbeddingProvider(api_key="sk-test")
    with pytest.raises(RuntimeError, match="no data"):
        provider.embed_text("Hello")


@patch("urllib.request.urlopen")
def test_embed_text_empty_embedding(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(
        {"data": [{"embedding": [], "index": 0}]}
    ).encode()
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    provider = OpenAIEmbeddingProvider(api_key="sk-test")
    with pytest.raises(RuntimeError, match="empty embedding"):
        provider.embed_text("Hello")
