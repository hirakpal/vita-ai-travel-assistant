"""Central configuration loaded from environment variables or Streamlit secrets."""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """Reads a config value from the environment first, then falls back to
    Streamlit's secrets store (st.secrets) when running under Streamlit."""
    value = os.getenv(key)
    if value:
        return value
    try:
        import streamlit as st

        return st.secrets.get(key, default)
    except Exception:
        return default


def _infer_llm_provider() -> str:
    explicit = _get_secret("LLM_PROVIDER")
    if explicit:
        return explicit
    if _get_secret("OPENAI_API_KEY"):
        return "openai"
    if _get_secret("ANTHROPIC_API_KEY"):
        return "anthropic"
    if _get_secret("GOOGLE_API_KEY"):
        return "gemini"
    if _get_secret("OPENROUTER_API_KEY"):
        return "openrouter"
    return "openai"


def _infer_llm_model(provider: str) -> str:
    explicit = _get_secret("LLM_MODEL")
    if explicit:
        return explicit
    return {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-sonnet-5",
        "gemini": "gemini-1.5-flash",
        "openrouter": "openai/gpt-4o-mini",
    }.get(provider, "gpt-4o-mini")


@dataclass(frozen=True)
class Settings:
    llm_provider: str = field(default_factory=_infer_llm_provider)
    llm_model: str = field(default_factory=lambda: _infer_llm_model(_infer_llm_provider()))

    openai_api_key: str = field(default_factory=lambda: _get_secret("OPENAI_API_KEY"))
    google_api_key: str = field(default_factory=lambda: _get_secret("GOOGLE_API_KEY"))
    anthropic_api_key: str = field(default_factory=lambda: _get_secret("ANTHROPIC_API_KEY"))
    openrouter_api_key: str = field(default_factory=lambda: _get_secret("OPENROUTER_API_KEY"))
    google_maps_api_key: str = field(default_factory=lambda: _get_secret("GOOGLE_MAPS_API_KEY"))

    embedding_provider: str = field(default_factory=lambda: _get_secret("EMBEDDING_PROVIDER", "sentence_transformers"))
    embedding_model: str = field(default_factory=lambda: _get_secret("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))

    chroma_persist_dir: str = field(default_factory=lambda: _get_secret("CHROMA_PERSIST_DIR", "vectordb/store"))
    documents_dir: str = field(default_factory=lambda: _get_secret("DOCUMENTS_DIR", "documents"))


settings = Settings()
