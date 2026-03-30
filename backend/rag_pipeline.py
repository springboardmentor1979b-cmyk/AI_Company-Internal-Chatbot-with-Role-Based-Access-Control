import os
from langchain_community.vectorstores import Chroma #type: ignore
from langchain_community.embeddings import HuggingFaceEmbeddings #type: ignore
from langchain_huggingface import HuggingFaceEndpoint  # type: ignore
from langchain_core.prompts import PromptTemplate #type: ignore
from dotenv import load_dotenv #type: ignore

load_dotenv()

VECTOR_DB_DIR = "vectorstore"

# Initialize embeddings globally to avoid reloading
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize ChromaDB. Vector DB must exist (created via utils/data_processor.py)
if os.path.exists(VECTOR_DB_DIR):
    vectorstore = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
else:
    vectorstore = None

# Initialize LLM
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if hf_token:
    # Use a solid instruction-following model without explicit task to avoid provider restrictions
    llm = HuggingFaceEndpoint(
        repo_id="google/flan-t5-large",
        huggingfacehub_api_token=hf_token,
        temperature=0.1,
        max_new_tokens=512
    )
else:
    # Mock LLM for local quick testing if no key provided
    from langchain_community.llms.fake import FakeListLLM
    llm = FakeListLLM(responses=["Please set HUGGINGFACEHUB_API_TOKEN in .env to enable true LLM generation."])

# Prompt template
system_prompt = (
    "You are a helpful company internal chatbot. Use the following pieces of retrieved "
    "context to answer the user's question. Based your answer strictly on the context below. "
    "If you don't know the answer or the context doesn't contain the information, just say "
    "that you don't have access to that information.\n\n"
    "Context:\n{context}"
)

prompt_template = PromptTemplate.from_template(system_prompt)

def query_rag(query: str, user_role: str):
    """Query the RAG pipeline with role-based filtering."""
    if vectorstore is None:
        return {"answer": "Vector database not found. Please run utils/data_processor.py first.", "sources": []}
        
    # Apply RBAC filtering
    filter_dict = {f"allow_{user_role}": True}
    
    # Direct similarity search instead of chain
    retrieved_docs = vectorstore.similarity_search(
        query,
        k=4,
        filter=filter_dict
    )
    
    # Construct context
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    full_prompt = prompt_template.format(context=context, input=query)
    
    # Call standard LLM invoke
    try:
        answer = llm.invoke(full_prompt)
        answer_text = str(answer).strip()
    except Exception as e:
        answer_text = f"**Warning: Your LLM API Provider returned an error:** `{str(e)}`\n\nHowever, I was still able to retrieve the following relevant information securely for your role:\n\n{context}"
    
    # Extract sources
    sources = []
    for doc in retrieved_docs:
        source_doc = doc.metadata.get("source_document", "Unknown")
        department = doc.metadata.get("department", "Unknown")
        sources.append(f"{source_doc} ({department})")
            
    # Deduplicate sources
    sources = list(set(sources))
    
    return {
        "answer": answer_text,
        "sources": sources
    }
