from backend.rag_pipeline import query_rag

with open("rag_test_results.txt", "w") as f:
    f.write("--- Querying as Finance User ---\n")
    res = query_rag("What are the internal HR policies?", "Finance")
    for s in res['sources']:
        f.write(f"Source: {s}\n")
    f.write(f"Answer: {res['answer']}\n")

    f.write("\n--- Querying as HR User ---\n")
    res2 = query_rag("What are the internal HR policies?", "HR")
    for s in res2['sources']:
        f.write(f"Source: {s}\n")
    f.write(f"Answer: {res2['answer']}\n")
