"""
preprocessor.py
───────────────
Handles:
  • Text cleaning (markdown + CSV)
  • Word-level chunking (300-token windows)
  • Role-based metadata tagging
  • Walking the Fintech-data folder recursively
"""

import os
import re
import pandas as pd
import nltk

from src.config import DATA_FOLDER, CHUNK_SIZE, ROLE_MAPPING

# Download NLTK data once
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
from nltk.tokenize import word_tokenize


# ────────────────────────────────────────────────────────────────
# Text helpers
# ────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Normalise whitespace, strip special chars, lowercase optional."""
    text = re.sub(r"[^\x00-\x7F]+", " ", text)   # non-ASCII
    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = word_tokenize(text)
    chunks = []
    stride = max(1, chunk_size - 50)          # 50-token overlap
    for i in range(0, len(words), stride):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


# ────────────────────────────────────────────────────────────────
# Metadata
# ────────────────────────────────────────────────────────────────

def get_roles_for_file(filepath: str) -> str:
    """
    Returns comma-separated roles that can access this file.
    ChromaDB metadata does NOT support lists → use a string.
    """
    filepath_lower = filepath.lower().replace("\\", "/")
    file_name = os.path.basename(filepath_lower)
    roles = []
    
    for role, resources in ROLE_MAPPING.items():
        if role == "c_level": 
            continue
            
        # 1. Path-based matching (e.g., if in /hr/ folder)
        if f"/{role}/" in filepath_lower:
            roles.append(role)
            
        # 2. Name-based matching (if filename is explicitly mapped to a role)
        if isinstance(resources, list) and file_name in resources:
            if role not in roles:
                roles.append(role)

    # Also check if it's in a 'general' folder or marked as employee-wide
    if "/general/" in filepath_lower or file_name in ROLE_MAPPING.get("employees", []):
        if "employees" not in roles:
            roles.append("employees")

    if not roles:
        roles = ["c_level"]

    return ",".join(list(set(roles)))


def build_metadata(filepath: str, file_name: str, chunk: str) -> dict:
    return {
        "source":     file_name,
        "roles":      get_roles_for_file(filepath),   # string, not list
        "chunk_text": chunk[:200],                      # preview only
    }


# ────────────────────────────────────────────────────────────────
# File parsers
# ────────────────────────────────────────────────────────────────

def parse_markdown(filepath: str) -> list[dict]:
    """Return list of {text, metadata} dicts from a .md file."""
    file_name = os.path.basename(filepath)
    records   = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        cleaned = clean_text(raw)
        for chunk in chunk_text(cleaned):
            records.append({
                "text":     chunk,
                "metadata": build_metadata(filepath, file_name, chunk),
            })
    except Exception as e:
        print(f"  [WARN] Skipping {filepath}: {e}")
    return records


def parse_csv(filepath: str) -> list[dict]:
    """Return list of {text, metadata} dicts from a .csv file."""
    file_name = os.path.basename(filepath)
    records   = []
    try:
        df = pd.read_csv(filepath, encoding="utf-8", on_bad_lines="skip")
        for col in df.select_dtypes(include="object").columns:
            text = " ".join(df[col].dropna().astype(str).tolist())
            cleaned = clean_text(text)
            for chunk in chunk_text(cleaned):
                records.append({
                    "text":     chunk,
                    "metadata": build_metadata(filepath, file_name, chunk),
                })
    except Exception as e:
        print(f"  [WARN] Skipping {filepath}: {e}")
    return records


# ────────────────────────────────────────────────────────────────
# Main entry point
# ────────────────────────────────────────────────────────────────

def load_all_documents(data_folder: str = DATA_FOLDER) -> list[dict]:
    """
    Walk the data folder recursively and parse all .md and .csv files.
    Returns a flat list of {text, metadata} records.
    """
    all_records: list[dict] = []

    if not os.path.exists(data_folder):
        raise FileNotFoundError(
            f"Data folder '{data_folder}' not found.\n"
            "Run: git clone https://github.com/springboardmentor441p-coderr/Fintech-data"
        )

    for root, _dirs, files in os.walk(data_folder):
        for fname in files:
            fpath = os.path.join(root, fname)
            if fname.endswith(".md"):
                print(f"  Parsing MD : {fpath}")
                all_records.extend(parse_markdown(fpath))
            elif fname.endswith(".csv"):
                print(f"  Parsing CSV: {fpath}")
                all_records.extend(parse_csv(fpath))

    print(f"\n✅ Total chunks loaded: {len(all_records)}")
    return all_records


if __name__ == "__main__":
    docs = load_all_documents()
    if docs:
        print("\nSample record:")
        print("  text    :", docs[0]["text"][:100])
        print("  metadata:", docs[0]["metadata"])
