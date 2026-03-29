from typing import Dict, List
from datetime import datetime

# ── ROLE HIERARCHY ────────────────────────────────────────
ROLE_HIERARCHY = {
    "C-Level":     5,
    "Finance":     4,
    "HR":          4,
    "Marketing":   4,
    "Engineering": 4,
    "Employee":    1,
}

# ── DEPARTMENT → ALLOWED ROLES ────────────────────────────
DEPARTMENT_ACCESS = {
    "finance":     ["Finance", "C-Level"],
    "hr":          ["HR", "C-Level"],
    "marketing":   ["Marketing", "C-Level"],
    "engineering": ["Engineering", "C-Level"],
    "general":     ["Employee", "HR", "C-Level"],  # Employee handbook — all employees can read
    "uploads":     ["C-Level"],                    # Admin-uploaded docs — C-Level only
}


def create_metadata(chunk_id: str, chunk_text: str,
                    department: str, source_document: str) -> Dict:
    department = department.lower()
    if department not in DEPARTMENT_ACCESS:
        department = "general"   # unknown departments fall back to general

    return {
        "chunk_id":       chunk_id,
        "department":     department,
        "source":         source_document,
        "allowed_roles":  DEPARTMENT_ACCESS[department],
        "created_at":     datetime.utcnow().isoformat(),
        "token_estimate": len(chunk_text.split()),
    }


def is_role_authorized(user_role: str, allowed_roles: List[str]) -> bool:
    if user_role == "C-Level":
        return True
    return user_role in allowed_roles
