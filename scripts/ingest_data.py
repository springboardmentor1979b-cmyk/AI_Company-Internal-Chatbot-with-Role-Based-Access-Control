"""
ingest_data.py
──────────────
Run ONCE (or whenever you update documents):

    python scripts/ingest_data.py

This will:
  1. Clone the GitHub data repo (if not present)
  2. Parse and chunk all .md and .csv files
  3. Generate embeddings and index into ChromaDB
  4. Seed demo user accounts into SQLite
"""

import subprocess
import sys
import os

# Make sure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config import DATA_FOLDER
from src.data_processing.preprocessor import load_all_documents
from src.vector_db.vector_store import get_store
from src.auth.auth_handler import seed_demo_users

REPO_URL = "https://github.com/springboardmentor441p-coderr/Fintech-data"


def clone_data_repo():
    if os.path.exists(DATA_FOLDER):
        print(f"📁 '{DATA_FOLDER}' already exists — skipping clone.")
        return
    print(f"🌐 Cloning data repository from {REPO_URL} …")
    result = subprocess.run(["git", "clone", REPO_URL], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Clone failed:\n", result.stderr)
        sys.exit(1)
    print("✅ Repository cloned successfully.")


def main():
    print("=" * 55)
    print("  Company Chatbot — Data Ingestion Pipeline")
    print("=" * 55)

    # Step 1: Clone data
    clone_data_repo()

    # Step 2: Parse documents
    print("\n📄 Step 2: Parsing and chunking documents…")
    records = load_all_documents(DATA_FOLDER)
    if not records:
        print("⚠️  No documents found. Check your DATA_FOLDER path.")
        sys.exit(1)

    # Step 3: Index into ChromaDB
    print(f"\n🗄️  Step 3: Indexing {len(records)} chunks into ChromaDB…")
    store = get_store()

    if store.count() > 0:
        ans = input(f"⚠️  DB already has {store.count()} docs. Re-index? (y/N): ")
        if ans.strip().lower() == "y":
            store.clear()
        else:
            print("Skipping indexing.")

    if store.count() == 0:
        store.add_documents(records)

    # Step 4: Seed demo users
    print("\n👤 Step 4: Seeding demo user accounts…")
    seed_demo_users()

    print("\n" + "=" * 55)
    print("  ✅ Ingestion complete! You can now start the app.")
    print("=" * 55)
    print("\nNext steps:")
    print("  Terminal 1:  python -m backend.main")
    print("  Terminal 2:  streamlit run frontend/app.py")


if __name__ == "__main__":
    main()
