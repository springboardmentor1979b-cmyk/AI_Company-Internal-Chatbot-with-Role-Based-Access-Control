try:
    from transformers import pipeline
    print("Transformers imported successfully!")
    qa_pipe = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    
    context = "The reported revenue is $2.3 billion, up 25% YoY, fueled by strong enterprise software sales."
    question = "What is the revenue?"
    
    res = qa_pipe(question=question, context=context)
    print("QA Result:", res)
except Exception as e:
    print(f"Error: {e}")
