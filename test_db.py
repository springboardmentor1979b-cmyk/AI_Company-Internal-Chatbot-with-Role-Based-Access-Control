from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

VECTOR_DB_DIR = "vectorstore"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)

filter_dict = {"allow_Finance": True}
# Just get the collection directly to see all docs that match this filter
docs = vectorstore._collection.get(where=filter_dict)

print("Total matches for allow_Finance=True:", len(docs['ids']))

# Print a sampling of the departments for these matches
departments = set()
for meta in docs['metadatas']:
    departments.add(meta.get('department'))
print("Departments matched:", departments)
