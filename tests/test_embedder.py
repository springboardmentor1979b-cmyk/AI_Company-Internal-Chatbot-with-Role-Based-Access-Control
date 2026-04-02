from backend.rag.embedder import EmbeddingModel

embedder = EmbeddingModel()

text = "Revenue increased by 12 percent in Q3."

embedding = embedder.embed_text(text)

print("Embedding dimension:", len(embedding))
print("First 10 values:", embedding[:10])