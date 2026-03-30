from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

VECTOR_DB_DIR = "vectorstore"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)

filter_dict = {"allow_Finance": True}
# Search through langchain
retrieved_docs = vectorstore.similarity_search(
    "technology architecture",
    k=10,
    filter=filter_dict
)

print("Total matches via Langchain:", len(retrieved_docs))

departments = set()
for doc in retrieved_docs:
    departments.add(doc.metadata.get('department'))
print("Langchain departments returned:", departments)
