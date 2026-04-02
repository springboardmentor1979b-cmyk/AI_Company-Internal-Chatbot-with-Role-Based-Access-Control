from backend.rag.retriever import Retriever

retriever = Retriever()

query = "What was the revenue growth in Q3?"

results = retriever.search(query, user_role="finance")

for r in results:
    print("\nSOURCE:", r["source"])
    print("SECTION:", r["section"])
    print("TEXT:", r["text"][:200])