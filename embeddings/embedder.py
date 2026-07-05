"""Embedding model wrapper. Defaults to a local sentence-transformers model so
the RAG pipeline works without any external API key."""
from functools import lru_cache

from config.settings import settings


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return model.encode(texts, show_progress_bar=False).tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
