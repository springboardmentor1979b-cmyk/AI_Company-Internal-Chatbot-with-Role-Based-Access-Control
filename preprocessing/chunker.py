import re
from typing import List


# ---------------------------
# TEXT CLEANING
# ---------------------------

def clean_text(text: str) -> str:
    """
    Advanced text normalization for embedding pipeline.
    Preserves financial and technical formatting.
    """

    if not text or not isinstance(text, str):
        return ""

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove unwanted control characters
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)

    # Preserve currency, %, decimals, commas
    text = re.sub(r"[^\w\s.,:%$₹€£\-()/]", "", text)

    return text.strip()


# ---------------------------
# TOKEN ESTIMATION
# ---------------------------

def estimate_tokens(text: str) -> int:
    """
    Rough token estimation.
    (1 token ≈ 0.75 words average in English)
    """
    words = len(text.split())
    return int(words / 0.75)


# ---------------------------
# SENTENCE-AWARE CHUNKING
# ---------------------------

def chunk_text(
    text: str,
    max_tokens: int = 450,
    overlap_tokens: int = 75
) -> List[str]:
    """
    Advanced sentence-aware chunking.

    - Avoids breaking sentences.
    - Uses token estimation.
    - Maintains overlap for context continuity.
    """

    if not text:
        return []

    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []
    current_chunk = []
    current_token_count = 0

    for sentence in sentences:
        sentence_tokens = estimate_tokens(sentence)

        # If adding sentence exceeds max_tokens
        if current_token_count + sentence_tokens > max_tokens:
            chunk_text_combined = " ".join(current_chunk).strip()
            if chunk_text_combined:
                chunks.append(chunk_text_combined)

            # Create overlap
            overlap_words = chunk_text_combined.split()[-overlap_tokens:]
            current_chunk = [" ".join(overlap_words)]
            current_token_count = estimate_tokens(current_chunk[0])

        current_chunk.append(sentence)
        current_token_count += sentence_tokens

    # Add final chunk
    final_chunk = " ".join(current_chunk).strip()
    if final_chunk:
        chunks.append(final_chunk)

    return chunks
