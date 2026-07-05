"""ChromaDB-backed vector store for the travel knowledge base."""
import glob
import os

from config.settings import settings
from embeddings.embedder import embed_query, embed_texts

COLLECTION_NAME = "vita_knowledge_base"


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


class KnowledgeBase:
    """Loads travel documents, embeds them, and supports similarity search."""

    def __init__(self, persist_dir: str = None, documents_dir: str = None):
        import chromadb

        self.persist_dir = persist_dir or settings.chroma_persist_dir
        self.documents_dir = documents_dir or settings.documents_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(COLLECTION_NAME)

    def is_indexed(self) -> bool:
        return self.collection.count() > 0

    def index_documents(self, force: bool = False) -> int:
        if self.is_indexed() and not force:
            return self.collection.count()
        if force:
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(COLLECTION_NAME)

        ids, docs, metadatas = [], [], []
        for path in sorted(glob.glob(os.path.join(self.documents_dir, "*.md"))):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            for i, chunk in enumerate(_chunk_text(text)):
                ids.append(f"{os.path.basename(path)}-{i}")
                docs.append(chunk)
                metadatas.append({"source": os.path.basename(path)})

        if not docs:
            return 0

        embeddings = embed_texts(docs)
        self.collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)
        return len(docs)

    def similarity_search(self, query: str, k: int = 3) -> list[dict]:
        if not self.is_indexed():
            self.index_documents()
        query_embedding = embed_query(query)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=k)
        hits = []
        for doc, meta in zip(results.get("documents", [[]])[0], results.get("metadatas", [[]])[0]):
            hits.append({"text": doc, "source": meta.get("source", "unknown")})
        return hits
