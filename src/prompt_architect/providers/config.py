import os
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Settings:
    default_provider: str = field(
        default_factory=lambda: os.environ.get(
            "PROMPT_ARCHITECT_DEFAULT_PROVIDER", "mock"
        )
    )

    openai_api_key: str = field(
        default_factory=lambda: os.environ.get("OPENAI_API_KEY", "")
    )
    openai_model: str = field(
        default_factory=lambda: os.environ.get("OPENAI_MODEL", "gpt-4o")
    )

    anthropic_api_key: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", "")
    )
    anthropic_model: str = field(
        default_factory=lambda: os.environ.get(
            "ANTHROPIC_MODEL", "claude-sonnet-4-20250514"
        )
    )

    ollama_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
    )
    ollama_model: str = field(
        default_factory=lambda: os.environ.get("OLLAMA_MODEL", "llama3")
    )

    gemini_api_key: str = field(
        default_factory=lambda: os.environ.get("GEMINI_API_KEY", "")
    )
    gemini_model: str = field(
        default_factory=lambda: os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    )

    llamacpp_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "LLAMACPP_BASE_URL", "http://localhost:8080"
        )
    )
    llamacpp_model: str = field(
        default_factory=lambda: os.environ.get("LLAMACPP_MODEL", "default")
    )

    openai_embedding_model: str = field(
        default_factory=lambda: os.environ.get(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        )
    )
    openai_embedding_dim: int = field(
        default_factory=lambda: int(os.environ.get("OPENAI_EMBEDDING_DIM", "1536"))
    )

    judge_provider: str = field(
        default_factory=lambda: os.environ.get("PROMPT_ARCHITECT_JUDGE", "mock")
    )
    judge_model: str = field(
        default_factory=lambda: os.environ.get("PROMPT_ARCHITECT_JUDGE_MODEL", "gpt-4o")
    )

    def for_provider(self, name: str) -> Dict[str, str]:
        mapping = {
            "openai": {"api_key": self.openai_api_key, "model": self.openai_model},
            "anthropic": {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
            },
            "ollama": {"base_url": self.ollama_base_url, "model": self.ollama_model},
            "gemini": {"api_key": self.gemini_api_key, "model": self.gemini_model},
            "llamacpp": {
                "base_url": self.llamacpp_base_url,
                "model": self.llamacpp_model,
            },
            "mock": {},
        }
        return mapping.get(name.lower(), {})
