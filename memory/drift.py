# memory/drift.py — REPLACE ENTIRE FILE WITH THIS

from memory.recall import get_interest_memory
from backend.llm import call_llm_structured


def detect_interest_drift_from_memory(student_id: str) -> dict:
    """
    Reads Hindsight memory and detects
    if student interests are shifting over time.
    """
    memory = get_interest_memory(student_id)

    prompt = f"""
Analyze this student's activity memory to detect interest drift.

Memory (ordered oldest to newest):
{memory}

Return ONLY a JSON object:
{{
  "emerging": [],
  "fading": [],
  "stable": [],
  "drift_detected": false
}}

Rules:
- emerging: categories appearing MORE in recent memory
- fading: categories appearing LESS in recent memory
- stable: categories consistently present throughout
- drift_detected: true if any clear shift exists
- categories from: tech, arts, sports, cultural, entrepreneurship
- If memory too short return all empty and drift_detected: false
Return ONLY the JSON. No explanation.
"""

    try:
        import json
        raw = call_llm_structured(prompt)
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {
            "emerging": [],
            "fading": [],
            "stable": [],
            "drift_detected": False
        }


# Keep Bikash's math functions for compatibility
def calculate_interest_score(
    current_score: float,
    days_since_last: int,
    interacted: bool
) -> float:
    decay = 0.95 ** days_since_last
    boost = 0.2 if interacted else 0
    new_score = (current_score * decay) + boost
    return round(min(new_score, 1.0), 3)


def update_all_interests(
    interest_scores: dict,
    last_seen: dict,
    today
) -> dict:
    updated = {}
    for category, score in interest_scores.items():
        last = last_seen.get(category, today)
        days_gap = (today - last).days
        updated[category] = calculate_interest_score(score, days_gap, False)
    return updated
