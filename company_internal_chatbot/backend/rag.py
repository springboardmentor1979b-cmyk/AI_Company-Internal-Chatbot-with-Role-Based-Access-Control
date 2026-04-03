import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DB_DIR = "vector_db"

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DB_DIR)

def init_rag_db():
    client = get_chroma_client()
    
    # Use simple default sentence-transformers model underlying chromadb
    sentence_transformer_ef = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name="company_docs", 
        embedding_function=sentence_transformer_ef
    )
    
    if collection.count() == 0:
        docs = []
        data_dir = "data"
        if os.path.exists(data_dir):
            for role_folder in os.listdir(data_dir):
                role_path = os.path.join(data_dir, role_folder)
                if os.path.isdir(role_path):
                    for filename in os.listdir(role_path):
                        if filename.endswith(".txt"):
                            file_path = os.path.join(role_path, filename)
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            # each line can be a chunk
                            chunks = [line.strip() for line in content.split("\n") if line.strip()]
                            for i, chunk in enumerate(chunks):
                                docs.append((f"{role_folder}_{filename}_{i}", chunk, role_folder, filename))
        
        if docs:
            ids = [doc[0] for doc in docs]
            documents = [doc[1] for doc in docs]
            metadatas = [{"role": doc[2], "source": doc[3]} for doc in docs]
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    print(f"RAG Vector DB initialized with {collection.count()} documents.")

def get_answer(query: str, user_role: str):
    client = get_chroma_client()
    # Default embedding function
    sentence_transformer_ef = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_collection(
        name="company_docs",
        embedding_function=sentence_transformer_ef
    )
    
    # Filter rules: c_level gets access to everything
    # Others: only their department
    if user_role == "c_level":
        where_filter = None  # No filter
    else:
        where_filter = {"role": user_role}
    
    try:
        results = collection.query(
            query_texts=[query],
            n_results=3,
            where=where_filter
        )
    except Exception:
            results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    
    if not docs:
        return {
            "answer": "I don't have enough context to answer that based on your access level.",
            "sources": [],
            "confidence": "Low"
        }
        
    # Generate mock LLM answer strictly based on contexts
    context_str = " ".join(docs)
    answer = f"Based on the retrieved context: {context_str} \n\n(Note: This is an extracted summary mapping to the RAG functionality)"
    
    # Calculate simple confidence mapped from distance
    # lower distance in chroma default L2 = higher confidence
    avg_distance = sum(distances) / len(distances) if distances else 1.5
    if avg_distance < 1.0:
        confidence = "High"
    elif avg_distance < 1.5:
        confidence = "Medium"
    else:
        confidence = "Low"
        
    sources = [meta.get("source", "Unknown") for meta in metadatas]
    
    return {
        "answer": answer,
        "sources": list(set(sources)),
        "confidence": confidence
    }
