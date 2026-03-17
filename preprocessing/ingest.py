import os
import chromadb
from vector_db.search_engine import load_embedding_model

# -----------------------------------
# PATH CONFIG
# -----------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")
CHROMA_PATH = os.path.join(PROJECT_ROOT, "chroma_storage")

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="company_documents")

embedding_model = load_embedding_model()

# -----------------------------------
# CHUNK FUNCTION
# -----------------------------------

def chunk_text(text, chunk_size=500):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

doc_id = 0

# -----------------------------------
# INGEST FILES
# -----------------------------------

for root, dirs, files in os.walk(DATA_FOLDER):
    for filename in files:
        if filename.endswith(".md"):

            file_path = os.path.join(root, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # -----------------------------------
            # ROLE MAPPING
            # -----------------------------------

            if "finance" in filename.lower():
                metadata = {
                    "source": filename,
                    "department": "Finance",
                    "allowed_roles": ["Finance"],
                    "sensitivity": "High"
                }

            elif "hr" in filename.lower():
                metadata = {
                    "source": filename,
                    "department": "HR",
                    "allowed_roles": ["HR"],
                    "sensitivity": "Medium"
                }

            elif "marketing" in filename.lower():
                metadata = {
                    "source": filename,
                    "department": "Marketing",
                    "allowed_roles": ["Marketing"],
                    "sensitivity": "Medium"
                }

            elif "engineering" in filename.lower():
                metadata = {
                    "source": filename,
                    "department": "Engineering",
                    "allowed_roles": ["Engineering"],
                    "sensitivity": "Medium"
                }

            else:
                # General employee handbook
                metadata = {
                    "source": filename,
                    "department": "General",
                    "allowed_roles": ["Employee"],
                    "sensitivity": "Low"
                }

            # -----------------------------------
            # CHUNK & STORE
            # -----------------------------------

            chunks = chunk_text(content)

            for chunk in chunks:
                embedding = embedding_model.encode(
                    chunk,
                    normalize_embeddings=True
                ).tolist()

                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    ids=[f"doc_{doc_id}"]
                )

                doc_id += 1

print("Documents ingested successfully.")