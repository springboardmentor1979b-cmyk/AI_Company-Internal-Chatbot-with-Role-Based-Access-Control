import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(PROJECT_ROOT, "chroma_storage")
CHUNKS_FILE = os.path.join(PROJECT_ROOT, "vector_db", "processed_chunks.json")


def embed_documents():
    if not os.path.exists(CHUNKS_FILE):
        print(f"❌ processed_chunks.json not found at {CHUNKS_FILE}")
        print("   Run: python -m preprocessing.preprocess_all first")
        return

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        print("❌ No chunks to embed.")
        return

    print(f"📦 Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print(f"🗄️  Connecting to ChromaDB at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Delete and recreate to ensure clean state
    try:
        client.delete_collection("company_documents")
    except Exception:
        pass

    collection = client.create_collection(
        name="company_documents",
        metadata={"hnsw:space": "cosine"}
    )

    print(f"🔢 Embedding {len(chunks)} chunks...")
    batch_size = 32
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]
        embeddings = model.encode(texts, normalize_embeddings=True).tolist()

        # ChromaDB requires metadata values to be str/int/float/bool
        # Convert allowed_roles list to comma-separated string
        metas = []
        for c in batch:
            m = dict(c["metadata"])
            if isinstance(m.get("allowed_roles"), list):
                m["allowed_roles"] = ", ".join(m["allowed_roles"])
            metas.append(m)

        collection.add(
            ids=[c["id"] for c in batch],
            documents=texts,
            embeddings=embeddings,
            metadatas=metas
        )
        print(f"  Embedded {min(i+batch_size, len(chunks))}/{len(chunks)} chunks")

    print(f"✅ Done — {collection.count()} chunks stored in ChromaDB.")


if __name__ == "__main__":
    embed_documents()
