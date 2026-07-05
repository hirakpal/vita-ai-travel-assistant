"""Retrieval-Augmented Generation helper: fetches relevant knowledge chunks."""
from vectordb.chroma_store import KnowledgeBase

_kb: KnowledgeBase | None = None


def get_knowledge_base() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
        _kb.index_documents()
    return _kb


def retrieve_context(query: str, k: int = 3) -> str:
    if not query:
        return ""
    hits = get_knowledge_base().similarity_search(query, k=k)
    if not hits:
        return ""
    return "\n\n".join(f"[{h['source']}] {h['text']}" for h in hits)
