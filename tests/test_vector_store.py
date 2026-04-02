from backend.rag.vector_store import get_vector_store

collection = get_vector_store()

print("Vector store initialized successfully.")
print("Current vector count:", collection.count())