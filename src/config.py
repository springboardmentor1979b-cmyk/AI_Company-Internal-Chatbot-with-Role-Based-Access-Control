import os
from dotenv import load_dotenv

load_dotenv()

# ── JWT ──────────────────────────────────────────────
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM  = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", 8))

# ── Paths ─────────────────────────────────────────────
DATA_FOLDER    = os.getenv("DATA_FOLDER", "Fintech-data")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./users.db")

# ── Embedding model ───────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE      = 300          # tokens per chunk
COLLECTION_NAME = "company_docs"

# ── HuggingFace ───────────────────────────────────────
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
HF_MODEL     = "google/flan-t5-large"   # free & small enough
HF_API_URL   = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# ── Role → document mapping ───────────────────────────
# Keys must match actual filenames in the repo (lowercase)
ROLE_MAPPING: dict[str, list[str] | str] = {
    "finance":     ["finance_report.md", "quarterly_summary.csv",
                    "budget_plan.md", "financial_summary.csv"],
    "marketing":   ["marketing_analysis.md", "campaign_data.csv",
                    "marketing_report.md"],
    "hr":          ["employee_data.csv", "hr_policies.md",
                    "hr_data.csv", "hr_report.md"],
    "engineering": ["tech_docs.md", "system_architecture.md",
                    "engineering_report.md"],
    "employees":   ["general_handbook.md", "company_policies.md"],
    "c_level":     "all",     # special sentinel — sees everything
}

ROLES = list(ROLE_MAPPING.keys())
