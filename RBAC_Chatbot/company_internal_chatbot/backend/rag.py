import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from transformers import pipeline

# Load NLP components (Using small model for much faster CPU inference)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
llm_pipeline = pipeline("text2text-generation", model="google/flan-t5-small", max_new_tokens=100)

# Vector DB
client = chromadb.Client()
collection = client.get_or_create_collection(name="company_docs")

role_mapping = {
    "finance": ["finance_report.md", "quarterly_summary.csv"],
    "marketing": ["marketing_analysis.md", "campaign_data.csv"],
    "hr": ["employee_data.csv", "hr_policies.md", "hr_data.csv"],
    "engineering": ["tech_docs.md", "system_architecture.md"],
    "employee": ["general_handbook.md"],
    "employees": ["general_handbook.md"],
    "c_level": "all"
}

def clean_text(text):
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.strip()
    text = " ".join(text.split())
    return text

def chunk_text(text, chunk_size=300):
    from nltk.tokenize import word_tokenize
    try:
        words = word_tokenize(text)
    except LookupError:
        import nltk
        nltk.download('punkt')
        nltk.download('punkt_tab')
        words = word_tokenize(text)
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def assign_metadata(file_name, chunk, role_mapping):
    metadata = {}
    metadata["source_file"] = file_name
    metadata["chunk_text"] = chunk
    metadata["roles"] = []

    for role, files in role_mapping.items():
        if files == "all" or file_name in files:
            metadata["roles"].append(role)
    
    # If no roles matched (maybe file naming mismatch), at least C-level gets it.
    if not metadata["roles"] or metadata["roles"] == ["c_level"]:
        metadata["roles"].append("employee") # fallback for generic documents
    
    return metadata

def load_documents():
    if collection.count() > 0:
        return
    folder = "../data"
    all_chunks_with_metadata = []
    
    for root, _, files in os.walk(folder):
        for file_name in files:
            if file_name.endswith(".md"):
                with open(os.path.join(root, file_name), "r", encoding="utf-8") as f:
                    raw_text = f.read()
                    cleaned_text = clean_text(raw_text)
                    chunks = chunk_text(cleaned_text, chunk_size=300)
                    for chunk in chunks:
                        all_chunks_with_metadata.append(assign_metadata(file_name, chunk, role_mapping))

            elif file_name.endswith(".csv"):
                try:
                    df = pd.read_csv(os.path.join(root, file_name))
                    for col in df.columns:
                        if df[col].dtype == "object":
                            text_for_chunking = " ".join(df[col].dropna().astype(str).tolist())
                            cleaned_text = clean_text(text_for_chunking)
                            chunks = chunk_text(cleaned_text, chunk_size=300)
                            for chunk in chunks:
                                all_chunks_with_metadata.append(assign_metadata(file_name, chunk, role_mapping))
                except Exception as e:
                    print(f"Error reading {file_name}: {e}")

    if not all_chunks_with_metadata:
        return

    ids = []
    embeddings = []
    documents = []
    metadatas = []
    for i, item in enumerate(all_chunks_with_metadata):
        text = item["chunk_text"]
        roles = item["roles"]
        source = item["source_file"]
        
        ids.append(f"chunk_{i}")
        documents.append(text)
        metadatas.append({"roles": ",".join(roles), "source": source})

    embeddings = embedding_model.encode(documents).tolist()
    
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )

def role_based_search(query, user_role, top_k=3):
    user_role = user_role.lower()
    results = collection.query(
        query_texts=[query],
        n_results=top_k * 5
    )
    filtered_docs = []
    if not results or not results["documents"] or not list(results["documents"][0]):
        return filtered_docs

    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        roles = meta["roles"].split(",")
        if user_role in roles or "c_level" in roles:
            filtered_docs.append({
                "document": doc,
                "source": meta["source"],
                "roles": roles
            })
        if len(filtered_docs) == top_k:
            break
    return filtered_docs

def retrieve_and_generate(query, user_role):
    docs = role_based_search(query, user_role, top_k=3)
    if not docs:
        return {"answer": "No relevant documents found for your role or query.", "sources": []}
    
    context = " ".join([d["document"] for d in docs])
    prompt = f"Answer the query based strictly on the context.\nContext: {context}\nQuery: {query}\nAnswer:"
    
    response = llm_pipeline(prompt)
    answer = response[0]['generated_text']
    
    return {"answer": answer, "sources": docs}
