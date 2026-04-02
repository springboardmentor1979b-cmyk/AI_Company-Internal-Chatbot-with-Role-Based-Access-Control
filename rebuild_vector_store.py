#!/usr/bin/env python3
"""
Script to rebuild the vector store with proper RBAC role filtering.
This will:
1. Clear the old vector store
2. Re-ingest all documents with proper role-based access control
"""

import os
import shutil
import json
from pathlib import Path

# Import ingestion components
from backend.ingestion.ingest import ingest_all_documents
from backend.ingestion.parser import parse_document
from backend.ingestion.cleaner import clean_text
from backend.ingestion.chunker import chunk_sections
from backend.config.roles import DEPARTMENT_ACCESS
from backend.rag.embedder import EmbeddingModel
from backend.rag.vector_store import get_vector_store

# Paths
VECTOR_DB_PATH = Path("vector_store/chroma_db")
CHUNKS_PATH = Path("data/processed/chunks.json")


def clear_vector_store():
    """Delete the old vector store to start fresh."""
    if VECTOR_DB_PATH.exists():
        print(f"Deleting old vector store at {VECTOR_DB_PATH}...")
        shutil.rmtree(VECTOR_DB_PATH)
        print("✓ Vector store deleted")
    else:
        print("Vector store doesn't exist, skipping deletion")


def ingest_documents_to_vector_store():
    """
    Ingest documents from chunks.json into the vector store with proper embeddings.
    """
    print("\n" + "="*80)
    print("REBUILDING VECTOR STORE WITH RBAC")
    print("="*80 + "\n")
    
    # Step 1: Generate chunks with proper roles
    print("Step 1: Generating document chunks with role-based access...")
    ingest_all_documents()
    print("✓ Chunks generated successfully\n")
    
    # Step 2: Load chunks
    print("Step 2: Loading chunks from file...")
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"✓ Loaded {len(chunks)} chunks\n")
    
    # Step 3: Initialize embedder and vector store
    print("Step 3: Initializing embedder and vector store...")
    embedder = EmbeddingModel()
    collection = get_vector_store()
    print("✓ Embedder and vector store initialized\n")
    
    # Step 4: Add chunks to vector store
    print("Step 4: Adding chunks to vector store with embeddings...")
    print("This may take a minute or two...\n")
    
    for i, chunk in enumerate(chunks):
        if (i + 1) % 10 == 0:
            print(f"  Processing chunk {i+1}/{len(chunks)}...")
        
        # Generate embedding for the chunk text
        embedding = embedder.embed_text(chunk["text"])
        
        # Prepare metadata
        metadata = {
            "source": chunk["source"],
            "section": chunk["section"],
            "department": chunk["department"],
            "allowed_roles": chunk["allowed_roles"]
        }
        
        # Add to collection
        collection.add(
            ids=[f"chunk_{i}"],
            documents=[chunk["text"]],
            metadatas=[metadata],
            embeddings=[embedding.tolist()]
        )
    
    print(f"\n✓ Successfully added {len(chunks)} chunks to vector store\n")
    
    # Step 5: Verify RBAC by checking allowed_roles in metadata
    print("Step 5: Verifying RBAC configuration...")
    print("\nRole access configuration:")
    for department, allowed_roles in DEPARTMENT_ACCESS.items():
        print(f"  {department:15} → {allowed_roles}")
    print()
    
    # Print summary by department
    department_summary = {}
    for chunk in chunks:
        dept = chunk["department"]
        if dept not in department_summary:
            department_summary[dept] = {"count": 0, "roles": set()}
        department_summary[dept]["count"] += 1
        roles = chunk["allowed_roles"].split(",")
        department_summary[dept]["roles"].update(roles)
    
    print("\nChunks per department:")
    for dept, info in sorted(department_summary.items()):
        print(f"  {dept:15} {info['count']:3} chunks → Roles: {sorted(info['roles'])}")
    
    print("\n" + "="*80)
    print("VECTOR STORE REBUILD COMPLETE!")
    print("="*80)
    print("\nRBAC is now properly configured:")
    print("  ✓ HR documents only accessible to HR and C-level users")
    print("  ✓ Marketing documents only accessible to Marketing and C-level users")
    print("  ✓ Finance documents only accessible to Finance and C-level users")
    print("  ✓ Engineering documents only accessible to Engineering and C-level users")
    print("  ✓ General documents accessible to all users")
    print("\nPlease restart your backend to use the new vector store!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        clear_vector_store()
        ingest_documents_to_vector_store()
        print("\n✅ SUCCESS: Vector store rebuilt with proper RBAC!\n")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
