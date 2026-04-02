from backend.rag.retriever import Retriever
from backend.rag.llm_client import generate_answer
from backend.config.logger import setup_logger
#import logging
import time



logger = setup_logger()

class RAGPipeline:

    def __init__(self):
        self.retriever = Retriever()

    def run(self, query: str, user_role: str):

        start_time = time.time()

        logger.info(f"User Query: {query}")
        logger.info(f"User Role: {user_role}")

        # Step 1 — Retrieve relevant chunks
        retrieval_start = time.time()

        chunks = self.retriever.search(
            query=query,
            user_role=user_role,
            top_k=5
        )

        retrieval_time = time.time() - retrieval_start
        logger.info(f"Chunks Retrieved: {len(chunks)}")
        logger.info(f"Retrieval Time: {retrieval_time:.3f} seconds")
        sources = list(set([chunk["source"] for chunk in chunks]))
        logger.info(f"Sources Used: {sources}")

        if not chunks:
            return {
                "answer": "No relevant information found.",
                "sources": []
            }

        # Step 2 — Build structured context
        context_blocks = []

        for chunk in chunks:
            block = f"""
            Document: {chunk['source']}
            Section: {chunk.get('section','Unknown')}

            Content:
            {chunk['text']}
            """
            context_blocks.append(block)

        context = "\n\n".join(context_blocks)

        # Step 3 — Build prompt
        prompt = f"""
            You are an internal company AI assistant.

            Answer the user's question using ONLY the provided company documents.

            Context:
            {context}

            Question:
            {query}

            Instructions:
            - Answer clearly.
            - Do NOT invent information.
            - If the answer is not in the context, say you do not have enough information.
            - Cite document sources when possible.
        """

        logger.info("Generating LLM response...")

        # Step 4 — Call LLM
        llm_start = time.time()

        answer = generate_answer(prompt)
        logger.info("LLM response generated successfully")

        llm_time = time.time() - llm_start
        logger.info(f"LLM Generation Time: {llm_time:.3f} seconds")

        # Step 5 — Extract sources
        sources = list(set([chunk["source"] for chunk in chunks]))

        total_time = time.time() - start_time
        logger.info(f"Total Pipeline Time: {total_time:.3f} seconds")

        return {
            "answer": answer,
            "sources": sources
        }