import os
import json
import hashlib
import logging
from uuid import uuid4
from typing import List, Dict
from datetime import datetime

from preprocessing.parser import parse_markdown, parse_csv
from preprocessing.chunker import clean_text, chunk_text
from preprocessing.metadata import create_metadata


# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "..", "data")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "vector_db", "processed_chunks.json")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ---------------------------------------
# UTILITY: HASH FOR DUPLICATE PREVENTION
# ---------------------------------------

def generate_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------
# MAIN PROCESSOR
# ---------------------------------------

def process_documents() -> List[Dict]:

    if not os.path.exists(DATA_FOLDER):
        raise FileNotFoundError("Data folder does not exist.")

    all_chunks = []
    seen_hashes = set()

    logging.info("Starting document ingestion process...")

    for department in os.listdir(DATA_FOLDER):

        department_path = os.path.join(DATA_FOLDER, department)

        if not os.path.isdir(department_path):
            continue

        logging.info(f"Processing department: {department}")

        for filename in os.listdir(department_path):

            file_path = os.path.join(department_path, filename)

            try:
                # --------------------------
                # FILE TYPE HANDLING
                # --------------------------
                if filename.endswith(".md"):
                    raw_text = parse_markdown(file_path)

                elif filename.endswith(".csv"):
                    raw_text = parse_csv(file_path)

                else:
                    logging.warning(f"Unsupported file type skipped: {filename}")
                    continue

                # --------------------------
                # CLEANING
                # --------------------------
                cleaned_text = clean_text(raw_text)

                if not cleaned_text:
                    logging.warning(f"Empty content after cleaning: {filename}")
                    continue

                # --------------------------
                # CHUNKING
                # --------------------------
                chunks = chunk_text(cleaned_text)

                logging.info(f"{len(chunks)} chunks created from {filename}")

                # --------------------------
                # PROCESS EACH CHUNK
                # --------------------------
                for chunk in chunks:

                    content_hash = generate_content_hash(chunk)

                    if content_hash in seen_hashes:
                        continue  # Skip duplicate chunks

                    seen_hashes.add(content_hash)

                    chunk_id = str(uuid4())

                    metadata = create_metadata(
                        chunk_id=chunk_id,
                        chunk_text=chunk,
                        department=department,
                        source_document=filename
                    )

                    document_entry = {
                        "id": chunk_id,
                        "text": chunk,
                        "metadata": metadata,
                        "content_hash": content_hash,
                        "ingested_at": datetime.utcnow().isoformat()
                    }

                    all_chunks.append(document_entry)

            except Exception as e:
                logging.error(f"Error processing file {filename}: {str(e)}")

    logging.info(f"Total unique chunks processed: {len(all_chunks)}")

    return all_chunks


# ---------------------------------------
# EXPORT FUNCTION
# ---------------------------------------

def export_to_json(data: List[Dict]):

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    logging.info(f"Processed data exported to {OUTPUT_FILE}")


# ---------------------------------------
# EXECUTION ENTRY POINT
# ---------------------------------------

if __name__ == "__main__":

    processed_data = process_documents()

    if processed_data:
        export_to_json(processed_data)
    else:
        logging.warning("No data processed.")
