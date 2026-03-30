from backend.rag_pipeline import query_rag

print("--- Querying for HR data as Finance User ---")
res = query_rag("What are the employee salaries or what is in hr_data.csv?", "Finance")
for s in res['sources']:
    print("Source:", s)
print("Answer:", res['answer'])
