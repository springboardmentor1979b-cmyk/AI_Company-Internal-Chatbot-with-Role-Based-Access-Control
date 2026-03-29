import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH  = os.path.join(PROJECT_ROOT, "chroma_storage")

_client     = None
_collection = None
_ef         = None


def get_ef():
    """Singleton embedding function — loaded once at warmup."""
    global _ef
    if _ef is None:
        _ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    return _ef


def get_collection():
    """Singleton ChromaDB collection — lazy-loaded, persisted to disk."""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name="company_documents",
            embedding_function=get_ef(),
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def is_authorized(user_role: str, allowed_roles_raw) -> bool:
    """Check if user role is permitted to see a chunk."""
    if user_role == "C-Level":
        return True
    if isinstance(allowed_roles_raw, list):
        roles = allowed_roles_raw
    else:
        # Stored as comma-separated string in ChromaDB metadata
        roles = [r.strip() for r in str(allowed_roles_raw).split(",") if r.strip()]
    return user_role in roles


def secure_semantic_search(query: str, user_role: str, top_k: int = 3) -> list:
    """
    Run a cosine-similarity search then RBAC-filter results.
    Fetches top_k * 4 candidates to ensure enough pass the role filter.
    Returns up to top_k authorized documents with similarity scores.
    """
    try:
        collection = get_collection()
        if collection.count() == 0:
            return []

        candidates = min(top_k * 4, collection.count())
        results = collection.query(
            query_texts=[query],
            n_results=candidates,
            include=["documents", "metadatas", "distances"]
        )

        authorized = []
        docs  = results.get("documents",  [[]])[0]
        metas = results.get("metadatas",  [[]])[0]
        dists = results.get("distances",  [[]])[0]

        for doc, meta, dist in zip(docs, metas, dists):
            allowed = meta.get("allowed_roles", "")
            if is_authorized(user_role, allowed):
                authorized.append({
                    "document":         doc,
                    "metadata":         meta,
                    "similarity_score": round(1 - dist, 4)
                })
            if len(authorized) >= top_k:
                break

        return authorized

    except Exception as e:
        print(f"⚠️ ChromaDB search error: {e}")
        return []
