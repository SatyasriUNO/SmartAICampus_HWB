# memory/recall.py

import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()


# ─────────────────────────────────────────────
# Hindsight client — single instance
# ─────────────────────────────────────────────

def _get_client():
    return Hindsight(
        base_url=os.getenv("HINDSIGHT_BASE_URL"),
        api_key=os.getenv("HINDSIGHT_API_KEY")
    )


# ─────────────────────────────────────────────
# CORE RECALL
# ─────────────────────────────────────────────

def recall(student_id: str, query: str, top_k: int = 10) -> list[dict]:
    try:
        client = _get_client()
        results = client.recall(bank_id=student_id, query=query)
        return results if results else []
    except Exception as e:
        print(f"  [recall] ❌ Failed for {student_id}: {e}")
        return []


def recall_as_string(student_id: str, query: str, top_k: int = 10) -> str:
    results = recall(student_id, query, top_k)
    if not results:
        return "No memory found for this student yet."
    return "\n".join(
        f"- {r.get('text', r) if isinstance(r, dict) else r}"
        for r in results[:top_k]
    )


# ─────────────────────────────────────────────
# SHORTHAND HELPERS — used by filters, recommender,
# reminders, social to AVOID importing from agent.py
# (prevents circular imports)
# ─────────────────────────────────────────────

def _recall(student_id: str, query: str) -> str:
    """
    Drop-in replacement for agent._recall.
    Import THIS instead of backend.agent._recall
    to avoid circular imports.
    """
    return recall_as_string(student_id, query)


# ─────────────────────────────────────────────
# TYPED RECALL CALLS
# ─────────────────────────────────────────────

def get_interest_memory(student_id: str) -> str:
    return recall_as_string(
        student_id,
        "student interests clubs events attended activities categories"
    )


def get_avoidance_memory(student_id: str) -> str:
    return recall_as_string(
        student_id,
        "events ignored skipped avoided morning sports disliked"
    )


def get_deadline_memory(student_id: str) -> str:
    return recall_as_string(
        student_id,
        "deadline completed missed late submission academic"
    )


def get_social_memory(student_id: str) -> str:
    return recall_as_string(
        student_id,
        "club joined dropped members peers social group"
    )


def get_full_context(student_id: str) -> str:
    interest = get_interest_memory(student_id)
    avoidance = get_avoidance_memory(student_id)
    deadline = get_deadline_memory(student_id)
    return f"""
--- INTEREST & ACTIVITY MEMORY ---
{interest}

--- AVOIDANCE PATTERNS ---
{avoidance}

--- DEADLINE BEHAVIOR ---
{deadline}
"""


def get_recent_interactions(student_id: str) -> str:
    return recall_as_string(
        student_id,
        "student said asked queried agent responded"
    )


def check_memory_exists(student_id: str) -> bool:
    results = recall(student_id, "student", top_k=1)
    return len(results) > 0
