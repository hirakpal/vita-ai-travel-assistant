"""Smoke tests that every module imports cleanly (catches missing imports
that unit tests mocking things out could otherwise miss)."""
import importlib

import pytest

# Third-party packages that may not be installed in a lightweight dev/test
# environment; a missing one of these is not a bug in our code.
OPTIONAL_DEPENDENCIES = {"streamlit", "chromadb", "sentence_transformers", "openai", "google", "anthropic"}

MODULES = [
    "config.settings",
    "models.trip",
    "agents.conversation_state",
    "agents.extractor",
    "agents.travel_agent",
    "guardrails.persona",
    "guardrails.conversation_flow",
    "guardrails.transportation",
    "memory.memory_manager",
    "services.llm_client",
    "services.maps_service",
    "services.budget_estimator",
    "services.retrieval_engine",
    "vectordb.chroma_store",
    "embeddings.embedder",
    "ui.chat_panel",
    "ui.itinerary_panel",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_module_imports_cleanly(module_name):
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name in OPTIONAL_DEPENDENCIES or exc.name.split(".")[0] in OPTIONAL_DEPENDENCIES:
            pytest.skip(f"optional dependency not installed: {exc.name}")
        raise


def test_chroma_store_references_are_resolvable():
    """Regression: KnowledgeBase.index_documents/similarity_search call
    embed_texts/embed_query, which must actually be bound at module scope -
    a plain import smoke test wouldn't catch a NameError raised only when
    those functions are called."""
    from vectordb import chroma_store

    assert callable(chroma_store.embed_texts)
    assert callable(chroma_store.embed_query)
