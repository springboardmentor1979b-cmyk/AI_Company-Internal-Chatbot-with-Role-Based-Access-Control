from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.create_collection("docs")

docs = [
    {"text": "Finance report Q1 revenue is 10M", "role": "finance"},
    {"text": "HR policy: 2 days leave per month", "role": "hr"},
]

for i, d in enumerate(docs):
    emb = model.encode(d["text"]).tolist()
    collection.add(
        embeddings=[emb],
        documents=[d["text"]],
        metadatas=[{"role": d["role"]}],
        ids=[str(i)]
    )

def query_rag(query, role):
    q_emb = model.encode(query).tolist()
    results = collection.query(query_embeddings=[q_emb], n_results=2)

    filtered = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        if role == "c_level" or meta["role"] == role:
            filtered.append(doc)

    return filtered if filtered else ["Access denied or no data"]