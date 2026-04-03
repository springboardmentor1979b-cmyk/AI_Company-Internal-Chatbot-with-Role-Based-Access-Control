# Cell 0


# Cell 1


# Cell 2


# Cell 3
import pandas as pd
df = pd.read_csv("Fintech-data/HR/hr_data.csv")
df.head(10)

# Cell 4
import pandas as pd
df = pd.read_csv("Fintech-data/HR/hr_data.csv")
df.head(10)

# Cell 5
import os
import pandas as pd

# Cell 6
def clean_text(text):
    # Remove special characters
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.strip()
    # Normalize multiple spaces
    text = " ".join(text.split())
    return text

# Cell 7
folder = "Fintech-data"
for file in os.listdir(folder):
    if file.endswith(".md"):
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            raw_text = f.read()
            cleaned = clean_text(raw_text)
            print(f"--- {file} ---")
            print(cleaned[:300])  # show first 300 chars

# Cell 8
for file in os.listdir(folder):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(folder, file))
        # Apply cleaning to text columns
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(lambda x: clean_text(str(x)))
        print(f"--- {file} ---")
        print(df.head())

# Cell 9
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

# Cell 10
from nltk.tokenize import word_tokenize

def chunk_text(text, chunk_size=300):
    words = word_tokenize(text)
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

# Cell 11
folder = "Fintech-data"
for file in os.listdir(folder):
    if file.endswith(".md"):
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            raw_text = f.read()
            chunks = chunk_text(raw_text, chunk_size=300)
            print(f"--- {file} ---")
            print(f"Total chunks: {len(chunks)}")
            print("Sample chunk:\n", chunks[0][:200])

# Cell 12
for file in os.listdir(folder):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(folder, file))
        for col in df.columns:
            if df[col].dtype == "object":
                text = " ".join(df[col].dropna().astype(str).tolist())
                chunks = chunk_text(text, chunk_size=300)
                print(f"--- {file} ---")
                print(f"Total chunks: {len(chunks)}")
                print("Sample chunk:\n", chunks[0][:200])

# Cell 13
role_mapping = {
    "finance": ["finance_report.md", "quarterly_summary.csv"],
    "marketing": ["marketing_analysis.md", "campaign_data.csv"],
    "hr": ["employee_data.csv", "hr_policies.md"],
    "engineering": ["tech_docs.md", "system_architecture.md"],
    "employees": ["general_handbook.md"],
    "c_level": "all"  # C-Level can access everything
}


# Cell 14
def assign_metadata(file_name, chunk, role_mapping):
    metadata = {}
    metadata["source_file"] = file_name
    metadata["chunk_text"] = chunk
    metadata["roles"] = []

    for role, files in role_mapping.items():
        if files == "all" or file_name in files:
            metadata["roles"].append(role)
    return metadata

# Cell 15


# Cell 16
from sentence_transformers import SentenceTransformer
import chromadb

# Cell 17
model = SentenceTransformer("all-MiniLM-L6-v2")

# Cell 18
client = chromadb.Client()
collection = client.get_or_create_collection(name="company_docs")

# Cell 19
all_chunks_with_metadata = []

for file_name in os.listdir(folder):
    if file_name.endswith(".md"):
        with open(os.path.join(folder, file_name), "r", encoding="utf-8") as f:
            raw_text = f.read()
            cleaned_text = clean_text(raw_text)
            chunks = chunk_text(cleaned_text, chunk_size=300)
            for chunk in chunks:
                all_chunks_with_metadata.append(assign_metadata(file_name, chunk, role_mapping))

    elif file_name.endswith(".csv"):
        df = pd.read_csv(os.path.join(folder, file_name))
        for col in df.columns:
            if df[col].dtype == "object":
                # Join all non-null string values from the column into a single text
                text_for_chunking = " ".join(df[col].dropna().astype(str).tolist())
                cleaned_text = clean_text(text_for_chunking)
                chunks = chunk_text(cleaned_text, chunk_size=300)
                for chunk in chunks:
                    all_chunks_with_metadata.append(assign_metadata(file_name, chunk, role_mapping))

for i, item in enumerate(all_chunks_with_metadata):
    text = item["chunk_text"]
    roles = item["roles"]
    source = item["source_file"]

    embedding = model.encode(text).tolist()

    collection.add(
        ids=[f"chunk_{i}"],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"roles": roles, "source": source}]
    )

# Cell 20
results = collection.query(
    query_texts=["latest quarterly spend"],
    n_results=3
)
print(results)

# Cell 21
def role_based_search(query, user_role, top_k=3):
    # Run semantic search
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    # Filter results by role
    filtered_docs = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        if user_role in meta["roles"] or "c_level" in meta["roles"]:
            filtered_docs.append({
                "document": doc,
                "source": meta["source"],
                "roles": meta["roles"]
            })
    return filtered_docs


# Cell 22
if all_chunks_with_metadata:
    print(all_chunks_with_metadata[0])
else:
    print("The list all_chunks_with_metadata is empty.")

# Cell 23
for item in all_chunks_with_metadata[:5]:
    print(item["source_file"], item["roles"])

# Cell 24
for i, item in enumerate(all_chunks_with_metadata):
    text = item["chunk_text"]
    roles = item["roles"]
    source = item["source_file"]

    embedding = model.encode(text).tolist()

    collection.add(
        ids=[f"chunk_{i}"],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"roles": roles, "source": source}]
    )

# Cell 25
def role_based_search(query, user_role, top_k=3):
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    filtered_docs = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        if user_role in meta["roles"] or "c_level" in meta["roles"]:
            filtered_docs.append({
                "document": doc,
                "source": meta["source"],
                "roles": meta["roles"]
            })
    return filtered_docs

finance_results = role_based_search("latest quarterly spend", "finance")
print(finance_results)

# Cell 27


