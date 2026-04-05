"""
vector_store.py
───────────────
Wraps ChromaDB:
  • Persistent storage (survives restarts)
  • Embedding via sentence-transformers
  • Role-based semantic search
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from src.config import (
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)


class VectorStore:
    def __init__(self):
        # Persistent client — data survives process restarts
        self._client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        print(f"📦 ChromaDB loaded — {self._collection.count()} docs indexed")
        self._model = SentenceTransformer(EMBEDDING_MODEL)

    # ── Indexing ─────────────────────────────────────────────────

    def add_documents(self, records: list[dict], batch_size: int = 100):
        """
        records: list of {text, metadata}
        metadata must have 'roles' (comma-sep string) and 'source'.
        ChromaDB does NOT accept list values — roles must be a string.
        """
        total = len(records)
        for start in range(0, total, batch_size):
            batch = records[start : start + batch_size]
            texts      = [r["text"]     for r in batch]
            metadatas  = [r["metadata"] for r in batch]
            ids        = [f"chunk_{start + i}" for i in range(len(batch))]
            embeddings = self._model.encode(texts, show_progress_bar=False).tolist()

            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
            print(f"  Indexed {min(start + batch_size, total)}/{total} chunks…")

        print(f"\n✅ Indexing complete. Total in DB: {self._collection.count()}")

    def clear(self):
        """Drop and recreate the collection (use before re-ingesting)."""
        self._client.delete_collection(COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        print("🗑️  Collection cleared.")

    # ── Search ───────────────────────────────────────────────────

    def search(self, query: str, user_role: str, top_k: int = 5) -> list[dict]:
        """
        Semantic search filtered by RBAC.
        Returns list of {document, source, roles, distance}.
        """
        # Look at the top results only to prevent "desperate" context-bleeding
        n_candidates = min(self._collection.count(), top_k * 3) or 1
        user_safe = user_role.lower().strip()

        results = self._collection.query(
            query_embeddings=self._model.encode([query]).tolist(),
            n_results=n_candidates,
            include=["documents", "metadatas", "distances"],
        )

        docs, metas, dists = (
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )

        print(f"\n🔍 SECURITY AUDIT: User '{user_safe}' is querying... (Top {n_candidates} candidates)")
        filtered = []
        for doc, meta, dist in zip(docs, metas, dists):
            allowed_roles = meta.get("roles", "").split(",")
            source = meta.get("source", "unknown")
            
            # Super-user check
            is_super = user_safe in ["c_level", "admin"]
            
            # Match check
            is_authorized = (user_safe in allowed_roles) or ("employees" in allowed_roles) or is_super
            
            if is_authorized:
                print(f"  ✅ [ALLOWED] Source: {source} (Roles: {allowed_roles})")
                filtered.append({
                    "document": doc,
                    "source":   source,
                    "roles":    allowed_roles,
                    "score":    round(1 - dist, 4),
                })
            else:
                print(f"  ❌ [BLOCKED] Source: {source} (Roles: {allowed_roles})")

            if len(filtered) >= top_k:
                break

        return filtered

    def count(self) -> int:
        return self._collection.count()


# Singleton — import this everywhere
_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
