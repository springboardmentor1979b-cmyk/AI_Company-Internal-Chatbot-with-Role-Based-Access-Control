import os
import pandas as pd
from langchain_community.document_loaders import TextLoader, CSVLoader, UnstructuredMarkdownLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = "data/Fintech-data"
VECTOR_DB_DIR = "vectorstore"

# Define access mapping
ROLE_MAPPINGS = {
    "Finance": ["Finance", "C-Level"],
    "HR": ["HR", "C-Level"],
    "engineering": ["Engineering", "C-Level"],
    "marketing": ["Marketing", "C-Level"],
    "general": ["Employee", "Finance", "HR", "Marketing", "Engineering", "C-Level"]
}

def process_documents():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # We will collect all Document objects here
    all_docs = []
    
    # Set up text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Iterate through folders
    for folder_name in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, folder_name)
        if not os.path.isdir(folder_path) or folder_name.startswith("."):
            continue
            
        allowed_roles = ROLE_MAPPINGS.get(folder_name, ["C-Level"])
        # In Chroma, metadata values must be str, int, float, or bool. 
        # A list cannot be directly stored. We can store it as a comma-separated string
        # and do exact matches or 'contains' checks if Chroma supports it, 
        # but Chroma's $in operator works by checking if a single metadata field's value is IN a provided list.
        # Wait, Chroma allows filtering where a single property is $in a list: `{"role": {"$in": ["Finance"]}}`.
        # However, if a document has MULTIPLE allowed roles, Chroma doesn't natively support "array overlaps" natively well in simple filters without complex queries.
        # So we can create multiple boolean fields: `allow_Finance`: True, `allow_HR`: True, etc.
        
        metadata_roles = {f"allow_{role}": True for role in allowed_roles}
        
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            
            # Load content
            if file.endswith(".md") or file.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                try:
                    docs = loader.load()
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
                    continue
            elif file.endswith(".csv"):
                loader = CSVLoader(file_path)
                docs = loader.load()
            elif file.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                docs = loader.load()
            else:
                continue
                
            # Chunking
            chunks = text_splitter.split_documents(docs)
            
            # Assign metadata
            for chunk in chunks:
                chunk.metadata["source_document"] = file
                chunk.metadata["department"] = folder_name
                # Add boolean roles for easier filtering in ChromaDB
                for key, val in metadata_roles.items():
                    chunk.metadata[key] = val
                    
                all_docs.append(chunk)
                
    print(f"Total chunks created: {len(all_docs)}")
    
    # Ingest into VectorDB
    if all_docs:
        print("Ingesting into ChromaDB...")
        vectorstore = Chroma.from_documents(
            documents=all_docs,
            embedding=embeddings,
            persist_directory=VECTOR_DB_DIR
        )
        print("Ingestion complete!")

if __name__ == "__main__":
    process_documents()
